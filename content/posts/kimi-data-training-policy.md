+++
title = "Kimi 会用我的数据训练模型吗？中文、英文和 API 协议不一样"
date = 2026-05-24T00:00:00+08:00
slug = "kimi-data-training-policy"
tags = ["Kimi", "API", "隐私", "数据训练", "调研"]
+++

我想确认一个很具体的问题：

> 用 Kimi 聊天、订阅 Kimi 会员，或者调用 Kimi API，我的数据会不会被用于模型训练或服务优化？能不能 opt out？

结论不是一句「会」或「不会」能说清楚。**Kimi 中文 C 端、英文 C 端、API 平台对应的公开协议不一样，签约主体也不一样。**

## 先看结论

| 用户身份 | 签约主体 | 默认是否授权用于优化/改进 | 定向 opt-out |
|---|---|---:|---:|
| 中文 C 端用户 | 北京月之暗面科技有限公司 | ✅ 是 | ❌ 公开协议未提供 |
| 英文 C 端用户 | Moonshot AI PTE. LTD.（新加坡） | ✅ 是 | ✅ 邮件 |
| API 开发者 | 北京月之暗面科技有限公司 | ✅ 授权优化 | ❌ 公开协议未提供 |

所以我的实用判断是：

- **中文 Kimi 聊天/会员：不要输入敏感数据。** 公开协议里没有看到定向退出模型/服务优化的机制。
- **英文 Kimi：可以通过邮件 opt out。** 协议写了 `membership@moonshot.ai`。
- **Kimi API：不要默认当成 OpenAI/Anthropic 那种「API 数据不训练」。** 公开协议没有给出同等承诺。

## 中文 C 端：授权用于模型服务优化，但没有找到定向 opt-out

中文版《Kimi用户服务协议》第五节写道：

> 为了提升您使用本服务的体验，您授予我们一项免费的使用权，以在法律允许的范围内将您输入输出之内容及反馈用于模型服务优化。

我在协议里没有找到类似「退出训练」「opt out」「不参与模型优化」的定向退出路径。

中文版隐私政策也把「对话信息」列入用于提供服务和优化模型的信息范围：

> 您在使用我们的产品和服务过程中输入和输出的文本、语音/音频、图片、视频等各类型内容。这些信息有助于我们为您提供服务、优化模型，并了解您的需求和偏好。

这里的关键点不是它有没有写「训练」两个字，而是：**它明确写了可以用于优化模型/模型服务优化，并且没有提供像英文协议那样的定向 opt-out。**

## 英文 C 端：有邮件 opt-out

英文版 Terms of Service 写得更明确，也给了退出方式：

> We may use your Content to operate, maintain, improve, and develop the Services...
>
> You may opt out of allowing your Content to be used for model improvement and research purposes by contacting us at membership@moonshot.ai.

这里要注意两件事：

1. 英文版协议主体是 **Moonshot AI PTE. LTD.**，不是北京月之暗面科技有限公司。
2. 英文版有 opt-out，不代表中文用户自动拥有同样的合同权利。

## API 平台：公开条款没有「API 数据不用于训练」承诺

API 开放平台协议也有授权优化服务的表述，例如：

> 您输入的知识文档、数据、文本、文件、资料、链接等内容会在本协议约定范围（包括提供、优化服务等）内被使用……

以及：

> 为了提升您使用本服务的体验，您授予我们一项免费的使用权，以在法律允许的范围内将您输入输出之内容及反馈用于模型服务优化。

这和 OpenAI、Anthropic、Google Cloud Gemini 的 API 数据政策形成对比：后几者会明确写「默认不使用 API 输入输出训练模型」或类似承诺；Kimi API 公开协议里没有看到等价表述。

所以对 API 开发者来说，保守做法是：**条款没写不会，就不要假设不会。**

## 付费不等于不训练

这次调研里一个容易误解的点是：很多人会默认「我付费了，所以数据应该不会被训练」。但 Kimi 的公开条款不是这样写的。

至少从公开协议看：

- 中文 C 端免费和付费会员都没有明显的数据训练/优化政策差异。
- API 平台是按量付费，但公开条款仍授权用于优化服务。
- 企业级 API 可能可以单独签数据保护条款，但这不属于公开默认承诺。

## 建议怎么做

1. **普通聊天：避免输入隐私、商业文档、私密代码。**
2. **英文 C 端用户：如需退出，按协议邮件联系 `membership@moonshot.ai`。**
3. **API 开发者：敏感数据不要默认走 Kimi API。** 除非你拿到合同级别的「不用于训练/模型优化」承诺。
4. **企业场景：联系销售，把数据使用边界写进合同。**
5. **最高确定性方案：自部署开源权重。** 本地运行可以从根上避免数据外流。

## 参考来源

- 中文版用户协议：`https://www.kimi.com/user/agreement/zh/modelUse?version=v2`
- 英文版 Terms of Service：`https://www.kimi.com/user/agreement/en/modelUse?version=v2`
- 中文版隐私政策：`https://www.kimi.com/user/agreement/userPrivacy?version=v2`
- 英文版 Privacy Policy：`https://www.kimi.com/user/agreement/en/userPrivacy?version=v2`
- API 开放平台服务协议：`https://platform.moonshot.cn/docs/agreement/modeluse`
- API 开放平台隐私政策：`https://platform.moonshot.cn/docs/agreement/userprivacy`

这篇文章只是基于公开条款的技术/条款笔记，不构成法律意见。涉及公司代码、客户数据、隐私数据时，应以合同和法务审查为准。
