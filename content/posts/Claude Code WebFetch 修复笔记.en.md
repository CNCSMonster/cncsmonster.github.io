+++
title = "Fixing Claude Code WebFetch: Bypassing preflight to Rescue Failed Site Fetching"
date = 2026-05-07T00:00:00+08:00
slug = "claude-code-fix-webfetch-preflight"
tags = ["Claude Code", "WebFetch", "Troubleshooting"]
+++

## Background

When using third-party LLM providers (e.g. Zhipu, or other Anthropic-compatible APIs), Claude Code's built-in network tools have problems: WebSearch is unavailable, and WebFetch appears to be blocked by Chinese websites. By analyzing Claude Code's source code and running real tests, I found the root cause and a fix.

## Source Code Facts (Claude Code 2.x)

> Source location: `claude-code-haha/src/tools/`

### WebFetch Architecture

```
Call chain:
  ① preflight domain safety check → POST https://api.anthropic.com/api/web/domain_info
     Hardcoded — not controlled by ANTHROPIC_BASE_URL
  ② Local HTTP fetch → axios.get(url), outgoing from the user's machine
  ③ Content summarization → ANTHROPIC_BASE_URL (Haiku), routed through user's provider
```

Key files:
- `WebFetchTool/WebFetchTool.ts` — tool definition and permission checks
- `WebFetchTool/utils.ts` — `getWithPermittedRedirects()` performs local fetching via `axios.get()` (line 262)
- `WebFetchTool/utils.ts` — `checkDomainBlocklist()` preflight check (line 176)

### WebSearch Architecture

```
Call chain:
  Construct server_tool_use schema (type: web_search_20250305)
  → Inject into Messages API request
  → Anthropic server performs the search
  → Client consumes streamed web_search_tool_result
  Entirely server-side; client never initiates HTTP search requests
```

Key files:
- `WebSearchTool/WebSearchTool.ts` — `isEnabled()` only allows firstParty/vertex/foundry (line 168)
- `WebSearchTool/prompt.ts` — explicitly states "Searches are performed automatically within a single API call"

### ANTHROPIC_BASE_URL Scope

| Affected | Not Affected |
|----------|-------------|
| Chat Completions API | WebFetch preflight (hardcoded to api.anthropic.com) |
| WebFetch content summarization (Haiku) | WebFetch local fetch (axios.get) |
| | WebSearch unavailable (third-party providers don't implement it) |

## The Fix

### One Config Line to Fix WebFetch

```json
// .claude/settings.local.json
{
  "skipWebFetchPreflight": true
}
```

**How it works**: skips the `checkDomainBlocklist()` API call. Local `axios.get()` fetches directly without passing through Anthropic's safety check.

### Verified Results

| Target | skipWebFetchPreflight=false | skipWebFetchPreflight=true |
|--------|----------------------------|---------------------------|
| deepseek.com | ❌ Unable to verify... | ✅ DeepSeek \| 深度求索 |
| docs.bigmodel.cn | ❌ Unable to verify... | ✅ (verified) |

### WebSearch: No Fix Available

Third-party providers don't implement Anthropic's server_tool protocol. `isEnabled()` returns false directly — the tool isn't registered. **Not a config issue — a provider capability limitation.**

### MCP Search as a Supplement

After the WebFetch fix, it's already the primary fetching tool. The following MCP tools provide search capabilities (search engine vs. single-page fetch are different capabilities):

| Tool | Use Case | Free Tier |
|------|----------|-----------|
| Tavily MCP | Best for technical documentation search | 1000 queries/month |
| Brave Search MCP | General-purpose search + independent index | 2000 queries/month |

## Final Configuration

```json
{
  "skipWebFetchPreflight": true,
  "permissions": {
    "allow": [
      "WebFetch",
      "Bash(curl:*)",
      "Bash(claude mcp *)",
      "Bash(python3 *)"
    ],
    "deny": ["WebSearch"]
  }
}
```

## Network Tool Capability Matrix (After Fix)

| Tool | Status | How It Works |
|------|--------|-------------|
| WebFetch | ✅ Fixed | Local axios.get(), bypasses Anthropic preflight |
| WebSearch | ❌ deny | Third-party providers don't implement server_tool |
| Brave MCP | Installed | Local process, requires API Key |
| Tavily MCP | Installed | Local process, requires API Key |
| curl | ✅ Fallback | Zero dependencies |

## Priority Strategy

```
Fetch specific webpage content  → WebFetch (fixed, unlimited)
Search docs/API references      → Tavily MCP (best search quality)
General web search              → Brave Search MCP (independent index)
Quick fetch from known doc sites → llms.txt + curl (zero token cost)
```

## Key Lessons

1. **Error messages can be misleading**: `"unable to verify domain is safe"` looked like the target site was blocking the request. In reality, the Anthropic preflight was silently intercepting it.
2. **Source code beats speculation**: I initially assumed WebFetch fetched from Anthropic's servers. The source code proved it's a local `axios` call.
3. **One config line can solve a huge problem**: The single most effective move in this entire investigation was `skipWebFetchPreflight: true`. All the earlier MCP tinkering was because I didn't know this setting existed.
