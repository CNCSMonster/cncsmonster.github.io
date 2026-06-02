+++
title = "WSL2 + Intel 集显跑 LLM 推理：为什么不行？分层诊断全记录"
date = 2026-06-01T00:00:00+08:00
slug = "wsl2-intel-gpu-llm-inference-diagnosis"
tags = ["WSL2", "Intel GPU", "LLM", "推理", "OpenCL", "DXG", "故障排查"]
+++

在 [上一篇](/posts/shimmy-ollama-rust-alternative-wsl2-intel/) 中，Shimmy 在 WSL2 + Intel 集显环境下无法运行。本文深入拆解这个问题的根因——不是 Shimmy 的锅，也不是 llama.cpp 的锅，而是 **WSL2 的 DXG 内核模块与 Intel GPU 驱动在协议层就不兼容**。

> 本文是「本地 LLM 推理环境」系列第二篇。

## 核心结论

WSL2 中 Intel 集成显卡**无法用于 LLM 推理**。问题不在 IGC 或 OpenCL 驱动本身，而是 WSL2 DXG 内核模块与 Intel Arc 140T 的 Windows 驱动不兼容。

## WSL2 的 GPU 栈长什么样

从硬件往上 4 层：

```
Python (llama-cpp-python, OpenCL)
         ↓
[3] IGC — Intel Graphics Compiler
         ↓
[2] OpenCL ICD (intel-opencl-icd)
         ↓
[1] WSL2 DXG 内核模块 (/dev/dxg)
         ↓
[0] Windows Intel GPU 驱动
         ↓
     物理 GPU (Intel Arc 140T / Arrow Lake H)
```

### 各层诊断结果

| 层 | 组件 | 状态 | 证据 |
|----|------|------|------|
| [0] | Windows 驱动 (32.0.101.6554) | ⚠️ **偏旧** | 2025-01-15，Intel 在 1~5 月发布了大量 Arrow Lake 更新 |
| [1] | WSL2 DXG (kernel 6.6.87.2) | 🔴 **大量 ioctl 失败** | dmesg 从开机 5 秒起持续报错 |
| [2] | OpenCL ICD (23.43.27642.40) | ✅ 能枚举 GPU | `clGetDeviceIDs` 成功返回 Intel Graphics |
| [3] | IGC (1.0.15468.25) | ✅ 库完整 | 编译正常，但提交内核需过 DXG 层 → 崩溃 |

**Layer 1 是真正的故障点。**

## dmesg 里的铁证

`dmesg` 从头到尾充斥 DXG ioctl 错误，**不是运行 llama.cpp 才触发**：

```
[    5.459659] misc dxg: dxgkio_query_adapter_info: Ioctl failed: -22  (EINVAL)
[    5.460357] misc dxg: dxgkio_query_adapter_info: Ioctl failed: -2   (ENOENT)
[    5.460880] misc dxg: dxgkio_query_adapter_info: Ioctl failed: -22
...
[78509.821263] misc dxg: dxgkio_query_adapter_info: Ioctl failed: -22
[78509.825964] misc dxg: dxgkio_reserve_gpu_va:     Ioctl failed: -75  (EOVERFLOW)
```

错误码含义：

| errno | 宏 | 含义 |
|-------|-----|------|
| -2 | ENOENT | 适配器不存在 |
| -22 | EINVAL | 参数无效（WSL2 DXG 传了 Windows 驱动不理解的参数） |
| -75 | EOVERFLOW | GPU 虚拟地址预留溢出 |

**WSL2 内核的 dxg 模块和 Windows 侧的 Intel GPU 驱动在协议层面不兼容。**

## 根本原因

**Intel Arc 140T 属于 Arrow Lake H 架构，2024 年底刚发布。** Windows 驱动 `32.0.101.6554`（2025-01-15）是 Arrow Lake 早期版本，对 WSL2 的 DXG 接口支持不完整。DXG 模块向 Windows 驱动发出请求时，驱动不理解或处理有 bug，导致 ioctl 返回 EINVAL/EOVERFLOW。

## 五种方案实测对比

| 方案 | GPU 识别 | 推理 | 推荐度 | 备注 |
|------|---------|------|--------|------|
| Vulkan (WSL2) | ❌ 只有 llvmpipe | fallback CPU | ⭐ | Mesa 需要原生 `/dev/dri` |
| OpenCL (WSL2) | ✅ 枚举成功 | ❌ DXG ioctl 崩溃 | ⭐ | 更新驱动后再试 |
| SYCL (WSL2) | ❌ 已确认不可行 | 需手动 patch ABI | ⭐ | 社区已放弃 |
| **Windows Ollama** | ✅ | ✅ 开箱即用 | ⭐⭐⭐ | **当前唯一可用方案** |
| **IPEX-LLM (Win)** | ✅ | ✅ 17-18 t/s | ⭐⭐⭐ | Lunar Lake 已验证 |

### 各方案详情

**Vulkan (WSL2)**：`/dev/dri` 设备不存在，Mesa Intel Vulkan ICD 无法初始化。强制指定后 GPU 数量为 0。

**OpenCL (WSL2)**：GPU 能被正确识别（`Intel(R) Graphics [0x7d51]`），但提交计算内核时 IGC 编译崩溃——根源在 DXG 层。

**SYCL (WSL2)**：Reddit r/IntelArc 用户 2026-04 确认，WSL2 无法通过标准 Intel SYCL 运行时识别 Intel GPU。社区一致建议改用 Windows 原生。

**Windows Ollama**：Windows 版原生支持 Intel GPU，WSL2 通过 HTTP API 调用即可。**实测验证通过，开箱即用。**

**IPEX-LLM (Windows 原生)**：r/IntelArc 用户通过替换 IPEX-LLM 内置 Ollama 二进制，在 Lunar Lake Arc 140V 上实现 qwen3:8b 达到 17-18 tokens/s，100% GPU 占用。

## 可行的后续方向

| 优先级 | 方案 | 操作 |
|--------|------|------|
| 1 | 🔑 更新 Windows Intel GPU 驱动 | 下载最新版（当前 6554 → 最新 8801） |
| 2 | 更新 WSL2 | `wsl --update` |
| 3 | 切回 Windows 稳定版 | 退出 Insider Preview Canary |
| 4 | 尝试 Level Zero 路径 | `sudo apt install intel-level-zero-gpu`，走不同 DXG ioctl |

**推荐顺序**：先更新驱动 → 再更新 WSL → 测试效果 → 如仍有问题再切稳定版。

## 参考

- [Intel Arc Graphics 驱动下载](https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html)
- [Microsoft WSL 基本命令](https://learn.microsoft.com/en-us/windows/wsl/basic-commands)
- [Shimmy 项目](https://github.com/Michael-A-Kuykendall/shimmy)
- [上一篇：Shimmy 评测](/posts/shimmy-ollama-rust-alternative-wsl2-intel/)
