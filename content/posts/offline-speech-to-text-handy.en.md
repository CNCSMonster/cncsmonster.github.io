+++
title = "Offline Speech-to-Text: Why I Ultimately Chose Handy"
date = 2026-08-08T00:00:00+08:00
slug = "offline-speech-to-text-handy-en"
[taxonomies]
    tags = ["Speech-to-Text", "Voice Input", "Handy", "Local Inference", "Privacy", "Offline"]
+++

Speaking to your AI coding assistant is becoming a natural way to interact. But there's an often-overlooked question in the speech-to-text pipeline: **who gets your voice data?**

This article researches cross-platform, fully offline speech-to-text solutions, explains why I ultimately chose [Handy](https://handy.computer), and documents the complete selection process with real-world measurements.

## Why Speech-to-Text Should Run Locally

Local (offline) speech-to-text provides two independent values:

1. **Privacy** — Your voice is a biometric characteristic, and its exposure carries real risks of cloning and abuse. When audio never leaves the device, the risk is closed at the source.
2. **Performance** — No network round-trip of "upload audio → cloud transcription → return text". For push-to-talk interaction, the latency difference is perceptible.

### The Risk of Voice Exposure

**Voice is a biometric characteristic** (official definitions):

- [NIST SP 800-63B](https://pages.nist.gov/800-63-4/sp800-63b.html) lists voice prints among biometric characteristics
- [EDPB Guidelines 02/2021](https://www.edpb.europa.eu/system/files/2021-03/edpb_guidelines_022021_virtual_voice_assistants_adopted-public-consultation_en.pdf) (para. 31): "voice data is inherently biometric personal data"

**Exposure is a scaled, real-world threat**:

| Fact | Data | Source |
|------|------|--------|
| Cloning threshold | 3 seconds of audio → 85% similarity | McAfee |
| Fraud scale | $1.65B deepfake losses in 2025 | Surfshark |
| Reach | 1 in 4 Americans encountered AI voice scams; 77% of victims lost money | Hiya / McAfee |
| Official recognition | FBI's first AI crime category in 2025, $893M in losses | FBI IC3 |

**Cases in China**:

- [The Paper 2025-02](https://www.thepaper.cn/newsDetail_forward_30204154): AI voice impersonation of a grandson defrauded an elderly person of ¥20,000
- [Jinshipin 2026-06](https://news.qq.com/rain/a/20260605A070IM00): AI face-swap + voice impersonation of a friend, ¥4.3M defrauded (5–10 seconds of audio is enough to extract a voiceprint)
- China's Personal Information Protection Law (PIPL) classifies voiceprints as **sensitive personal information**, consistent with GDPR's treatment of biometrics

**Implication**: An online speech-to-text service means voluntarily handing your audio to an uncontrollable third party, which decides retention, training, and security. Risk paths:

- Cloning and impersonation (deceiving *people*, not technical systems)
- Entering training datasets (nearly impossible to remove)

## Tool Selection: Why Handy

**Requirements**: Cross-platform / fully offline / push-to-talk / terminal paste compatibility / Chinese support

**Handy vs. Shandianshuo** (both local solutions, key difference in terminal adaptation):

| Dimension | Handy | Shandianshuo |
|-----------|-------|--------------|
| Paste method | Configurable: Ctrl+V / Ctrl+Shift+V / Shift+Insert | Fixed Ctrl+V |
| Terminal compatibility | Windows Terminal etc. ✅ | Cannot input in Ctrl+Shift+V terminals ❌ |
| Linux | ✅ | ❌ No Linux version |
| Models | Switchable (Whisper / Parakeet / SenseVoice) | Fixed |

**Two key points**:

1. **Terminal paste**: Windows Terminal's paste shortcut is `Ctrl+Shift+V`, not `Ctrl+V`. Shandianshuo only simulates `Ctrl+V`, so transcribed text cannot be pasted into terminals that require `Ctrl+Shift+V`. Handy lets you configure the paste method — the only one that works in terminals.
2. **Multiple models**: Handy supports switching between several local models. In testing, **SenseVoice** gave the best Chinese quality, better than Whisper.

**Other candidates eliminated**: Zhipu Input Method has no Linux version; Voisty is paid.

## Measurements (2026-05)

> **Scenario**: push-to-talk real-time voice input (press to speak, release to get text immediately), where real-time performance is a hard requirement.
> **Hardware baseline**: Intel Core Ultra 7 255H (Arc 140T iGPU, no discrete GPU).
> Model conclusions must be tied to hardware and use case — without these, "which model is better" is meaningless.

| Environment | Result |
|-------------|--------|
| Windows | ✅ Tested: works out of the box, SenseVoice best for Chinese |
| macOS | ✅ Officially supported (.dmg for Apple Silicon / Intel), not tested |
| Ubuntu (Wayland) | ⚠️ Tested: global hotkey unusable out of the box — a Wayland platform limitation ([#1691](https://github.com/cjpais/Handy/issues/1691), [#140](https://github.com/cjpais/Handy/issues/140)); fixable with a udev rule for /dev/uinput permissions + switching to X11 session, verified working |

**Model conclusion** (Intel Core Ultra 7 255H + Arc 140T iGPU, push-to-talk scenario):

- **SenseVoice wins**: ~240 MB, **converts 1 minute of speech in under 3 seconds**; simple commands appear instantly
- vs. Whisper large v3 (over 1 GB):
  - **Better** Chinese quality
  - **Comparable** for mixed Chinese-English and pure English
  - **Much faster**

## Boundaries

- Voice input suits natural-language intent; **passwords and full code are unsuitable for voice input** (precision issues)
- Local solutions prevent "audio → third party"; they do **not** prevent recording by a compromised machine or physical eavesdropping
- Transcribed text is still sent to the AI model — local processing protects the audio, not the content itself

## References

- [Handy website](https://handy.computer)
- [Handy GitHub](https://github.com/cjpais/Handy)
- [Handy issue #1691 (global hotkey unusable in background on Ubuntu 24.04, with workaround)](https://github.com/cjpais/Handy/issues/1691)
- [NIST SP 800-63B](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [EDPB Guidelines 02/2021 on Virtual Voice Assistants (PDF, para. 31)](https://www.edpb.europa.eu/system/files/2021-03/edpb_guidelines_022021_virtual_voice_assistants_adopted-public-consultation_en.pdf)
