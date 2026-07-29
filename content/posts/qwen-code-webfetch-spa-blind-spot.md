+++
title = "Qwen Code WebFetch 的 SPA 盲区：html-to-text 空内容问题"
date = 2026-07-29T00:00:00+08:00
slug = "qwen-code-webfetch-spa-blind-spot"
[taxonomies]
    tags = ["Qwen Code", "WebFetch", "SPA", "Bug", "Coding Assistant"]
+++

使用 Qwen Code 的 `web_fetch` 工具抓取 SPA（单页应用）页面时，经常会返回空内容。这不是网络问题，而是一个设计 gap：`html-to-text` 对空 body 页面返回空字符串，但 Qwen Code 没有任何 fallback 机制。

## 问题

SPA 页面的 body 通常只有一个挂载点：

```html
<body>
  <div id="root"></div>
  <script src="app.js"></script>
</body>
```

`html-to-text` 解析这段 HTML 后返回空字符串。但 curl 能拿到 `<title>` 和 `<meta description>`——这些信息在 `<head>` 里，不是 body 的一部分。

## 复现

```
URL: https://www.stepfun.com
web_fetch 返回: （空）
curl 返回: <title>阶跃星辰</title> + <meta description="...">
```

## 解决方案

### 推荐：用 `tavily-extract` 替代

如果你已配置 Tavily MCP（参考 [Qwen Code 接入 Tavily 搜索](/posts/qwen-code-tavily-mcp-setup/)），直接使用 `tavily-extract` 工具替代 `web_fetch`。Tavily 在服务端渲染 JavaScript，能正确处理 SPA 页面。

### 备选：禁用 `web_fetch`，配置其他 MCP fetch 工具

在 `settings.json` 中禁用内置 `web_fetch`：

```json
{
  "tools": {
    "disabled": ["web_fetch"]
  }
}
```

MCP fetch 工具有多种类型：

- **无头浏览器类**：用 Playwright/Puppeteer 渲染页面，能处理 SPA
- **API 类**：如 Tavily Extract，服务端渲染后返回结构化内容
- **命令行类**：封装 curl/wget 等工具，简单直接但不渲染 JS

## 源码事实

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

没有 fallback 逻辑。`html-to-text` 返回空 → 直接送空字符串给 LLM → LLM 拿到空内容 → 返回空或胡编。

## 与 Claude Code 的对比

Claude Code 的 WebFetch 同样没有 SPA fallback。两者在 SPA 场景下都有盲区。

## 给贡献者的修复思路

如果你有兴趣修复这个问题，以下是几个方向（按成本从低到高）：

1. **`<head>` fallback**：`html-to-text` 返回空时，提取 `<title>` + `<meta description>` 作为兜底。改动最小，只需在 `convert()` 返回空时加一个 fallback 分支。
2. **SPA 检测**：识别 `<div id="root">` 等特征，提示用户该页面需要 JS 渲染，建议使用 MCP 工具。
3. **无头浏览器集成**：对检测到的 SPA 页面，用无头浏览器渲染后再提取内容。效果最好但引入重依赖。
