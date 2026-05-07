+++
title = "Claude Code WebFetch 修复：跳过 preflight 解决站点抓取失败"
date = 2026-05-07T00:00:00+08:00
slug = "claude-code-fix-webfetch-preflight"
tags = ["Claude Code", "WebFetch", "踩坑记录"]
+++

## 背景

使用三方 LLM provider（智谱等 Anthropic 兼容 API）时，Claude Code 的原生网络工具存在问题：WebSearch 不可用，WebFetch 看似被国内站点拒绝。经过 Claude Code 源码分析和实测验证，找到了根因和修复方案。

## 源码事实（Claude Code 2.x）

> 源码位置：`claude-code-haha/src/tools/`

### WebFetch 架构

```
调用链：
  ① preflight 域名安全检查 → POST https://api.anthropic.com/api/web/domain_info
     硬编码，不受 ANTHROPIC_BASE_URL 控制
  ② 本地 HTTP 抓取 → axios.get(url)，从用户机器直接发出
  ③ 内容摘要 → ANTHROPIC_BASE_URL (Haiku)，走用户的 provider
```

关键文件：
- `WebFetchTool/WebFetchTool.ts` — 工具定义和权限检查
- `WebFetchTool/utils.ts` — `getWithPermittedRedirects()` 通过 `axios.get()` 本地抓取（262行）
- `WebFetchTool/utils.ts` — `checkDomainBlocklist()` preflight 检查（176行）

### WebSearch 架构

```
调用链：
  构造 server_tool_use schema (type: web_search_20250305)
  → 注入到 Messages API 请求中
  → Anthropic 服务端执行搜索
  → 客户端消费流式返回的 web_search_tool_result
  全程服务端执行，客户端不发起搜索 HTTP 请求
```

关键文件：
- `WebSearchTool/WebSearchTool.ts` — `isEnabled()` 只允许 firstParty/vertex/foundry（168行）
- `WebSearchTool/prompt.ts` — 明确说明 "Searches are performed automatically within a single API call"

### ANTHROPIC_BASE_URL 的作用范围

| 受影响 | 不受影响 |
|---|---|
| Chat Completions API | WebFetch preflight（硬编码 api.anthropic.com） |
| WebFetch 内容摘要（Haiku） | WebFetch 本地抓取（axios.get） |
| | WebSearch 不可用（三方 provider 不实现） |

## 修复方案

### 一条配置解决 WebFetch

```json
// .claude/settings.local.json
{
  "skipWebFetchPreflight": true
}
```

**原理**：跳过 `checkDomainBlocklist()` 的 API 调用。本地 `axios.get()` 直接抓取，不经过 Anthropic 安全检查。

### 实测验证

| 测试目标 | skipWebFetchPreflight=false | skipWebFetchPreflight=true |
|---|---|---|
| deepseek.com | ❌ Unable to verify... | ✅ DeepSeek \| 深度求索 |
| docs.bigmodel.cn | ❌ Unable to verify... | ✅ (验证通过) |

### WebSearch 无解

三方 provider 不实现 Anthropic 的 server_tool 协议。`isEnabled()` 直接返回 false，工具不注册。**不是配置问题，是 provider 能力限制**。

### MCP 搜索作为补充

WebFetch 修复后已是主要抓取工具。以下 MCP 工具提供搜索能力（搜索引擎 vs 单页抓取是不同能力）：

| 工具 | 定位 | 免费额度 |
|---|---|---|
| Tavily MCP | 技术文档搜索最优 | 1000次/月 |
| Brave Search MCP | 通用搜索 + 独立索引 | 2000次/月 |

## 最终配置

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

## 网络工具能力矩阵（修复后）

| 工具 | 状态 | 原理 |
|---|---|---|
| WebFetch | ✅ 已修复 | 本地 axios.get()，跳过 Anthropic preflight |
| WebSearch | ❌ deny | 三方 provider 不实现 server_tool |
| Brave MCP | 已装 | 本地进程，需 API Key |
| Tavily MCP | 已装 | 本地进程，需 API Key |
| curl | ✅ 兜底 | 无依赖 |

## 优先级策略

```
查特定网页内容     → WebFetch（已修复，无额度限制）
查技术文档/API     → Tavily MCP（搜索质量最优）
通用搜索          → Brave Search MCP（独立索引）
已知文档站快速获取  → llms.txt + curl（零 token 消耗）
```

## 关键教训

1. **报错信息具有误导性**：`"unable to verify domain is safe"` 看起来像目标站拒绝，实则是 Anthropic preflight 在不通知的情况下拦截
2. **源码验证优于推测**：最初推测 WebFetch 从 Anthropic 服务器抓取，源码证明是本地 axios
3. **一行配置解决大问题**：整个探索过程中最有效的措施是 `skipWebFetchPreflight: true`，之前折腾 MCP 是因为不知道这个配置存在
