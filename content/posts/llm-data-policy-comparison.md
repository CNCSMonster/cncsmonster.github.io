+++
title = "LLM Provider 数据训练政策横向对比"
date = 2026-07-02T00:00:00+08:00
slug = "llm-data-policy-comparison"
[taxonomies]
    tags = ["LLM", "数据训练", "隐私", "调研", "对比"]
+++

> **更新于 2026-09-22**：修正 DeepSeek 的判定，并修正本文方法论中一条导致该误判的前提。原稿把 DeepSeek API 归入"条款沉默"，是因为只读了《开放平台服务协议》一份文件。

---

## 一句话

已调研的 7 家厂商中，**小米最透明**（隐私政策逐字承诺不训练），**智谱团队版和企业合同次之**，**StepFun 条款沉默**，**DeepSeek 最容易被人读反**——它的开放平台协议看着干净，训练授权却写在母协议《用户协议》4.3 里，而其服务定义包含 API。相比 Kimi 中文版、Google 免费管道那种"明写会训练"，DeepSeek 的问题不是更坏，而是**风险被藏在协议栈上一层**，只读一份文件就会得出相反结论。

---

## 全貌一览

| 厂商 | API 服务 | 数据训练政策 | Opt-out | 可信度 |
|------|---------|-------------|---------|:-----:|
| **小米** | MiMo API / Token Plan | 🟢 **隐私政策逐字承诺 "will not use for training"** | — | 高 |
| **智谱** | 团队版 Coding Plan | 🟢 **明确承诺不用于训练**（专用条款） | — | 中 |
| **智谱** | 个人版 Coding Plan | 🟡 通用条款允许脱敏后训练 | ❌ | 中 |
| **智谱** | 按量付费 API | 🟡 通用条款允许脱敏后训练 | ❌ | 中 |
| **Kimi** | C 端订阅 / API | 🔶 **中文版默认训练**，英文版可邮件 opt-out | 🌐 英文可 | 高 |
| **MiniMax** | API（国际） | 🟡 **ToS 授权改进服务**，未承诺排除 | ❌ | 中 |
| **MiniMax** | API（国内） | 🟡 未明确声明用于训练，但未承诺排除 | ❌ | 中 |
| **DeepSeek** | API | 🔴 **母协议《用户协议》4.3 授权训练**（1.1 服务定义含 API）；子协议无表述、无留存声明 | ❌ API 端无开关 | 高 |
| **StepFun** | Step Plan / API | ⚠️ **条款沉默**，保留 "improve the Services" | ❌ | 低 |
| **Google** | Gemini API（Cloud 付费） | 🟢 **不用于训练** | — | 高 |
| **Google** | Gemini API（免费/消费者） | 🔶 **默认训练** | — | 高 |

---

## 按梯队分组

### 🟢 可信赖（明确承诺不训练）

| 厂商 | 承诺形式 | 说明 |
|------|---------|------|
| 小米 MiMo | 隐私政策逐字承诺 | 国内版："未经您的事先同意不会用于训练"；国际版："will not use for training or any other purposes" |
| 智谱 团队版 | 套餐购买协议专用条款 | "数据默认不用于模型训练"，具有合同法律效力 |
| Google Cloud 管道 | 企业条款 | 开了 Cloud Billing 的 API / Vertex AI 不训练 |

### 🟡 模糊地带（未明确排除）

| 厂商 | 风险点 |
|------|--------|
| 智谱 个人版/按量付费 | 通用协议授权"永久不可撤销"数据使用权 + 脱敏后可用于训练 |
| MiniMax | 国际版 ToS 保留 "improve the Services"；国内版条款沉默 |
| Kimi 英文版 | 默认用于训练，但可邮件 opt-out |

### 🔴 高风险（默认训练或沉默）

| 厂商 | 风险点 |
|------|--------|
| Kimi 中文版 | C 端和 API 都默认用于训练，无 opt-out |
| DeepSeek API | 母协议《用户协议》4.3 保留训练授权，且其服务定义含 API；开放平台协议与隐私政策均未声明是否收集/留存 API 的 prompt 内容 |
| StepFun API / Step Plan | 英文 ToS 保留 "improve the Services"，国内条款沉默 |
| Google 免费/消费者管道 | 默认用于训练 |

---

## 关键差异维度

### Opt-out 能力

| ✅ 可 opt-out | ❌ 无 opt-out |
|-------------|--------------|
| Kimi 英文版（邮件） | 智谱（所有产品） |
| DeepSeek Web/App（开关） | Kimi 中文版（所有产品） |
| | MiniMax（所有产品） |
| | StepFun（所有产品） |

### 国际版 vs 国内版差异

| 厂商 | 差异 |
|------|------|
| **智谱** | 国际版 z.ai 对 API 客户声称不存储（DPA），国内版授权永久使用权 |
| **Kimi** | 英文版可邮件 opt-out，中文版无 |
| **MiniMax** | 国际版 ToS 明确授权训练，国内版条款沉默 |
| **小米** | 两版措辞类似，国际版覆盖更广（"content" 含多模态） |

---

## 方法论说明

- 所有结论基于各厂商的**公开协议原文**，不是营销文案或客服口径
- **判定单元是"协议栈"，不是单份协议**：先列出适用于该产品的全部文件（母协议 / 专门协议 / 隐私政策），逐份查训练授权，并专门查一件事——专门协议有没有把数据处理规则**指回**隐私政策或母协议
- 效力层级（专用合同 > 服务专用条款 > 通用用户协议 > 隐私政策）**只在同一事项存在冲突时**决定谁优先。专门条款对某事项保持沉默**不构成冲突**，母协议对该事项的通用授权继续适用。把"专门条款没写"读成"这个场景不受母协议约束"是错的——DeepSeek 即为反例（开放平台协议无训练条款，但《用户协议》4.3 有，且 1.1 服务定义含 API）
- **"条款沉默"这个标签只用于整条协议栈都查不到训练授权的情形**。若上层协议保留了授权，应写成"母协议授权"，不能归入沉默——两者的处置强度不同
- 沉默的准确含义是**未披露**：既不是"承诺不训练"，也不是"确认训练"。按未披露做保守处置（敏感数据不用），但不要给未披露发正面评级

---

## 各厂商详细调研

| 厂商 | 完整调研 |
|------|---------|
| 小米 MiMo | [查看](https://cncsmonster.github.io/posts/xiaomi-mimo-token-plan-data-training-policy/) |
| 智谱 GLM | [查看](https://cncsmonster.github.io/posts/zhipu-glm-data-training-policy/) |
| Google | [查看](https://cncsmonster.github.io/posts/google-model-service-data-privacy/) |
| DeepSeek | [查看](https://cncsmonster.github.io/posts/deepseek-api-data-training-policy/) |
| StepFun | [查看](https://cncsmonster.github.io/posts/stepfun-step-plan-data-training-policy/) |
| MiniMax | [查看](https://cncsmonster.github.io/posts/minimax-api-data-training-policy/) |
| Kimi | [查看](https://cncsmonster.github.io/posts/kimi-data-training-policy/) |
