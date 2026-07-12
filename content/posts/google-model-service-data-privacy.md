+++
title = "Google 模型服务数据隐私调研"
date = 2026-05-21T00:00:00+08:00
slug = "google-model-service-data-privacy"
[taxonomies]
    tags = ["Google", "Gemini", "API", "隐私", "数据训练", "调研"]
+++

> **一句话：数据是否被训练，不看你是不是会员/订阅，只看走的哪条管道——Google Cloud 管道有隐私保护，消费者管道没有。**

---

## 会被训练 vs 不会训练

### 会被训练

| 场景 | 为什么 |
|------|--------|
| Gemini App（网页/手机） | 免费和 Pro/Ultra 会员隐私条款相同，都允许训练 |
| Google AI Studio（网页聊天） | 官方列在「非付费服务」下（未开 Billing 时） |
| Gemini API 免费 Key | 没开 Cloud Billing 的 Key 走「非付费服务」条款 |
| Gemini CLI（Google 账号登录） | 走 Google 普通隐私政策 |
| Gemini Code Assist 个人免费 | IDE 插件免费版 |

### 不会训练

| 场景 | 为什么 |
|------|--------|
| Gemini API + Cloud Billing | 开 Billing 后所有 API/AI Studio 使用自动按付费处理 |
| Vertex AI | Google Cloud 企业平台，条款明确不训练 |
| Gemini Code Assist Standard/Enterprise | 走 Google Cloud 企业条款 |
| Workspace Gemini（企业版） | Gmail/Docs 里的 AI |
| NotebookLM | 条款明确上传文档不用于训练 |
| EEA/UK/CH 用户的 API | 地区法律强制，免费 API 也按付费标准 |

---

## 三个关键发现

### 1. "会员 ≠ API 付费"

Google AI Pro/Ultra 会员（每月 $20-$100）是**消费者订阅**，不是 API 付费。数据保护不因此改变，只有开了 Cloud Billing 才算。

### 2. API Key 免费就能拿

去 aistudio.google.com，无需绑卡即可创建。Pro 会员只是让免费配额变多，不改变隐私规则。

### 3. Cloud Billing 是唯一开关

在 Google Cloud 绑一张信用卡，API 调用自动从「免费服务」切为「付费服务」——哪怕一分钱不花。免费配额（如 Flash 每天 1500 次）对个人开发完全够用。

---

## 实践路径

```
需要隐私保护？
→ console.cloud.google.com 绑卡开 Billing
→ aistudio.google.com 拿 Key（选已关联 Billing 的项目）
→ 零成本，不再被训练
```

---

## 参考

- [Gemini API 附加服务条款](https://ai.google.dev/gemini-api/terms?hl=zh-cn)
- [Gemini API 数据记录和共享](https://ai.google.dev/gemini-api/docs/logs-policy?hl=zh-cn)
- [Gemini 应用隐私信息中心](https://support.google.com/gemini/answer/13594961?hl=zh-Hans)
- [Google Workspace Generative AI Privacy Hub](https://knowledge.workspace.google.com/admin/gemini/generative-ai-in-google-workspace-privacy-hub)
- [Google AI Studio + Google One 订阅博客公告 (2026-04-20)](https://blog.google/innovation-and-ai/technology/developers-tools/google-one-ai-studio)
