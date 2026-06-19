+++
title = "MiniMax 模型服务会用我的数据训练吗？"
date = 2026-06-19T00:00:00+08:00
slug = "minimax-api-data-training-policy"
tags = ["MiniMax", "API", "隐私", "数据训练", "调研"]
+++

如果你正在考虑用 MiniMax API 处理代码、文档或个人内容，又担心输入/输出被拿去训练模型，这篇直接给你答案和依据。

> 调研日期：2026-06-19。pricing 以 [MiniMax 官方定价页](https://platform.minimax.io/docs/pricing/overview) 实时页面为准。

## 一句话结论

MiniMax 的四类模型服务产品中，**国际 API 平台的 ToS 明确授权使用输入/输出改进服务；国内 API 平台政策未明说训练，但也未承诺排除**。都没有“关闭训练”的开关。

| 产品 | 训练风险 | 依据 |
|------|---------|------|
| 国内 Token Plan | ⚠️ 未明说训练，但未承诺排除 | 国内开放平台隐私政策 |
| 国内 Pay as You Go | ⚠️ 同左 | 同左 |
| 国际 Token Plan | ❌ 可能用于改进服务 | Terms of Service 明确授权 |
| 国际 Pay as You Go | ❌ 同左 | 同左 |

---

## 答案：不同场景能不能用？

| 场景 | 国内 API | 国际 API | 理由 |
|------|---------|---------|------|
| 公开算法/通用脚本 | ✅ | ✅ | 训练风险低 |
| 学生作业/个人原型 | ✅ | ⚠️ | 国际 ToS 已授权使用输入/输出 |
| 个人日记/简历/身份信息 | ⚠️ | ❌ | 不建议输入敏感个人信息 |
| 公司代码/商业逻辑 | ❌ | ❌ | 数据训练风险不可控 |
| 含密码/API Key 的代码 | ❌ | ❌ | 严禁 |

**核心原则**：只要内容对你有保密价值，就别直接发给 MiniMax API。国际 API 平台在法律授权上最宽松，国内 API 平台政策文本最模糊。

---

## 依据

### 依据 1：国际 API 平台明确授权使用输入/输出

**来源**：[MiniMax API Terms of Service](https://platform.minimax.io/protocol/terms-of-service)

> As between you and us, and to the extent permitted by applicable laws, you retain your ownership rights in Client input and generated content. We may use the input and generated content to provide, maintain, develop, and improve our Services...

**说明**：虽然 Privacy Policy 声明不将“个人数据”用于画像/定向训练，但 Terms of Service 明确保留了使用用户输入和生成内容来 develop and improve Services 的权利。这通常包括模型优化。

### 依据 2：国内 API 开放平台政策文本模糊

**来源**：[MiniMax 开放平台隐私政策](https://platform.minimaxi.com/protocol/privacy-policy)

> 调用 API：我们收集该次提交的处理数据... 用于后台计算，生成返回数据...

**说明**：政策没有写“模型训练”，但也**没有承诺排除**。不能作为国内 API “不训练”的安全依据。

### 依据 3：均无专门 opt-out

MiniMax 各模型服务产品都没有“关闭数据训练”的开关。个人用户如果不同意，只能选择停止使用，或尝试行使删除/撤回同意等一般性权利。

---

## 我该怎么办？

1. **不要输入密码、API Key、身份证号、内部代码。**
2. **不要把公司文档、客户数据、商业逻辑发上去。**
3. **国际 API 用户尤其谨慎**：ToS 明确授权使用输入/输出改进服务。
4. **已经输入过敏感内容**：可联系官方删除，但无法保证训练数据被彻底清除。
5. **对隐私高度敏感的内容**：优先使用本地模型。
6. **企业用户**：如需书面排除训练，需通过官方销售通道谈判，个人用户无此选项。

---

## 参考来源

- [MiniMax API Privacy Policy（英文）](https://platform.minimax.io/protocol/privacy-policy)
- [MiniMax API Terms of Service（英文）](https://platform.minimax.io/protocol/terms-of-service)
- [MiniMax 开放平台隐私政策（中文）](https://platform.minimaxi.com/protocol/privacy-policy)
- [MiniMax 官方定价页](https://platform.minimax.io/docs/pricing/overview)

---

**作者注**：这是基于公开政策的分析，不构成法律建议。协议可能更新，关键决策前请复核官方原文。
