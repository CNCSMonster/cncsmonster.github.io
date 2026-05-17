+++
title = "WSL2 GPU Troubleshooting: 5 Minutes to Diagnose, 4 Hours Down the Rabbit Hole"
date = 2026-05-10T00:00:00+08:00
tags = ["WSL2", "GPU", "Debugging", "Troubleshooting"]
+++

Running llama.cpp on an Intel integrated GPU inside WSL2, I hit `IGC: Internal Compiler Error`. That error sent me down a four-hour rabbit hole. Turns out the answer was already sitting in `dmesg` at second five of boot.

This isn't about how to fix a GPU. It's about the gap between four hours and five minutes.

## One Diagram: The WSL2 GPU Stack

For any GPU problem in WSL2, count four layers upwards from the hardware:

```
Your code (llama.cpp)
  ↓
[3] IGC — compiles OpenCL kernels, submits to GPU
  ↓
[2] OpenCL ICD — GPU API adaptation layer
  ↓
[1] WSL2 DXG kernel module (/dev/dxg) — talks to Windows driver
  ↓
[0] Windows GPU driver — actually controls the hardware
  ↓
   Physical GPU
```

Each layer breaks in a different way, but the error message **only ever appears at the layer where things crash**. Layer 1 breaks, Layer 3 reports the error. The crash point is downstream of the fault. The diagnosis goes the other way.

## IGC Wasn't Broken

llama.cpp threw this while loading an OpenCL kernel:

```
IGC: Internal Compiler Error: Segmentation violation
```

IGC (the Intel Graphics Compiler) does two things: compile GPU code, then submit the compiled program to the GPU. Compilation is pure CPU computation — almost impossible to segfault. The **submission** step crosses Layer 2, Layer 1, and Layer 0 to reach hardware.

Let's check one layer down — Layer 2. `clinfo` properly enumerates the GPU: `Intel(R) Graphics [0x7d51]`. The OpenCL adapter layer is fine.

One more layer down. `dmesg | grep dxg | grep failed`:

```
[    5.456342] dxgkio_query_adapter_info: Ioctl failed: -22
[    5.460880] dxgkio_query_adapter_info: Ioctl failed: -22
[78509.821263] dxgkio_query_adapter_info: Ioctl failed: -22
[78509.825964] dxgkio_reserve_gpu_va:     Ioctl failed: -75
[78536.966245] dxgkio_is_feature_enabled:  Ioctl failed: -22
```

104 entries. Starting from second five of boot.

`-22` is `EINVAL` — the WSL2 kernel's DXG module is passing parameters the Windows GPU driver doesn't understand. `-75` is `EOVERFLOW` — GPU virtual address overflow.

When IGC submits a GPU program, it calls through to this layer. That's why IGC crashes.

## Root Cause: Layer 0

The Windows-side GPU is an **Intel Arc 140T** (16 GB), Arrow Lake H architecture, released late 2024. Driver version `32.0.101.6554`, dated 2025-01-15 — an early driver from two months after Arrow Lake's launch.

The WSL2 kernel's DXG module sends ioctls to this driver. The driver doesn't understand them. The driver isn't broken per se — this version simply isn't adapted to WSL2's DXG interface yet.

**Translation: IGC is fine. OpenCL ICD is fine. The WSL2 kernel is fine. The problem is compatibility between a new GPU's early Windows driver and the WSL2 DXG module. Updating the Windows driver is the most direct fix.**

## Why Four Hours

The first time you see `IGC segfault`, intuition says "IGC is the problem." So you check IGC versions, look for known bugs, search Reddit — IGC is the latest, no known issues. Shift direction. Test Vulkan (WSL2 doesn't support native Vulkan passthrough — only CPU software renderer). Test DirectML (Windows-only). Test Shimmy (same llama.cpp backend — and unrelated: it doesn't support the Qwen3.5 architecture).

Four hours went into **tracing upward and sideways**. Downward takes one command, five minutes.

Why isn't "check the layer below the crash" the default reaction?

One explanation: crash log formatting naturally draws your attention to the crashing layer. `IGC: Internal Compiler Error` — IGC's name is in the error message. Your attention gets pinned there. But when any component crashes **while calling into an external layer**, the root cause is almost always in the layer being called. Self-contained computation failures are your own problem. Calling failures are theirs.

## After This

No fix has been applied yet. The plan forward:

1. Update the Windows Intel GPU driver → `wsl --shutdown` → rerun `dmesg | grep dxg`. If the ioctl errors disappear, retest llama.cpp with OpenCL.
2. If that doesn't help, try Level Zero (`intel-level-zero-gpu`). It also goes through `/dev/dxg`, but takes different ioctl paths — may bypass the failing OpenCL-dependent calls.
3. If neither works, stop. Arrow Lake + WSL2 is not mature yet. Wait for driver and kernel updates. Don't waste more time on IGC upgrades, OpenCL reinstalls, or distro changes — none of those touch Layer 1.

If anyone has run GPU inference on similar hardware (Core Ultra 7 255H / Arc 140T + WSL2) and knows which Windows driver versions pass DXG cleanly, I'd love to hear about it.
