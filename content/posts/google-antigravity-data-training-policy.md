+++
title = "Google Antigravity 会用我的代码训练模型吗？条款分析"
date = 2026-07-17T00:00:00+08:00
slug = "google-antigravity-data-training-policy"

[taxonomies]
tags = ["Google", "Antigravity", "Gemini", "隐私", "数据训练", "调研"]
+++

> **一句话：个人用户（含 AI Pro 订阅）默认按"可能用于训练"处理。条款明确写了用于机器学习技术，Telemetry 开关的法律效力有争议。**

---

## 问题

我通过 Google Antigravity CLI（命令 `agy`）或 Antigravity IDE 使用 Gemini 模型写代码，我的代码、提示词和交互数据会不会被用于训练模型？

这是 2026 年 5 月新发布的工具，替代了之前的 Gemini CLI。它走的是消费者管道（Google 账号 OAuth 登录），不是 Gemini API 管道——所以之前"开 Cloud Billing 就不训练"的结论**不适用**。

## 先看结论

| 用户身份 | 数据会被收集吗？ | 会被用于训练吗？ | Opt-out 机制 |
|---------|:---:|:---:|---|
| 个人 Google 账户（免费/AI Pro） | ✅ 默认收集 | ✅ 可能用于训练 | 无明确机制 |
| 个人 Google 账户 + Telemetry 关闭 | ❓ 声称停止收集 | ❓ 声称不会 | 设置面板关闭（有争议） |
| Google Workspace（标准付费） | ✅ 收集（安全监控） | ❌ 明确承诺不训练 | 无需操作 |
| Workspace AI Ultra for Business | ✅ 收集（安全监控） | ❌ 明确不训练 | 无需操作 |

**实用建议：**

- **个人用户：按"会训练"处理。** 条款明确写了用于机器学习技术，Telemetry 开关的法律效力有争议。敏感代码不要输入。
- **企业用户：走 Workspace。** 标准付费即可享受"不训练"承诺。
- **需要 API 调用：用 Gemini API + Cloud Billing。** 条款明确不用于改进产品。

## 条款怎么说

### Antigravity 附加条款：明确写了用于 ML

来源：[Google Antigravity Additional Terms of Service](https://antigravity.google/terms)

> "When you use the Service, we record and store your user data, interaction data pertaining to your usage of the Service, related metadata connected to the Service, and any feedback you provide ('Interactions')."

> "We use Interactions to evaluate, develop, and improve Google and Alphabet research, products, services and **machine learning technologies**."

条款明确说了用于"机器学习技术"。"Interactions"包括提示词、代码、代码库上下文、元数据。

### Telemetry 开关：唯一的 opt-out 机制，但有争议

条款页面的 opt-out 表述：
> "If you don't want your Interactions used in this way, **navigate to settings** to change your preference on how such data is used."

注意：条款原文只说了"navigate to settings"，没有提到"Enable Telemetry"这个具体名称。有论坛用户在[讨论帖](https://discuss.ai.google.dev/t/urgent-data-deletion-opt-out-request-ignored-missing-privacy-settings/121602)中引用了 Abhijit Pramanik 的回复：

> "The primary mechanism for managing usage data collection is the 'Enable telemetry' setting. When this option is disabled, it stops the collection of interactions data..."

（注：Abhijit Pramanik 是论坛活跃用户，其回复不代表 Google 官方立场。）

**但社区质疑这个逻辑：**

条款说的是"开启时会收集"（When toggled on, collects...），但**没有明确说**"关闭时不收集"。"开启时做 X" 不等于 "关闭时不做 X"——这是一个法律效力的缺口。

> 来源：[Google Antigravity 论坛 - Telemetry opt-out 讨论](https://discuss.ai.google.dev/t/antigravity-data-training-opt-out/125236)、[完全 opt-out 讨论](https://discuss.ai.google.dev/t/how-can-i-completely-opt-out-of-the-use-of-my-data-for-model-training/168429)

### Workspace 用户：明确不训练

来源：[Generative AI in Google Workspace Privacy Hub](https://knowledge.workspace.google.com/admin/gemini/generative-ai-in-google-workspace-privacy-hub)

> "No. User prompts are considered customer data under the Cloud Data Processing Addendum. Workspace does not use customer data to train models without prior customer permission or direction."

Workspace 标准付费版就有这个保护，不需要额外的 Ultra 订阅。

## 与 Gemini API 的管道对比

Antigravity CLI 走的是**消费者管道**（Google 账号 OAuth 登录），不是 Gemini API 管道。这意味着它**不适用** Gemini API 的 Paid/Unpaid 二分法。

| 管道 | 适用条款 | 数据训练 |
|------|---------|---------|
| Gemini API + Cloud Billing | Gemini API Paid Services 条款 | ❌ 不用于改进产品 |
| Gemini API 免费 Key | Gemini API Unpaid Services 条款 | ✅ 用于改进产品 |
| **Antigravity CLI/IDE（consumer）** | **Antigravity 附加条款** | **⚠️ 可能用于训练** |
| Gemini App（网页/手机） | Google 普通隐私政策 + Gemini Apps Activity | 取决于 Keep Activity 开关 |

## Anthropic 侧的额外保护

Antigravity 后端也使用 Claude 模型（Claude Sonnet 4.6、Claude Opus 4.6）。Anthropic 的商业条款提供额外保护层：

> "Anthropic may not train models on Customer Content from Services."

> "Customer Content is Customer's Confidential Information."

这意味着当 Antigravity 路由到 Claude 模型时，Anthropic 侧承诺不训练。但 Google 侧的数据收集仍受 Antigravity 条款管辖。

## 透明度缺口

| 问题 | 严重程度 | 说明 |
|-----|:---:|------|
| Telemetry 开关的法律效力不明确 | 🔴 高 | "开启时收集" ≠ "关闭时不收集"，Google 未明确修正 |
| "Interactions" 是否包含本地代码库 | 🟡 中 | 社区要求澄清，Google 未正面回答 |
| 数据留存期限 | 🟡 中 | 条款说"可以删除"，但未说自动保留多久 |
| 安装时强制同意 | 🟡 中 | 安装 Antigravity 2.0 时必须同意数据收集才能继续 |

## 我该怎么办

1. **默认按"会训练"处理** — 条款明确写了用于机器学习技术，Telemetry 开关的法律效力有争议。在未确认 opt-out 生效前，不要假设数据是安全的
2. **敏感代码：不要输入** — 涉及商业机密/私有仓库的代码不要通过 Antigravity consumer 入口处理
3. **关闭 Telemetry（聊胜于无）** — 设置面板 → Account → Enable Telemetry → 关闭。法律效力有争议，但可能是账号级 opt-out 的触发入口
4. **企业用户：走 Workspace** — Workspace 账户有明确的"不训练"承诺（标准付费即可）
5. **替代方案：Gemini API + Cloud Billing** — 如果只需要 API 调用，在 Google Cloud 开 Billing 后用 Gemini API，条款明确不用于改进产品

## 参考来源

- [Google Antigravity Additional Terms of Service](https://antigravity.google/terms)
- [Google Terms of Service](https://policies.google.com/terms)
- [Google Privacy Policy](https://policies.google.com/privacy)
- [Gemini API Terms of Service](https://ai.google.dev/gemini-api/terms)
- [Generative AI in Google Workspace Privacy Hub](https://knowledge.workspace.google.com/admin/gemini/generative-ai-in-google-workspace-privacy-hub)
- [Google Workspace Blog - AI Ultra for Business 公告](https://workspace.google.com/blog/product-announcements/google-ai-ultra-for-business)
- [Anthropic Commercial Terms](https://www.anthropic.com/legal/commercial-terms)
- [Google Antigravity 论坛 - Telemetry opt-out 讨论](https://discuss.ai.google.dev/t/antigravity-data-training-opt-out/125236)

---

*本文是 [Google 模型服务数据隐私调研](../google-model-service-data-privacy) 的补充，聚焦 Antigravity CLI/IDE 这个新管道。*
