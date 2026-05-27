+++
title = "MiMo 模型配置避免降智：thinking 参数正确配置"
date = 2026-05-28T00:00:00+08:00
slug = "mimo-thinking-config-guide"
tags = ["小米", "MiMo", "配置", "thinking", "reasoning", "API", "pi", "qwen-code"]
+++

> 创建日期：2026-05-27
> 更新日期：2026-05-28
> 状态：已完成
> 类型：踩坑记录（半衰期 5-10 年）
> 来源：配置 MiMo V2.5 Pro 到 pi/qwen-code 的实践经验

## 问题

MiMo 模型配置不当会导致"降智"——推理能力静默失效，不报错但不思考。表现为：模型回答简单问题还行，但需要复杂推理时质量明显下降。

## 核心发现

**`reasoning: true` ≠ 推理功能真的在工作。** 要让客户端正确使用推理模型，需要三个配置项同时正确：

| 配置项 | 作用 | 缺失后果 | 官方依据 |
|--------|------|----------|----------|
| `thinkingFormat` | 告诉客户端用什么参数格式请求思考 | 请求格式错误，API 不返回 reasoning | [小米官方文档](https://platform.xiaomimimo.com/docs/zh-CN/api/chat/openai-api) |
| `requiresReasoningContentOnAssistantMessages` | 告诉客户端多轮回放时必须传回 `reasoning_content` | MiMo 要求每个 assistant message（带 tool_calls）必须传回，否则 400 | [小米官方 FAQ](https://platform.xiaomimimo.com/docs/en-US/faq) |
| `maxTokensField` | 某些 provider 用 `max_completion_tokens` 而非 `max_tokens` | 参数名错误，服务端忽略或报错 | [小米官方文档示例](https://platform.xiaomimimo.com/docs/zh-CN/api/chat/openai-api) |

三者缺一不可。

## 根本原则

**配置任何模型服务，第一步是查官方文档。** 没有官方文档依据，不凭感觉配置。

## 正确路径：先查文档，配置三件套

### 步骤 1：读官方 API 文档

确认三个关键信息：
1. 思考参数名（`thinking` / `enable_thinking` / `reasoning_effort`）
2. 合法值（`enabled/disabled` / `true/false` / `low/medium/high`）
3. reasoning_content 回传要求

> **MiMo 官方依据**：[小米 MiMo API 官方文档](https://platform.xiaomimimo.com/docs/zh-CN/api/chat/openai-api) 明确说明 `thinking.type` 可选值为 `enabled` 和 `disabled`。

### 步骤 2：选择匹配的 thinkingFormat

pi 的 `thinkingFormat` 配置项决定 pi 向 API 发送哪几个参数：

| thinkingFormat 值 | pi 发送的 API 参数 | 适用模型 |
|-------------------|-------------------|---------|
| `"reasoning_effort"` | 只发 `reasoning_effort` | 标准 OpenAI |
| `"deepseek"` | 同时发 `thinking` **和** `reasoning_effort` | DeepSeek V4, MiMo |
| `"qwen"` | 只发 `enable_thinking` | 百炼 Qwen |
| `"qwen-chat-template"` | 只发 `chat_template_kwargs.enable_thinking` | 本地 Qwen |

**MiMo 使用 `"deepseek"` 格式**（同时发送 `thinking` 和 `reasoning_effort`），不是 `"reasoning_effort"` 也不是 `"qwen"`。

> **官方依据**：[小米 MiMo API 官方文档](https://platform.xiaomimimo.com/docs/zh-CN/api/chat/openai-api) 明确说明使用 `thinking.type` 参数控制思维链，与 DeepSeek 格式一致。

### 步骤 3：配置 thinkingLevelMap（如需要）

pi 有 6 个思考级别：`off`、`minimal`、`low`、`medium`、`high`、`xhigh`。

目标 API 不一定全支持。`thinkingLevelMap` 做映射：

| 映射 | 含义 | 示例 |
|------|------|------|
| `"minimal": "low"` | pi 的 `minimal` → API 的 `low` | MiMo 不支持 `minimal`，用 `low` 替代 |
| `"xhigh": "high"` | pi 的 `xhigh` → API 的 `high` | MiMo 最高只到 `high` |
| `"medium": null` | pi 的 `medium` → 在 UI 中隐藏 | 模型不支持中等推理 |

### 步骤 4：改一项，验一项

```bash
# 逐个验证配置项
pi -p "test" --model mimo-v2.5-pro
```

## 实际配置示例

### pi 的 models.json 配置

```json
{
  "xiaomi-token-plan-cn": {
    "baseUrl": "https://token-plan-cn.xiaomimimo.com/v1",
    "api": "openai-completions",
    "apiKey": "MIMO_API_KEY",
    "compat": {
      "supportsDeveloperRole": false,
      "supportsReasoningEffort": true,
      "thinkingFormat": "deepseek",
      "requiresReasoningContentOnAssistantMessages": true,
      "maxTokensField": "max_completion_tokens"
    },
    "models": [
      {
        "id": "mimo-v2.5-pro",
        "name": "[XiaoMi] MiMo V2.5 Pro",
        "reasoning": true,
        "input": ["text"],
        "contextWindow": 1048576,
        "maxTokens": 64000,
        "thinkingLevelMap": {
          "minimal": "low",
          "xhigh": "high"
        }
      }
    ]
  }
}
```

> **官方依据**：[小米 MiMo API 官方文档](https://platform.xiaomimimo.com/docs/zh-CN/api/chat/openai-api) 示例中使用 `max_completion_tokens` 参数。

### qwen-code 的配置（格式完全不同）

```json
{
  "generationConfig": {
    "extra_body": {
      "thinking": {
        "type": "enabled"
      }
    }
  }
}
```

**注意**：同一个 MiMo API，pi 和 qwen-code 的配置语法完全不同，不能照搬。

## 各模型 API 支持的 reasoning 参数对比

| 模型 | thinking 开关 | reasoning_effort 值域 | 必须回传 reasoning_content |
|------|-------------|---------------------|--------------------------|
| DeepSeek V4 | ✅ `enabled`/`disabled` | `high`/`max` | ✅ 是（带 tool_calls 时） |
| MiMo V2.5 Pro | ✅ `thinking.type: enabled/disabled` | `low`/`medium`/`high` | ✅ 是 |
| 百炼 Qwen | `enable_thinking: true/false` | 不支持 | ❌ 不需要 |

> **官方依据**：[小米 MiMo API 官方文档](https://platform.xiaomimimo.com/docs/zh-CN/api/chat/openai-api) 明确说明 `thinking.type` 可选值为 `enabled` 和 `disabled`，默认值因模型而异。

## 调试三条黄金法则

1. **先读官方文档**：配任何 API 前，先找模型官方的 API 文档（参数名、合法值、thinking 控制方式、content 是否回传）。不搜二手帖子、不凭直觉猜。

2. **一次只改一项，改了立刻验证**：改一个 setting → 用 `pi -p "测试" --model <id>` 验证 → 确认 OK 再改下一项。试错不要叠加。

3. **遇到报错先读报错**：报错信息往往就是答案。例：`Input should be 'low', 'medium' or 'high', input: 'minimal'` 这句话等于一份 API 参数说明书。先读清报错，再排查是值不对、格式不对还是没重载，**不要看到报错就换格式**。

## 常见错误排查

| 现象 | 可能原因 | 排查方法 |
|------|----------|----------|
| 模型回答简单，但复杂问题质量差 | thinking 参数未生效 | 检查 thinkingFormat 是否正确 |
| 多轮对话报 400 错误 | reasoning_content 未回传 | 检查 requiresReasoningContentOnAssistantMessages |
| 参数名错误 | maxTokensField 配置错误 | 检查是 max_tokens 还是 max_completion_tokens |
| 思考级别不生效 | thinkingLevelMap 映射错误 | 检查 API 支持的值域 |

## contextWindow 精确值

`1M` 的数学精确值是 `1_048_576`（1024×1024），不是 `1_000_000`。虽然 API 通常都会接受，但精确值更专业。

## 参考来源

### 小米官方文档
- [小米 MiMo API 官方文档 - OpenAI API](https://platform.xiaomimimo.com/docs/zh-CN/api/chat/openai-api) - `thinking.type` 参数说明、`max_completion_tokens` 示例
- [小米 MiMo API 官方文档 - FAQ](https://platform.xiaomimimo.com/docs/en-US/faq) - `reasoning_content` 多轮回放要求
- [Model Hyperparameters](https://platform.xiaomimimo.com/docs/en-US/quick-start/model-hyperparameters) - temperature/top_p 参数说明

### 第三方验证
- [AI/ML API 文档 - MiMo V2.5 Pro](https://docs.aimlapi.com/api-references/text-models-llm/xiaomi/mimo-v2.5-pro) - 确认 `reasoning_effort` 支持 `low`, `medium`, `high`
- [nanobot issue #3585](https://github.com/HKUDS/nanobot/issues/3585) - 确认 `reasoning_effort` 可选值为 `low`, `medium`, `high`, `adaptive`, `null`
- [OpenRouter MiMo API](https://openrouter.ai/xiaomi/mimo-v2.5/api) - reasoning 参数使用说明

### 其他来源
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs)
- pi 的 thinkingFormat 配置文档
- 实践经验总结

## 官方文档验证结果

| 笔记声明 | 验证状态 | 官方依据 |
|----------|----------|----------|
| MiMo 使用 `thinking.type` 格式（`enabled`/`disabled`） | ✅ 已验证 | [小米官方文档 - OpenAI API](https://platform.xiaomimimo.com/docs/zh-CN/api/chat/openai-api) |
| `reasoning_effort` 支持 `low`/`medium`/`high` | ✅ 已验证 | [AI/ML API 文档](https://docs.aimlapi.com/api-references/text-models-llm/xiaomi/mimo-v2.5-pro) |
| `reasoning_content` 必须多轮回放时传回 | ✅ 已验证 | [小米官方文档 - FAQ](https://platform.xiaomimimo.com/docs/en-US/faq) |
| 不传回 `reasoning_content` 会报 400 | ✅ 已验证 | [小米官方文档 - FAQ](https://platform.xiaomimimo.com/docs/en-US/faq) |
| `maxTokensField` 为 `max_completion_tokens` | ✅ 已验证 | [小米官方文档 - OpenAI API](https://platform.xiaomimimo.com/docs/zh-CN/api/chat/openai-api) 示例代码 |
| MiMo 使用 `"deepseek"` 格式 | ✅ 已验证 | 官方文档确认使用 `thinking.type` 格式，与 DeepSeek 格式一致 |

**关键发现**：
1. 小米官方文档明确说明使用 `thinking.type` 参数控制思维链（`enabled`/`disabled`）
2. 官方示例代码中使用 `max_completion_tokens` 参数
3. FAQ 中明确说明多轮对话需要传回 `reasoning_content`
4. MiMo 的 `thinking.type` 格式与 DeepSeek 的 `thinking` 格式一致，因此 pi 中应使用 `"deepseek"` 格式
