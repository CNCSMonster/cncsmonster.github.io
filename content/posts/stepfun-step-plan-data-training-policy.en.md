+++
title = "Does StepFun Train on API Data? A Policy Investigation"
date = 2026-06-13T00:00:00+08:00
slug = "stepfun-step-plan-data-training-policy"
tags = ["StepFun", "Step Plan", "Privacy", "Data Training", "Research"]
+++

## The Question

I use Step Plan or StepFun API. Will my code/conversation data be used to train their models?

## The Answer

**It doesn't explicitly exclude training, nor does it explicitly commit to it.** None of the three core documents (Privacy Policy, User Agreement, Paid Service Agreement) contain phrases like "will not use for training" or "training exclusion". The English TOS retains the broad authorization of "improve the Services".

| I use | Will it train? | Clause basis |
|-------|:--------------:|--------------|
| Step Plan (subscription) | ❓ No commitment to exclude | Paid agreement has no training clause, refers to platform privacy policy |
| API pay-as-you-go | ❓ No commitment to exclude | User Agreement §6.5: "provide, diagnose, improve, optimize, upgrade" purposes |
| Enterprise/private deployment | Not disclosed | Requires business negotiation |

---

## Evidence

### Evidence 1: Privacy Policy has no training-related statements

**Source:** [StepFun Open Platform Privacy Policy](https://platform.stepfun.com/legal/privacy-policy.html) (2026-04-23)

2026-06-13 review: The policy still **does not contain any statements about "model training" or "will not use for training"**. Data usage purposes are limited to "providing intelligent conversation and content generation services" and "anonymized operational statistics".

**Key clause**:
> "We will collect information you actively input... as well as service output information. We will analyze and calculate the above information in order to better understand your needs and context..."

"Analysis and calculation" can be understood as context processing required for real-time inference, but may also include offline analysis.

---

### Evidence 2: English TOS retains "improve the Services"

**Source:** [StepFun Terms of Service](https://platform.stepfun.ai/docs/en/agreement/userservice) (Section 4.1.4)

> "We may use Content to provide, maintain, develop, and **improve the Services**..."

Among them, "develop, and improve the Services" can cover model training, fine-tuning, evaluation and other purposes.

**Comparison**: OpenAI and Anthropic's API terms explicitly exclude training purposes. StepFun lags significantly in this regard.

---

### Evidence 3: Step Plan Paid Agreement has no training clause

**Source:** [Step Plan Paid Service Agreement](https://platform.stepfun.com/docs/zh/step-plan/paid-service-agreement) (2026-05-25)

2026-06-13 review: The agreement **does not contain clauses specifically targeting data usage, model training, or data retention**, nor does it make any new commitments excluding data training or data retention. Clauses involving data liability are limited to users bearing responsibility for data breaches caused by third-party tools.

---

### Evidence 4: Data retention period — preliminary but insufficient

New explanation in privacy policy (first explicitly extracted in this review):
> "We will only retain your personal information for the period necessary for the purpose of providing the platform's related services... After you cancel your account, actively delete personal information, or exceed the necessary period, we will delete or anonymize your personal information."

**Exceptions**:
- Compliance with legal requirements for information retention
- Reasonable extension for financial, audit, dispute resolution purposes

**Gap**: How long is the "necessary period", what are the criteria for "exceeding the necessary period", and whether there is an audit mechanism are not explained.

---

## Industry Comparison

| Provider | Service | Data training policy | Transparency |
|----------|---------|----------------------|--------------|
| **OpenAI** | API | ✅ Explicitly does not train | High |
| **Anthropic** | API | ✅ Explicitly does not train | High |
| **Xiaomi MiMo** | API / Token Plan | ✅ Privacy policy literally promises "will not use for training" | High |
| **Alibaba Cloud Bailian** | API | ✅ Does not train (general clause) | Medium |
| **Alibaba Cloud Coding Plan** | Subscription | ⚠️ General clause says no training, but subscription clause 5.2.2 specifically authorizes training | Low |
| **DeepSeek** | API | ❌ Silent, no commitment | Low |
| **StepFun** | API / Step Plan | ❌ **No commitment, retains "improve the Services"** | **Low** |

**→ StepFun is in the same tier as DeepSeek, significantly behind OpenAI, Anthropic, and Xiaomi MiMo.**

---

## What Should I Do

### Normal Use

The agreement does not confirm no training, but StepFun has not explicitly stated that it will train. If you can accept this ambiguous state, you can continue to use it, but you need to follow these habits:

1. **Desensitize submissions**: Avoid including company names, personal names, specific numbers, and internal project code names in prompts
2. **Segmented processing**: Core algorithms/sensitive logic are processed locally, only generic/abstract parts are submitted to the API
3. **Balance monitoring**: Pay-as-you-go users set balance alerts to avoid data deletion clauses triggered by arrears

### Sensitive Data Scenarios

If the following data is involved, **public APIs are not recommended**:

- User personal information (PII)
- Financial, medical, and government data
- Undisclosed core intellectual property (technical solutions before patent application)

**Alternatives**:

- **Switch to vendors that explicitly commit to no training**: Such as Xiaomi MiMo (privacy policy literal commitment), Alibaba Cloud Bailian API
- **Local deployment**: StepFun partially open-sources models (Step-3.5-Flash, etc.), can run locally, data does not leave the machine at all
- **Enterprise isolation**: Contact `platform@stepfun.com` to confirm private deployment or exclusive instance options

### Questions to Ask Before Enterprise Contracting

1. Can we explicitly agree in the contract that "enterprise data will not be used for any model training"
2. Data retention period and deletion timeline after contract termination
3. Whether VPC/exclusive instance/private deployment is provided
4. SLA commitments and compensation for data breaches
5. What constraints are there on data flow through third-party tools

---

## References

- [StepFun Open Platform Privacy Policy](https://platform.stepfun.com/legal/privacy-policy.html) (2026-04-23, reviewed 2026-06-13)
- [StepFun Open Platform User Agreement](https://platform.stepfun.com/legal/user-agreement.html) (2026-04-08)
- [Step Plan Paid Service Agreement](https://platform.stepfun.com/docs/zh/step-plan/paid-service-agreement) (2026-05-25, reviewed 2026-06-13)
- [English Terms of Service](https://platform.stepfun.ai/docs/en/agreement/userservice)
