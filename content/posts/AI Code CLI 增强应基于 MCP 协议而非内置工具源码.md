+++
title = "AI Code CLI 能力增强应基于 MCP 协议，而非内置工具源码"
date = 2026-05-05T00:00:00+08:00
tags = ["AI Code CLI", "MCP", "Qwen Code", "经验教训"]
+++

**不要在会被删除的代码上盖房子。**

## 具体经历

Qwen Code 旧版内置了 `web_search` 工具，支持 Tavily、Google、DashScope 三个搜索后端（DashScope 可走 Qwen OAuth 认证）。但它的 provider 选择是静态的——用户在配置中指定一个 default，工具一次搜索只调一个 provider，失败就直接报错，不会尝试下一个。

笔者的目标是在工具内部实现运行时 provider fallback：按 Tavily → Google → DashScope 的顺序依次尝试，前一个失败自动切换到下一个，避免单后端不可用时搜索能力彻底瘫痪。

2026-04-24，方案还在本地，Qwen Code PR #3502 合并——**把整个 `web_search` 内置工具删了**，替换成 MCP 架构。旧版的所有配置键（`webSearch` 块、`advanced.tavilyApiKey`、`--tavily-api-key` 等 CLI 参数）全部作废。笔者针对的是一个已经不存在的目标。

## 为什么这个方向站不住脚

不是方案本身有问题——旧版确实缺少运行时 fallback，这是一个合理的改进方向。问题是地基：

- `web_search` 从存在到消失只隔了一个 PR。AI Code CLI 品类发展不到两年，内置工具随时可能被重构、合并或删除。
- MCP 是跨 CLI 的通用协议，Qwen Code、Claude Code、Gemini CLI 都支持。工具本身独立于任何 CLI 的实现——不存在"改了半天源码，工具一删全白干"的风险。

## 反思：正确的做法

fallback 本身的方向没问题——旧版确实需要，MCP 层也同样需要。错的是实现位置：

- ❌ 修改 CLI 内置工具的源码来实现 fallback
- ✅ 写一个独立的 MCP server，内部封装多 provider fallback 逻辑

同样的功能，放在内部工具源码里随时可能被删；放在 MCP server 里，和 CLI 版本解耦，自己控制生命周期。

## 经验

- 在 AI Code CLI 上做能力增强，优先在 MCP 层——工具独立于 CLI 实现，不会因为上游重构而作废。
- 动手前确认目标模块的生命周期：是稳定核心能力，还是随时可能被替代的实验性功能？
