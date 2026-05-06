+++
title = "Qwen Code 配置 Tavily MCP 搜索的最佳方式"
date = 2026-05-05T00:00:00+08:00
slug = "qwen-code-tavily-mcp-setup"
tags = ["Qwen Code", "MCP", "Tavily", "配置"]
+++

Qwen Code 自 2026-04-24（PR #3502）起移除了内置 `web_search`，搜索能力全部通过 MCP 接入。官方文档列出三种方式，本文分析哪种最值得用。

## 三种配置方式

### Remote MCP（远程 HTTP）

```jsonc
{
  "mcpServers": {
    "tavily": {
      "httpUrl": "https://mcp.tavily.com/mcp/?tavilyApiKey=${TAVILY_API_KEY}"
    }
  }
}
```

### Local NPX（官方 npm 包）

```jsonc
{
  "mcpServers": {
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@latest"],
      "env": {
        "TAVILY_API_KEY": "$TAVILY_API_KEY"
      }
    }
  }
}
```

`tavily-mcp` 是 Tavily 团队（dustin@tavily.com）官方维护的 npm 包，2026-01~04 已发 5 个版本，当前最新 0.2.19。

## 对比

| 维度 | Remote MCP | Local NPX |
|------|-----------|-----------|
| **API Key 安全** | ❌ 明文在 URL 中 | ✅ 通过环境变量注入 |
| **依赖性** | 需 Tavily 服务器在线 | 需 Node.js/npx |
| **版本控制** | 不可控 | 可锁版本 |
| **维护方** | Tavily 基础设施 | Tavily npm 包 |

## 推荐：Local NPX

原因是三个维度上的优势：

1. **安全**：API Key 不出现在配置文件中，通过 `$TAVILY_API_KEY` 环境变量注入，不会不小心提交到 Git
2. **长期支持**：Tavily 团队自己维护 npm 包，更新活跃，`@latest` 自动跟进
3. **简单**：一行 `npx -y tavily-mcp@latest`，对已有 Node.js 环境零额外配置

## 笔者的配置

```jsonc
// ~/.qwen/settings.json
"mcpServers": {
  "tavily": {
    "command": "npx",
    "args": ["-y", "tavily-mcp@latest"],
    "timeout": 30000
  }
}
```

未显式写 `env`，API Key 由 Qwen Code 进程环境变量继承。建议补上 `"TAVILY_API_KEY": "$TAVILY_API_KEY"` 让配置自说明。
