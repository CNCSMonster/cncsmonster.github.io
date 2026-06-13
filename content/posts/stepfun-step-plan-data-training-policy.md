+++
title = "StepFun Step Plan 会用我的数据训练模型吗？——条款调研"
date = 2026-06-13T00:00:00+08:00
slug = "stepfun-step-plan-data-training-policy"
tags = ["StepFun", "Step Plan", "隐私", "数据训练", "调研", "API"]
+++

## 问题

我使用 Step Plan 订阅或 StepFun API，我的代码/对话数据会不会被拿去训练模型？

## 答案

**不会明确排除，也不会明确承诺。** 三份核心文件（隐私政策、用户协议、付费服务协议）均未出现"不用于训练"或"training exclusion"等表述，英文 TOS 保留 "improve the Services" 的宽泛授权。

| 我用的是 | 会被训练吗？ | 条款依据 |
|---------|:-----------:|----------|
| Step Plan（订阅） | ❓ 未承诺排除 | 付费协议无训练条款，引用平台隐私政策 |
| API 按量付费 | ❓ 未承诺排除 | 用户协议 §6.5："改善、优化、升级"目的 |
| 企业版/私有化 | 未公开 | 需商务对接确认 |

---

## 证据

### 证据 1：隐私政策无训练相关表述

**来源：** [StepFun 开放平台隐私政策](https://platform.stepfun.com/legal/privacy-policy.html)（2026-04-23）

2026-06-13 复核：政策全文仍**未出现"模型训练"或"不用于训练"**等任何相关表述。数据使用目的限于"提供智能对话及内容生成服务"和"匿名化运营统计"。

**关键条款**：
> "我们会收集您主动输入的信息...以及服务的输出信息。我们会对上述信息进行分析与计算，以便于更好地理解您的需求和上下文语境..."

"分析与计算"可理解为实时推理所需的上下文处理，但也可能包含离线分析。

---

### 证据 2：英文 TOS 保留 "improve the Services"

**来源：** [StepFun Terms of Service](https://platform.stepfun.ai/docs/en/agreement/userservice)（Section 4.1.4）

> "We may use Content to provide, maintain, develop, and **improve the Services**..."

其中 "develop, and improve the Services" 可涵盖模型训练、微调、评估等用途。

**对比**：OpenAI、Anthropic 的 API 条款均明确排除训练用途。StepFun 在此项显著落后。

---

### 证据 3：Step Plan 付费协议无训练条款

**来源：** [Step Plan 付费服务协议](https://platform.stepfun.com/docs/zh/step-plan/paid-service-agreement)（2026-05-25）

2026-06-13 复核：协议正文**无专门针对数据使用、模型训练、数据留存的条款**，也未作出新增的数据训练排除或数据保留承诺。涉及数据责任的条款仅限第三方工具数据泄露由用户自行承担。

---

### 证据 4：数据留存期限——有初步说明，但不够具体

隐私政策新增说明（本次复核首次明确提取）：
> "仅在为提供本平台相关服务之目的所必需的期间内保留您的个人信息... 注销账户、主动删除个人信息或超出必要的期限后，将对个人信息进行删除或匿名化处理。"

**例外情况**：
- 遵从法律法规关于信息留存的要求
- 出于财务、审计、争议解决等目的需要合理延长期限

**缺口**："必需的期间"具体多长、"超出必要期限"的判断标准、是否有审计机制，均未说明。

---

## 行业对比

| 厂商 | 服务 | 数据训练政策 | 透明度 |
|------|------|-------------|--------|
| **OpenAI** | API | ✅ 明确不训练 | 高 |
| **Anthropic** | API | ✅ 明确不训练 | 高 |
| **小米 MiMo** | API / Token Plan | ✅ 隐私政策逐字承诺 "will not use for training" | 高 |
| **阿里云百炼** | API | ✅ 不训练（通用条款） | 中 |
| **阿里云 Coding Plan** | 订阅 | ⚠️ 通用条款不训练，但订阅套餐 5.2.2 专门授权训练 | 低 |
| **DeepSeek** | API | ❌ 沉默未承诺 | 低 |
| **StepFun** | API / Step Plan | ❌ **未承诺，保留 "improve the Services"** | **低** |

**→ StepFun 与 DeepSeek 处于同一梯队，显著落后于 OpenAI、Anthropic、小米 MiMo。**

---

## 我该怎么办

### 正常使用

协议层面未确认不训练，但 StepFun 也未明确声明会训练。如果你能接受这种模糊状态，可以继续使用，但需遵守以下习惯：

1. **脱敏提交**：避免在 prompt 中包含公司名、人名、具体数字、内部项目代号
2. **分段处理**：核心算法/敏感逻辑在本地处理，仅将通用/抽象部分提交给 API
3. **余额监控**：按量付费用户设置余额告警，避免欠费触发数据删除条款

### 敏感数据场景

如果涉及以下数据，**不建议使用公共 API**：

- 用户个人信息（PII）
- 金融、医疗、政务数据
- 未公开的核心知识产权（专利申请前技术方案）

**替代方案**：

- **改用明确承诺不训练的厂商**：如小米 MiMo（隐私政策逐字承诺）、阿里云百炼 API
- **本地部署**：StepFun 部分模型开源（Step-3.5-Flash 等），可本地运行，数据完全不出机器
- **企业级隔离**：联系 `platform@stepfun.com` 确认私有化部署或专属实例选项

### 企业签约前必问

1. 能否在合同中明确约定"企业数据不用于任何模型训练"
2. 数据留存期限及合同终止后的删除时限
3. 是否提供 VPC/专属实例/私有化部署
4. SLA 承诺及数据泄露赔偿责任
5. 对第三方工具的数据流转有何约束

---

## 参考来源

- [StepFun 开放平台隐私政策](https://platform.stepfun.com/legal/privacy-policy.html)（2026-04-23，2026-06-13 复核）
- [StepFun 开放平台用户协议](https://platform.stepfun.com/legal/user-agreement.html)（2026-04-08）
- [Step Plan 付费服务协议](https://platform.stepfun.com/docs/zh/step-plan/paid-service-agreement)（2026-05-25，2026-06-13 复核）
- [英文 Terms of Service](https://platform.stepfun.ai/docs/en/agreement/userservice)
