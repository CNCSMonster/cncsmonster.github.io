+++
title = "Kimi Code API 接入为什么会 403？"
date = 2026-05-24T00:00:00+08:00
slug = "kimi-code-api-access-403"
tags = ["Kimi", "Kimi Code", "AI Code CLI", "API", "pi", "Qwen Code"]
+++

我在把 Kimi Code 接入 pi 和 Qwen Code 时，遇到一个容易误判的问题：

> 为什么 Kimi Code 官方说支持 OpenAI 兼容协议，但我用标准 OpenAI SDK 调 `coding/v1/chat/completions` 会返回 403？

结论是：**Kimi Code 的 OpenAI 兼容端点会检查 coding agent 客户端身份；对 pi 和 Qwen Code 来说，更稳的方式都是走 Anthropic 兼容端点。**

## 两个端点不是完全等价的

Kimi Code 官方文档提供两个协议端点：

| 协议 | Base URL | 常见用途 |
|---|---|---|
| OpenAI 兼容 | `https://api.kimi.com/coding/v1` | Roo Code / OpenAI-compatible 工具 |
| Anthropic 兼容 | `https://api.kimi.com/coding/` | Claude Code / Anthropic Messages 工具 |

一开始我用 OpenAI SDK 风格请求 OpenAI 兼容端点，返回 403，大意是 Kimi For Coding 只能在 Coding Agents 中使用。

读 Kimi Code CLI 源码后，原因比较清楚：Kimi Code CLI 请求中会附带一组 `X-Msh-*` 身份头，用来标识请求来自 Kimi Code CLI 这类 coding agent。

```ts
// packages/oauth/src/identity.ts
export function createKimiDefaultHeaders(options: KimiIdentityOptions): Record<string, string> {
  return {
    'User-Agent': createKimiUserAgent(options),
    'X-Msh-Platform': 'kimi-code-cli',
    'X-Msh-Version': requiredAsciiHeader(options.version, 'Kimi identity version'),
    'X-Msh-Device-Name': asciiHeader(hostname()),
    'X-Msh-Device-Model': asciiHeader(deviceModel()),
    'X-Msh-Os-Version': asciiHeader(release()),
    'X-Msh-Device-Id': createKimiDeviceId(options.homeDir),
  };
}
```

所以这里的 403 不是简单的 API Key 错误，也不只是 User-Agent 问题，而是 OpenAI 兼容端点还依赖额外的客户端身份信息。

> 注意：Kimi 官方文档也提醒，使用时应保持工具真实身份标识，篡改客户端标识可能导致会员权益暂停。公开或生产使用时不要为了绕过限制伪造身份。

## pi：推荐走 Anthropic 兼容协议

对 pi 来说，最省事也最干净的方式是直接配置 Anthropic 兼容端点：

```json
{
  "kimi": {
    "baseUrl": "https://api.kimi.com/coding/",
    "api": "anthropic-messages",
    "apiKey": "KIMI_CODE_API_KEY",
    "models": [
      {
        "id": "kimi-for-coding",
        "name": "[Kimi Coding Plan]",
        "reasoning": true,
        "input": ["text", "image"],
        "contextWindow": 262144,
        "maxTokens": 128000
      }
    ]
  }
}
```

这个端点用 `x-api-key` 认证即可，不需要额外注入 `X-Msh-*` 头。我本地用 pi 实测可以正常返回。

## Qwen Code：也应该优先走 Anthropic 兼容协议

Qwen Code 同样支持 `modelProviders.anthropic`，因此也没必要优先走 OpenAI 兼容端点。

推荐配置形态是把 Kimi Code 放到 `modelProviders.anthropic` 里：

```json
{
  "modelProviders": {
    "anthropic": [
      {
        "id": "kimi-for-coding",
        "name": "[Kimi Code] K2.6",
        "baseUrl": "https://api.kimi.com/coding",
        "envKey": "KIMI_CODE_API_KEY",
        "generationConfig": {
          "contextWindowSize": 262144
        }
      }
    ]
  }
}
```

我查了当前 Qwen Code 源码：Anthropic provider 对非 Anthropic 原生 base URL 会走 proxy identity，使用 `Authorization: Bearer <key>`。我又用 curl 验证了 Kimi Code 的 Anthropic `/v1/messages` 端点同时接受 `x-api-key` 和 `Authorization: Bearer`，都能返回 200。

所以更准确的建议是：

- pi：走 `anthropic-messages`。
- Qwen Code：走 `modelProviders.anthropic`。
- 只有在你明确要调试 OpenAI 兼容端点时，才需要研究 `X-Msh-*` 和 `customHeaders`。

## 如果仍然走 Qwen Code 的 OpenAI 兼容端点

如果你确实在 Qwen Code 中走 OpenAI 兼容端点，需要注意一个配置位置问题：`customHeaders` 不能放在模型配置外层，而要放进 `generationConfig`。

原因是 Qwen Code 的 OpenAI-compatible provider 从 `contentGeneratorConfig.customHeaders` 读取自定义头，而 `contentGeneratorConfig` 是由 `generationConfig` 构造出来的。

也就是说：

```json
{
  "generationConfig": {
    "customHeaders": {
      "...": "..."
    }
  }
}
```

才会生效。

> ⚠️ 以上仅解释技术机制，不建议为了绕过限制伪造客户端身份。生产或公开配置应以 Kimi 官方允许的接入方式为准。

## 这次排查的经验

- **兼容协议不等于等价协议。** OpenAI-compatible 和 Anthropic-compatible 只是接口形状相似，不代表认证、网关和风控逻辑相同。
- **403 不一定是 Key 错。** 也可能是请求头、客户端身份、端点策略不匹配。
- **优先选择阻力最小的官方路径。** 对 pi 和 Qwen Code 来说，Anthropic 兼容端点就是更合适的接入方式。
