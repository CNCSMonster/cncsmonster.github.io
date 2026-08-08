+++
title = "离线语音转文字调研：为什么我最终选择了 Handy"
date = 2026-08-08T00:00:00+08:00
slug = "offline-speech-to-text-handy"
[taxonomies]
    tags = ["语音输入", "Speech-to-Text", "Handy", "本地推理", "隐私保护", "Local Inference", "Privacy"]
+++

用语音给 AI 编程助手说话，正在成为越来越自然的交互方式。但"语音转文字"这条链路有个常被忽略的问题：**你的声音数据交给了谁？**

本文调研了跨平台、完全离线的语音转文字方案，最终选择了 [Handy](https://handy.computer)，并记录了完整选型过程和实测数据。

## 为什么语音转文字要跑在本地

本地（离线）语音转文字的价值有两条，互相独立：

1. **隐私** — 声音是生物特征，泄露有被克隆/滥用的现实风险；音频不出设备，风险在源头关闭
2. **性能** — 省去"上传音频 → 云端转写 → 返回文本"的网络往返，push-to-talk 交互场景延迟体感显著

### 声音泄露的风险

**声音是生物特征**（官方定义）：

- [NIST SP 800-63B](https://pages.nist.gov/800-63-4/sp800-63b.html) 将 voice prints 列入生物特征清单
- [EDPB Guidelines 02/2021](https://www.edpb.europa.eu/system/files/2021-03/edpb_guidelines_022021_virtual_voice_assistants_adopted-public-consultation_en.pdf)（第 31 段）："voice data is inherently biometric personal data"

**泄露是已规模化的现实威胁**：

| 事实 | 数据 | 来源 |
|------|------|------|
| 克隆门槛 | 3 秒音频 → 85% 相似度 | McAfee |
| 诈骗规模 | 2025 年深度伪造损失 $16.5 亿 | Surfshark |
| 波及面 | 1/4 美国人遭遇 AI 语音诈骗，77% 受害者损失钱 | Hiya / McAfee |
| 官方确认 | FBI 2025 年首次单列 AI 犯罪类别，损失 $8.93 亿 | FBI IC3 |

**中国案例**：

- [澎湃新闻 2025-02](https://www.thepaper.cn/newsDetail_forward_30204154)：AI 换声仿冒孙子，诈骗老人 2 万元
- [今视频 2026-06](https://news.qq.com/rain/a/20260605A070IM00)：AI 换脸+拟声冒充好友，骗走 430 万元（5-10 秒语音即可提取声纹）
- 中国《个人信息保护法》将声纹列为**敏感个人信息**，与 GDPR 对生物特征的定位一致

**推论**：在线语音转文字服务 = 主动把音频交给不可控的第三方，留存/训练/安全防护全由对方决定。风险路径：

- 克隆冒充（骗过"人"，不需攻破技术系统）
- 进入训练集（难以删除）

## 工具选型：为什么是 Handy

**需求**：跨平台 / 完全离线 / push-to-talk / 终端粘贴兼容 / 中文

**Handy vs 闪电说**（同为本地方案，核心差异在终端适配）：

| 维度 | Handy | 闪电说 |
|------|-------|--------|
| 粘贴方式 | 可配置：Ctrl+V / Ctrl+Shift+V / Shift+Insert | 固定 Ctrl+V |
| 终端兼容 | Windows Terminal 等 ✅ | Ctrl+Shift+V 终端无法输入 ❌ |
| Linux | ✅ | ❌ 无 Linux 版 |
| 模型 | 多模型可切换（Whisper / Parakeet / SenseVoice） | 固定 |

**两个关键点**：

1. **终端粘贴**：Windows Terminal 的粘贴键是 `Ctrl+Shift+V`，不是 `Ctrl+V`。闪电说固定模拟 `Ctrl+V`，在需要 `Ctrl+Shift+V` 的终端里转写文字送不进去；Handy 可配置粘贴方式，是唯一能适配终端的
2. **多模型**：Handy 支持切换多个本地模型，实测中文用 **SenseVoice** 质量最佳，优于 Whisper

**其余候选淘汰**：智谱输入法无 Linux 版；Voisty 付费。

## 实测（2026-05）

> **场景**：push-to-talk 实时语音输入（按一下说话，说完立刻要出文字），实时性是硬指标。
> **硬件基准**：Intel Core Ultra 7 255H（核显 Arc 140T，无独显）。
> 模型切换结论必须绑定机器配置与使用场景——没有这两者，谈"哪个模型更好"没有意义。

| 环境 | 结果 |
|------|------|
| Windows | ✅ 实测：开箱即用，SenseVoice 中文体验最佳 |
| macOS | ✅ 官方支持（Apple Silicon / Intel 均有 .dmg），未实测 |
| Ubuntu (Wayland) | ⚠️ 实测：全局快捷键开箱不可用——Wayland 平台限制（[#1691](https://github.com/cjpais/Handy/issues/1691)、[#140](https://github.com/cjpais/Handy/issues/140)）；用 udev 规则放开 /dev/uinput 权限 + 切 X11 会话可解决，已验证可行 |

**模型结论**（Intel Core Ultra 7 255H + Arc 140T 核显，push-to-talk 场景实测）：

- **SenseVoice 胜出**：体积约 240 MB，**1 分钟语音 3 秒内完成转换**；平时说一句简单指令**秒出**
- 对比 Whisper large v3（体积超过 1 GB）：
  - 中文效果**更好**
  - 中英文混合、纯英文效果**接近**
  - 速度**快得多**

## 边界

- 语音输入适合自然语言意图；**密钥、完整代码不适合语音输入**（精确性差）
- 本地方案防"音频→第三方"这一跳；**不防**本机被攻破录音、物理环境收音
- 转写后的文本仍会发给 AI 模型——本地保护的是音频，不是内容本身

## 参考

- [Handy 官网](https://handy.computer)
- [Handy GitHub](https://github.com/cjpais/Handy)
- [Handy issue #1691（Ubuntu 24.04 全局热键后台不可用，含 workaround）](https://github.com/cjpais/Handy/issues/1691)
- [NIST SP 800-63B](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [EDPB Guidelines 02/2021 关于虚拟语音助手（PDF，第 31 段）](https://www.edpb.europa.eu/system/files/2021-03/edpb_guidelines_022021_virtual_voice_assistants_adopted-public-consultation_en.pdf)
