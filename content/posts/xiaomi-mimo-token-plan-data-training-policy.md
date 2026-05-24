+++
title = "小米 MiMo Token Plan 会用我的数据训练模型吗？——协议条款调研"
date = 2026-05-25T00:00:00+08:00
slug = "xiaomi-mimo-token-plan-data-training-policy"
tags = ["小米", "MiMo", "API", "隐私", "数据训练", "调研", "Token Plan"]
+++

## 一、产品概述

小米于 **2025年12月17日** 正式发布 MiMo 大模型及 API 开放平台，2026年4月3日推出订阅制套餐 **Token Plan**。

**核心定位**：面向开发者和 Agent 用户（"养虾党"）的 AI 大模型 API 平台，支持 1M 超长上下文、无时间限制使用。

**官方链接**：
- API 平台：https://platform.xiaomimimo.com/
- AI Studio 体验：https://aistudio.xiaomimimo.com/
- 开源模型：https://huggingface.co/XiaomiMiMo/

---

## 二、Token Plan 套餐定价

| 套餐 | 月费（中国） | 月费（海外） | Credits | 约等于任务量 |
|------|-------------|-------------|---------|-------------|
| Lite | ¥39 | $6 | 6000万 (60M) | ~120 个中等复杂任务 |
| Standard | ¥99 | $16 | 2亿 (200M) | ~400 个中等复杂任务 |
| Pro | ¥329 | $50 | 7亿 (700M) | ~1400 个中等复杂任务 |
| Max | ¥659 | $100 | 16亿 (1600M) | ~3200 个中等复杂任务 |

**优惠**：
- 首次购买享 88折（仅限一次）
- 夜间优惠（0:00-8:00 北京时间）：0.8x 消耗系数
- 连续包月/包年折扣

---

## 三、Credit 换算规则

**MiMo-V2.5 更新后的换算**（1M 上下文不再额外收费）：

| 模型 | 上下文 | 换算比例 |
|------|--------|---------|
| MiMo-V2.5 | 1M | 1 token = 1 credit |
| MiMo-V2.5-Pro | 1M | 1 token = 2 credits |

**支持模型**：MiMo-V2.5-Pro、MiMo-V2.5、MiMo-V2.5-TTS 系列、MiMo-V2-Pro、MiMo-V2-Omni

---

## 四、核心特点

### 优势

1. **无 5 小时滚动限额** — 区别于 Anthropic、OpenAI、阿里等厂商的限制，支持集中消耗
2. **支持第三方框架** — 兼容 OpenCode、OpenClaw、Claude Code、Cline、Cherry Studio 等
3. **1M 超长上下文** — 支持 Agent 多轮对话、长链推理场景，不再额外收费
4. **模型性价比高** — API 价格约为 Claude 同级模型的 1/5
5. **Cache 写入限时免费** — 降低 Agent 开发成本
6. **完全开源** — MiMo-V2.5 系列 MIT 协议开源，可本地部署

### 注意事项

1. 不支持套餐降级，仅支持跨等级补差价升级
2. 套餐到期 Credits 不结转，需重新订阅
3. 自动续费功能已上线
4. API Key 格式区分：Token Plan 用 `tp-xxxxx`，按量付费用 `sk-xxxxx`

---

## 五、数据训练政策分析（重点）

### 官方隐私政策声明

**隐私政策原文**（Section 3.1）：

> "If you use the API services, we will collect your IP address and the content (text, audio, video, picture) you submit to analyze the relevant instructions based on the model you select and to generate the returned content. **Xiaomi will not use the content you provide for model training or any other purposes.**"

**翻译**：小米不会使用你通过 API 提交的内容进行模型训练或任何其他目的。

### 协议结构分析

**关键问题**：Token Plan 是否有专门的数据训练条款？

| 协议条款 | 内容 |
|---------|------|
| 用户协议 1.1 | 适用范围："products, programs and services"（包含 Token Plan） |
| 用户协议 1.2 | MiMo 平台隐私政策列为补充协议（supplementary agreement），与主协议具有同等法律效力 |
| 用户协议 3.13 | Token Plan 条款，**仅涉及退款和调整政策，无数据使用约定** |
| 用户协议 第4条 | "数据处理依据隐私政策" |
| 隐私政策 | "Xiaomi will not use the content you provide for model training" |

**结论**：Token Plan 没有专门的"数据训练特别条款"，数据处理应适用隐私政策的承诺（不用于训练）。

### 与阿里云 Coding Plan 对比

| 项目 | 阿里云 Coding Plan | 小米 Token Plan |
|------|------------------|------------------|
| 通用条款（API 按量付费） | "不会在未获您明确授权的情况下使用对话数据训练模型"（6.2.5） | "will not use the content for model training"（Privacy 3.1） |
| 订阅套餐条款 | **专门章节 5.2**（"关于 Coding Plan 的特别约定"） | **普通条款 3.13**（嵌入平台服务章节） |
| 数据训练特别条款 | ✅ **有**（5.2.2 明确授权"用于模型优化"） | ❌ **没有** |
| 最终结论 | ⚠️ **Coding Plan 会用于训练** | ✅ **应适用隐私政策（不训练）** |

**关键差异**：阿里云服务协议有专门的"关于 Coding Plan 的特别约定"章节（5.2），其中 5.2.2 明确授权数据用于"模型优化"；小米用户协议中 Token Plan 相关条款（3.13）只涉及退款，没有改变数据处理规则的"特别约定"。

### 验证建议

尽管协议结构分析显示 Token Plan 应适用隐私政策，但仍建议：

1. 购买订阅页面是否显示额外的数据授权提示
2. 联系官方确认：support-mimo@xiaomi.com
3. 定期查看协议更新（用户协议 8.4 说小米有权修改）

---

## 六、与竞品对比

| 厂商 | 服务类型 | 数据训练政策 | 5小时限额 | 长上下文 |
|------|---------|-------------|----------|---------|
| **小米 MiMo** | Token Plan | ✅ 不训练（协议结构分析） | ❌ 无 | 1M |
| **Anthropic Claude** | API/订阅 | ✅ 默认不训练 | ✅ 有 | 200K |
| **阿里云百炼 API** | 按量付费 | ✅ 不训练 | ✅ 有 | 部分模型 1M |
| **阿里云 Coding Plan** | 订阅套餐 | ⚠️ **明确训练**（5.2.2） | ✅ 有 | - |
| **DeepSeek** | API/Web | ⚠️ 默认训练（可 opt-out） | - | - |

---

## 七、社区讨论摘要

### V2EX 讨论（Token Plan 上线）

**主要话题**：
- 价格和性价比讨论
- 与 GLM、DeepSeek 性能对比
- Token 消耗速度很快
- 担忧小米对大模型的投入决心

**关键发现**：在 42 条回复中，**没有人讨论数据训练或隐私政策问题**。

### 与阿里云 Coding Plan 讨论 V2EX 对比

阿里云 Coding Plan 有用户主动发现条款 5.2.2，在 V2EX 发帖警告"你的数据会被用于训练"；小米 Token Plan 目前无类似讨论。

---

## 八、使用建议

### 适合场景

- Agent 开发（多轮调用、长上下文）
- 重度编程用户（集中 coding session）
- 需要灵活控制成本的开发者
- 1M 上下文需求场景

### 不适合场景

- 需要企业级合规保障的场景（建议直接确认官方）
- 极端敏感的项目（建议本地部署）

### 本地部署替代方案

MiMo-V2.5 已完全开源（MIT 协议），可本地部署：
- 模型权重：https://huggingface.co/XiaomiMiMo/MiMo-V2.5
- 支持 SGLang、vLLM 推理框架
- 本地部署 = 数据完全不出机器

---

## 九、参考来源

- 小米 MiMo API 平台用户协议：https://platform.xiaomimimo.com/docs/terms/user-agreement
- 小米 MiMo API 平台隐私政策：https://platform.xiaomimimo.com/docs/terms/privacy-policy
- 阿里云百炼服务协议：https://terms.alicdn.com/legal-agreement/terms/common_platform_service/20230728213935489/20230728213935489.html
- V2EX 讨论：https://www.v2ex.com/t/1203353（小米 Token Plan）、https://www.v2ex.com/t/1190601（阿里云 Coding Plan 隐私警告）
