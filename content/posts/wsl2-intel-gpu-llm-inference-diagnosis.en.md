+++
title = "Why Intel GPU Can't Run LLM Inference in WSL2: A Layer-by-Layer Diagnosis"
date = 2026-06-01T00:00:00+08:00
slug = "wsl2-intel-gpu-llm-inference-diagnosis-en"
tags = ["WSL2", "Intel GPU", "LLM", "Inference", "OpenCL", "DXG", "Debugging"]
+++

In [the previous post](/posts/shimmy-ollama-rust-alternative-wsl2-intel-en/), Shimmy failed to run on WSL2 with Intel integrated graphics. This post digs into why — it's not Shimmy's fault, not llama.cpp's fault, but a fundamental **incompatibility between WSL2's DXG kernel module and the Intel GPU driver at the protocol level**.

> Part 2 of the "Local LLM Inference Environment" series.

## Core Finding

Intel integrated graphics **cannot be used for LLM inference in WSL2**. The issue isn't in IGC or OpenCL drivers — it's WSL2's DXG kernel module failing to communicate with the Intel Arc 140T Windows driver.

## WSL2 GPU Stack

Four layers from hardware to Python:

```
Python (llama-cpp-python, OpenCL)
         ↓
[3] IGC — Intel Graphics Compiler
         ↓
[2] OpenCL ICD (intel-opencl-icd)
         ↓
[1] WSL2 DXG kernel module (/dev/dxg)
         ↓
[0] Windows Intel GPU driver
         ↓
     Physical GPU (Intel Arc 140T / Arrow Lake H)
```

### Per-Layer Diagnosis

| Layer | Component | Status | Evidence |
|-------|-----------|--------|----------|
| [0] | Windows driver (32.0.101.6554) | ⚠️ **Outdated** | 2025-01-15, Intel shipped many Arrow Lake updates since |
| [1] | WSL2 DXG (kernel 6.6.87.2) | 🔴 **Massive ioctl failures** | dmesg errors from 5 seconds after boot |
| [2] | OpenCL ICD (23.43.27642.40) | ✅ Enumerates GPU | `clGetDeviceIDs` returns Intel Graphics |
| [3] | IGC (1.0.15468.25) | ✅ Library intact | Compilation OK, but kernel submission goes through DXG → crash |

**Layer 1 is the real failure point.**

## dmesg Evidence

`dmesg` is flooded with DXG ioctl errors from boot — **not triggered by running llama.cpp**:

```
[    5.459659] misc dxg: dxgkio_query_adapter_info: Ioctl failed: -22  (EINVAL)
[    5.460357] misc dxg: dxgkio_query_adapter_info: Ioctl failed: -2   (ENOENT)
[    5.460880] misc dxg: dxgkio_query_adapter_info: Ioctl failed: -22
...
[78509.821263] misc dxg: dxgkio_query_adapter_info: Ioctl failed: -22
[78509.825964] misc dxg: dxgkio_reserve_gpu_va:     Ioctl failed: -75  (EOVERFLOW)
```

| errno | Meaning |
|-------|---------|
| -2 (ENOENT) | Adapter not found |
| -22 (EINVAL) | Invalid parameter — WSL2 DXG sends params the driver doesn't understand |
| -75 (EOVERFLOW) | GPU virtual address reservation overflow |

**WSL2's dxg module and the Windows Intel GPU driver are incompatible at the protocol level.**

## Root Cause

**Intel Arc 140T is Arrow Lake H architecture, released late 2024.** Windows driver `32.0.101.6554` (2025-01-15) is an early Arrow Lake driver with incomplete WSL2 DXG support. When DXG sends requests, the driver doesn't understand them or has bugs, returning EINVAL/EOVERFLOW.

## Debugging Reflection

The first time you see `IGC segfault`, intuition says "IGC is the problem." So you check IGC versions, look for known bugs, search Reddit — IGC is the latest, no known issues. Shift direction. Test Vulkan (WSL2 doesn't support native Vulkan passthrough). Test DirectML (Windows-only, unusable in WSL2). Test Shimmy (same llama.cpp backend — completely unrelated variable).

Four hours went into **tracing upward and sideways**. Downward takes one command, five minutes.

Crash log formatting naturally draws your attention to the crashing layer. `IGC: Internal Compiler Error` — IGC's name is in the error message, your attention gets pinned there. But when any component crashes **while calling into an external layer**, the root cause is almost always in the layer being called. Self-contained computation failures are your own problem.

## Five Approaches Tested

| Approach | GPU Recognition | Inference | Rating | Notes |
|----------|----------------|-----------|--------|-------|
| Vulkan (WSL2) | ❌ Only llvmpipe | CPU fallback | ⭐ | Mesa needs native `/dev/dri` |
| OpenCL (WSL2) | ✅ Enumerates OK | ❌ DXG ioctl crash | ⭐ | Retry after driver update |
| SYCL (WSL2) | ❌ Confirmed dead | Needs ABI patch | ⭐ | Community has given up |
| **Windows Ollama** | ✅ | ✅ Works out of box | ⭐⭐⭐ | **Only viable option now** |
| **IPEX-LLM (Win)** | ✅ | ✅ 17-18 t/s | ⭐⭐⭐ | Verified on Lunar Lake |

### Details

**Vulkan (WSL2)**: No `/dev/dri` device, Mesa Intel Vulkan ICD can't initialize. GPU count = 0.

**OpenCL (WSL2)**: GPU recognized (`Intel(R) Graphics [0x7d51]`), but IGC crashes on kernel submission — root cause is DXG layer.

**SYCL (WSL2)**: Reddit r/IntelArc users confirmed (2026-04) that WSL2 can't detect Intel GPU via standard SYCL runtime. Community consensus: use Windows native.

**Windows Ollama**: Native Intel GPU support, WSL2 calls via HTTP API. **Verified working, zero config.**

**IPEX-LLM (Windows native)**: Replacing IPEX-LLM's bundled Ollama binary achieved 17-18 tokens/s on Lunar Lake Arc 140V with qwen3:8b at 100% GPU utilization.

## Next Steps

| Priority | Action |
|----------|--------|
| 1 | 🔑 Update Windows Intel GPU driver (6554 → 8801) |
| 2 | Update WSL2: `wsl --update` |
| 3 | Return to stable Windows (exit Insider Preview Canary) |
| 4 | Try Level Zero backend (`sudo apt install intel-level-zero-gpu`) |

## References

- [Intel Arc Graphics Driver Download](https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html)
- [Microsoft WSL Basic Commands](https://learn.microsoft.com/en-us/windows/wsl/basic-commands)
- [Shimmy Project](https://github.com/Michael-A-Kuykendall/shimmy)
- [Previous: Shimmy Review](/posts/shimmy-ollama-rust-alternative-wsl2-intel-en/)
