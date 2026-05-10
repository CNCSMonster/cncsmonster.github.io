+++
title = "WSL2 GPU 故障：诊断 5 分钟，踩坑 4 小时"
date = 2026-05-10T00:00:00+08:00
tags = ["WSL2", "GPU", "调试", "诊断"]
+++

WSL2 里用 Intel 集显跑 llama.cpp，遇到 `IGC: Internal Compiler Error`。这个错误带我绕了四个小时，最后发现答案在开机第 5 秒的 `dmesg` 里就已经在了。

文章不是讲怎么修 GPU，是讲那四个小时和五分钟之间的差距到底是什么。

## 一张图：WSL2 的 GPU 栈

任何 WSL2 里的 GPU 问题，硬件往上数四层：

```
你的代码 (llama.cpp)
  ↓
[3] IGC — 编译 OpenCL 内核，提交给 GPU
  ↓
[2] OpenCL ICD — GPU API 适配层
  ↓
[1] WSL2 DXG 内核模块 (/dev/dxg) — 和 Windows 驱动通信
  ↓
[0] Windows GPU 驱动 — 真正管硬件的
  ↓
  物理 GPU
```

每层出问题的表现完全不同，但报错信息**永远只会出现在崩溃的那一层**。Layer 1 坏了，Layer 3 报错。崩溃点往下追才是故障点。

## IGC 没坏

llama.cpp 加载 OpenCL 内核时报：

```
IGC: Internal Compiler Error: Segmentation violation
```

IGC（Intel Graphics Compiler）做两件事：编译 GPU 代码，然后把编译好的程序提交到 GPU。编译是纯 CPU 运算，几乎不可能 segfault。**提交**这个动作要穿越 Layer 2、Layer 1、Layer 0 三层才能触达硬件。

追一层看看 Layer 2：OpenCL 能正常枚举 GPU 设备 — `Intel(R) Graphics [0x7d51]`，适配层没坏。

再追一层：`dmesg | grep dxg | grep failed`。

```
[    5.456342] dxgkio_query_adapter_info: Ioctl failed: -22
[    5.460880] dxgkio_query_adapter_info: Ioctl failed: -22
[78509.821263] dxgkio_query_adapter_info: Ioctl failed: -22
[78509.825964] dxgkio_reserve_gpu_va:     Ioctl failed: -75
[78536.966245] dxgkio_is_feature_enabled:  Ioctl failed: -22
```

104 条。从开机第 5 秒就开始了。

`-22` 是 `EINVAL` — WSL2 内核的 DXG 模块传了一些参数，Windows 侧的 GPU 驱动不理解。`-75` 是 `EOVERFLOW` — GPU 虚拟地址溢出。

IGC 提交 GPU 程序时调的是这一层。这就是为什么 IGC 崩溃。

## 根因在 Layer 0

Windows 侧的 GPU 是 **Intel Arc 140T**（16GB），Arrow Lake H 架构，2024 年底发布。驱动版本 `32.0.101.6554`，日期 2025-01-15 — Arrow Lake 发布后两个月的早期驱动。

WSL2 内核的 DXG 模块向这个驱动发 ioctl，驱动不理解。不是驱动坏了，是这个驱动版本还没适配好 WSL2 的 DXG 接口。

**也就是说：IGC 没问题，OpenCL ICD 没问题，WSL2 内核没问题。问题是一个新 GPU 的早期 Windows 驱动和 WSL2 DXG 之间的兼容性。更新 Windows 驱动是最直接的修复路径。**

## 为什么踩了四个小时

第一次看到 `IGC segfault` 时，直觉是"IGC 有问题"。于是查 IGC 版本、看是不是已知 bug、翻 Reddit — IGC 是最新版，没有已知问题。换个方向，测试了 Vulkan（WSL2 不支持原生 Vulkan 透传，只有 CPU 软件渲染器）、DirectML（Windows 专属）和 Shimmy（底层还是同一个 llama.cpp，顺便发现它不支持 Qwen3.5 架构，完全无关的变量）。

四个小时花在了**往上追和往旁边追**。往下只需要一个命令，五分钟。

这引出一个问题：为什么"往崩溃点的下一层追"不是默认反应？

一个可能的解释：崩溃日志格式天然引导你关注崩溃的那一层。`IGC: Internal Compiler Error` — IGC 的名字在错误信息里，你的注意力就被钉在 IGC 上。但实际上，任何一个组件在**调用外部**时崩溃，根因几乎总是在被调的那一层。纯内部计算崩了才是自己的问题。

## 这之后

还没有执行修复。后续计划是：

1. 更新 Windows Intel GPU 驱动 → `wsl --shutdown` → 重跑 `dmesg | grep dxg`。如果 ioctl 错误消失，回测 llama.cpp OpenCL。
2. 如果还不行，试 Level Zero（`intel-level-zero-gpu`）。同样是过 `/dev/dxg`，但走不同的 ioctl 路径，可能绕过 OpenCL 依赖的那几个失败调用。
3. 如果也不行，就停。Arrow Lake + WSL2 的组合当前不成熟，等驱动和内核更新。不要继续花时间在升级 IGC、重装 OpenCL、换发行版上 — 这些不碰 Layer 1。

有人用相同硬件（Core Ultra 7 255H / Arc 140T + WSL2）跑过 GPU 推理吗？知道哪些 Windows 驱动版本能正常过 DXG 的，欢迎告诉我。
