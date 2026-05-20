+++
title = "DeepSeek API 会用我的数据训练模型吗？——条款调研"
date = 2026-05-19T00:00:00+08:00
slug = "deepseek-api-data-training-policy"
tags = ["DeepSeek", "API", "隐私", "数据训练", "调研"]
+++

## 问题

我用 DeepSeek API，我的数据会被拿去训练模型吗？

## 答案

**Open Platform 条款对此保持沉默——没说会，也没说不会。** 不像 OpenAI/Anthropic 那样明确承诺「API 数据不用于训练」。

| 我用的是 | 会被训练吗？ | 能关吗？ |
|---------|:-----------:|:------:|
| Web/App 聊天 | ✅ 默认会 | ✅ 关闭「Improve the model for everyone」 |
| API | ⚠️ 没说 | ❌ 无开关 |

## 我该怎么办

1. **默认当它「会」处理** — 条款没说不会，就不要假设不会
2. **敏感数据不要走 API** — 尤其是用户隐私、商业机密
3. **用本地部署替代** — DeepSeek 开源了模型权重（MIT License），本地跑完全规避
4. **联系官方要求澄清** — <privacy@deepseek.com> / <api-service@deepseek.com>

## 依据

### 依据 1：通用条款允许训练，但可 opt-out（Web/App 端）

**来源：** [DeepSeek Terms of Use — Section 4.3](https://cdn.deepseek.com/policies/en-US/deepseek-terms-of-use.html)

> *"Under the premise of secure encryption technology processing, strict de-identification rendering, and irreversibility to identify specific individuals, we may, to a minimal extent, use Inputs and Outputs to provide, maintain, operate, develop or improve the Services or the underlying technologies supporting the Services."*
>
> *"If you refuse to allow us to process the data in the manner described above, you can opt out by turning off 'Improve the model for everyone'."*

**→ 这说明：Web/App 端默认会用数据训练，但你可以关。**

### 依据 2：隐私政策明确写了训练用途

**来源：** [DeepSeek Privacy Policy](https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html)

> *"To improve and develop the Services and to train and improve our technology, such as our machine learning models and algorithms."*
>
> 用户权利: *"the right to opt-out of using your Personal Data for training our models or optimizing our technologies."*

**→ 这说明：训练用途是书面的，opt-out 权利也是书面的。**

### 依据 3：API 条款缺少等价承诺（关键）

**来源：** [DeepSeek Open Platform Terms of Service](https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html)

通读全文，与通用条款对比：

| 条款 | 通用 Terms（Web/App） | Open Platform Terms（API） |
|------|:---:|:---:|
| 声明可能使用 Input/Output 训练 | ✅ Section 4.3 | ❌ 无 |
| 提供 opt-out 开关 | ✅「Improve the model for everyone」 | ❌ 无 |
| 开发者保留 Input 所有权 | — | ✅ Section 4.2 |
| 引用隐私政策 | — | ✅ Section 5.5 |

**→ 这说明：API 端既没有说会用，也没有说不会用。不承诺 = 不可信。**

### 依据 4：行业对比——别人都承诺了

| 厂商 | 付费 API 承诺不训练？ | 来源 |
|------|:---:|------|
| **OpenAI** | ✅ 明确承诺（2023.3 起） | [developers.openai.com](https://developers.openai.com/api/docs/guides/your-data) |
| **Anthropic** | ✅ 明确承诺 | [privacy.claude.com](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training) |
| **Google Cloud Gemini** | ✅ 明确承诺 | [docs.cloud.google.com](https://docs.cloud.google.com/gemini/docs/discover/data-governance) |
| **DeepSeek** | ❌ 未承诺 | [Open Platform Terms](https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html) |

**→ 这说明：DeepSeek 的沉默不是行业惯例，是落后于同行。**

---

## 补充

- **微博 @刘聪NLP**（2026-05-15）：用户普遍担心 LLM 拿聊天数据训练

