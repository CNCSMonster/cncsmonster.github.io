+++
title = "Qwen Code WebFetch's SPA Blind Spot: The html-to-text Empty Content Problem"
date = 2026-07-29T00:00:00+08:00
slug = "qwen-code-webfetch-spa-blind-spot-en"
[taxonomies]
    tags = ["Qwen Code", "WebFetch", "SPA", "Bug", "Coding Assistant"]
+++

When using Qwen Code's `web_fetch` tool to scrape SPA (Single Page Application) pages, it frequently returns empty content. This isn't a network issue — it's a design gap: `html-to-text` returns an empty string for pages with empty bodies, and Qwen Code has no fallback mechanism.

## The Problem

SPA pages typically have only a mount point in their body:

```html
<body>
  <div id="root"></div>
  <script src="app.js"></script>
</body>
```

`html-to-text` parses this HTML and returns an empty string. But `curl` can retrieve the `<title>` and `<meta description>` — this information lives in `<head>`, not in the body.

## Reproduction

```
URL: https://www.stepfun.com
web_fetch returns: (empty)
curl returns: <title>StepFun</title> + <meta description="...">
```

## Solutions

### Recommended: Use `tavily-extract` Instead

If you already have Tavily MCP configured (see [Getting Qwen Code to Work with Tavily Search](/posts/qwen-code-tavily-mcp-setup/)), use the `tavily-extract` tool instead of `web_fetch`. Tavily renders JavaScript server-side and handles SPA pages correctly.

### Alternative: Disable `web_fetch` and Use Other MCP Fetch Tools

Disable the built-in `web_fetch` in `settings.json`:

```json
{
  "tools": {
    "disabled": ["web_fetch"]
  }
}
```

MCP fetch tools come in several types:

- **Headless browser-based**: Render pages with Playwright/Puppeteer, handles SPA
- **API-based**: Like Tavily Extract, server-side rendering returns structured content
- **CLI-based**: Wrappers around curl/wget, simple but no JS rendering

## Source Code Facts

```typescript
// packages/core/src/tools/web-fetch.ts (v0.20.1-preview.7215)
const textContent = convert(html, {
  wordwrap: false,
  selectors: [
    { selector: 'a', options: { ignoreHref: true } },
    { selector: 'img', format: 'skip' },
  ],
}).substring(0, MAX_CONTENT_LENGTH);
```

No fallback logic. `html-to-text` returns empty → empty string sent directly to the LLM → LLM receives empty content → returns empty or hallucinated output.

## Comparison with Claude Code

Claude Code's WebFetch similarly lacks SPA fallback. Both tools have blind spots in SPA scenarios.

## For Contributors: Fix Directions

If you're interested in fixing this, here are several approaches (ordered by cost, lowest first):

1. **`<head>` fallback**: When `html-to-text` returns empty, extract `<title>` + `<meta description>` as a fallback. Minimal change — just add a fallback branch when `convert()` returns empty.
2. **SPA detection**: Identify SPA characteristics like `<div id="root">` and alert the user that the page requires JS rendering, suggesting MCP tools instead.
3. **Headless browser integration**: For detected SPA pages, render with a headless browser before extracting content. Best results but heaviest dependencies.
