+++
title = "小米 MiMo Token Plan 会用我的数据训练模型吗？——协议条款调研"
date = 2026-05-25T00:00:00+08:00
slug = "xiaomi-mimo-token-plan-data-training-policy"
tags = ["小米", "MiMo", "API", "隐私", "数据训练", "调研", "Token Plan"]
+++


> 创建日期：2026-05-25
> 状态：已完成

## 问题

我订阅小米 MiMo Token Plan 或者调用 MiMo API，我的数据会不会被拿去训练模型？

## 答案

**不会。** 隐私政策明确承诺，且 Token Plan 条款没有像阿里云 Coding Plan 那样偷偷加"特别约定"来覆盖这个承诺。

| 我用的是 | 会被训练吗？ | 条款依据 |
|---------|:-----------:|------|
| MiMo API（按量付费） | ✅ 不会 | 隐私政策 3.1 明确承诺 |
| MiMo Token Plan（订阅） | ✅ 不会 | 用户协议 3.13 无特别约定，适用隐私政策 |
| 阿里云 Coding Plan（对比） | ⚠️ 会 | 服务协议 5.2.2 专门授权 |

但有个提醒：**这是基于公开协议的分析，不是法律意见。** 如果涉及敏感数据，最稳妥的方案是本地方案（MiMo-V2.5 已 MIT 开源）。

## 依据

### 依据 1：隐私政策逐字承诺"不训练"

**来源：** [Xiaomi MiMo Open Platform Privacy Policy — Section 3.1](https://platform.xiaomimimo.com/docs/terms/privacy-policy)

> "If you use the API services, we will collect your IP address and the content (text, audio, video, picture) you submit to analyze the relevant instructions based on the model you select and to generate the returned content. **Xiaomi will not use the content you provide for model training or any other purposes.**"

这个承诺覆盖范围很广——不仅是"不训练"，而且是"不用于任何其他目的"。对比 DeepSeek API 条款对此保持沉默，小米的承诺是明确且有力的。

### 依据 2：Token Plan 条款没有像阿里云那样的陷阱

这是本次调研的核心发现。

**阿里云 Coding Plan** 在通用条款之外加了专门的 5.2.2：

> "您同意并授权我们和我们的关联公司存储并使用您使用 Coding Plan 期间因调用模型而输入以及模型生成的内容（'Coding Plan 数据'）以用于**服务改进与模型优化**。"

**小米 Token Plan** 的对应条款（用户协议 3.13）只有：

> "Token Plan services are non-refundable and non-cancellable upon purchase. Xiaomi reserves the right to modify or adjust Token Plan based on operational needs..."

只讲退款，不讲数据。没有 5.2.2 那种"特别约定"。

| 对比项 | 阿里云 Coding Plan | 小米 Token Plan |
|--------|-------------------|-----------------|
| 通用条款 | "不会在未获授权时训练"（6.2.5） | "will not use for training"（Privacy 3.1） |
| 订阅套餐条款位置 | 专门章节 5.2 | 普通条款 3.13 |
| 数据训练特别授权 | ✅ 有（5.2.2） | ❌ 没有 |
| 数据训练结论 | ⚠️ 会训练 | ✅ 不训练 |

### 依据 3：协议结构确认隐私政策适用于 Token Plan

| 条款 | 内容 | 作用 |
|------|------|------|
| 用户协议 1.1 | 适用范围："products, programs and services" | Token Plan 在协议覆盖范围内 |
| 用户协议 1.2 | MiMo 平台隐私政策列为补充协议，同等法律效力 | 隐私政策承诺适用 |
| 用户协议 第4条 | "数据处理依据隐私政策" | 数据处理规则指向隐私政策 |
| 用户协议 3.13 | Token Plan 条款：仅退款/调整，无数据约定 | 没有覆盖隐私政策的特别约定 |

结论：Token Plan 的数据处理应适用隐私政策的承诺——不训练。

### 依据 4：行业全景对比

| 厂商 | 服务类型 | 数据训练政策 | 特别约定？ |
|------|---------|-------------|:---:|
| **小米 MiMo** | Token Plan / API | ✅ 不训练（Privacy 3.1） | ❌ 无陷阱 |
| **Anthropic Claude** | API / 订阅 | ✅ 默认不训练 | ❌ |
| **阿里云百炼 API** | 按量付费 | ✅ 不训练（6.2.5） | ❌ |
| **阿里云 Coding Plan** | 订阅套餐 | ⚠️ 明确训练（5.2.2） | ✅ 有陷阱 |
| **DeepSeek** | API | ⚠️ 沉默未承诺 | — |
| **Kimi** | API | ⚠️ 授权优化服务 | — |

## 我该怎么办

1. **正常使用没问题** — 协议层面已经确认不训练，比 DeepSeek/Kimi 的 API 条款都干净
2. **敏感数据仍建议走本地部署** — MiMo-V2.5 已 MIT 开源（[HuggingFace](https://huggingface.co/XiaomiMiMo/MiMo-V2.5)），支持 SGLang/vLLM，数据完全不出机器
3. **定期回查协议** — 用户协议 8.4 说小米有权修改协议，关注更新（官方联系：<support-mimo@xiaomi.com>）
4. **企业合规场景** — 直接联系官方确认，不依赖公开协议的分析

## 附录：Token Plan 定价参考

<details>
<summary>展开查看</summary>

| 套餐 | 月费（中国） | 月费（海外） | Credits |
|------|-------------|-------------|---------|
| Lite | ¥39 | $6 | 6000万 |
| Standard | ¥99 | $16 | 2亿 |
| Pro | ¥329 | $50 | 7亿 |
| Max | ¥659 | $100 | 16亿 |

首次 88 折，夜间（0:00-8:00）0.8x 消耗。

作为参考：Claude 同级模型 API 价格约为小米的 5 倍，且小米无 5 小时滚动限额。

</details>

## 参考来源

- [小米 MiMo API 平台用户协议](https://platform.xiaomimimo.com/docs/terms/user-agreement)
- [小米 MiMo API 平台隐私政策](https://platform.xiaomimimo.com/docs/terms/privacy-policy)
- [阿里云百炼服务协议](https://terms.alicdn.com/legal-agreement/terms/common_platform_service/20230728213935489/20230728213935489.html)
- [V2EX：阿里云 Coding Plan 隐私警告](https://www.v2ex.com/t/1190601)
