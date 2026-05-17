+++
title = "Enhancing AI Code CLI Capabilities Should Use MCP Protocol, Not Built-in Tool Source Code"
date = 2026-05-05T00:00:00+08:00
slug = "ai-code-cli-mcp-protocol-not-internal-tools"
tags = ["AI Code CLI", "MCP", "Qwen Code", "Lessons Learned"]
+++

**Don't build on code that's about to be deleted.**

## What Happened

The older version of Qwen Code had a built-in `web_search` tool supporting three search backends: Tavily, Google, and DashScope (DashScope was eligible for Qwen OAuth authentication). But its provider selection was static — you'd configure a single default, the tool would call that one provider per search, and failures were just errors. No fallback.

My goal was to add runtime provider fallback inside the tool: try Tavily first, then Google, then DashScope. If the first one fails, automatically move to the next. That way a single backend going down wouldn't kill search entirely.

On 2026-04-24, while my solution was still local — Qwen Code PR #3502 landed. **It deleted the entire `web_search` built-in tool** and replaced it with an MCP-based architecture. All the old config keys (`webSearch` block, `advanced.tavilyApiKey`, `--tavily-api-key` CLI flag, etc.) were deprecated. I had been working against a target that no longer existed.

## Why This Approach Was Doomed

The problem wasn't the idea — the old implementation genuinely lacked runtime fallback, and adding it was a reasonable improvement. The problem was the foundation:

- `web_search` went from existence to deletion in a single PR. The AI Code CLI category is less than two years old. Built-in tools can be refactored, merged, or deleted at any time.
- MCP is a cross-CLI standard. Qwen Code, Claude Code, Gemini CLI all support it. Tools built on MCP are independent of any CLI implementation — there's no risk of "I spent weeks modifying source code, and then the tool got deleted."

## Reflection: The Right Approach

Fallback itself was a good idea — the old version needed it, and the MCP layer needs it too. The mistake was **where** I chose to implement it:

- ❌ Modifying CLI built-in tool source code to add fallback
- ✅ Writing a standalone MCP server that internally handles multi-provider fallback

Same functionality. Placed in built-in tool source, it's one PR away from deletion. Placed in an MCP server, it's decoupled from the CLI version lifecycle — you control when it lives or dies.

## Takeaways

- When building capability enhancements for AI Code CLIs, **prioritize the MCP layer** — tools live independently of CLI implementation, immune to upstream refactoring.
- Before you start, check the module's lifecycle: is it stable core functionality, or experimental code that could be replaced at any time?
