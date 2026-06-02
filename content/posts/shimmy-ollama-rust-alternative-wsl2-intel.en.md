+++
title = "Shimmy: An Ollama Alternative in Rust — Tested on WSL2 + Intel GPU"
date = 2026-06-01T00:00:00+08:00
slug = "shimmy-ollama-rust-alternative-wsl2-intel-en"
tags = ["Shimmy", "Ollama", "LLM", "Rust", "WSL2", "Local Inference"]
+++

Looking for a lighter local LLM inference server than Ollama? **Shimmy** is written in Rust, ships as a single binary, offers 100% OpenAI API compatibility, and runs with zero configuration. This post covers what it is, how it compares to Ollama, and what happened when I tested it on WSL2 with Intel integrated graphics.

> This is Part 1 of a "Local LLM Inference Environment" series. [Part 2: Why Intel GPU Can't Run LLM Inference in WSL2 →](/posts/wsl2-intel-gpu-llm-inference-diagnosis-en/)

## What is Shimmy

One line: **a Rust drop-in replacement for Ollama** — lighter, faster, zero dependencies.

| Dimension | Shimmy | Ollama |
|-----------|--------|--------|
| Language | Rust | Go |
| Dependencies | Single binary, none | Requires llama.cpp dynamic libs |
| License | MIT | Non-commercial restrictions |
| GPU support | CUDA / Vulkan / OpenCL / MLX | CUDA / Metal |
| Model formats | GGUF + SafeTensors | GGUF |
| API compatibility | OpenAI 100% | OpenAI + custom API |
| Port allocation | Auto (default 11435) | Fixed (11434) |
| Response caching | LRU + TTL, 20-40% speedup | None |

Project: https://github.com/Michael-A-Kuykendall/shimmy

## Quick Start

```bash
# Linux x86_64
curl -L https://github.com/Michael-A-Kuykendall/shimmy/releases/latest/download/shimmy-linux-x86_64 -o shimmy && chmod +x shimmy

# macOS ARM64 (with MLX for Apple Silicon)
curl -L https://github.com/Michael-A-Kuykendall/shimmy/releases/latest/download/shimmy-macos-arm64 -o shimmy && chmod +x shimmy

# Windows x64 (with CUDA + Vulkan + OpenCL)
curl -L https://github.com/Michael-A-Kuykendall/shimmy/releases/latest/download/shimmy-windows-x86_64.exe -o shimmy.exe

# Start
./shimmy serve --gpu-backend auto
```

Zero config: auto-discovers models from HuggingFace cache, Ollama local directories. Hot-swap models without restarting.

Once running, it exposes an OpenAI-compatible `/v1/chat/completions` endpoint — existing OpenAI tools work with zero code changes:

```bash
curl http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"your-model","messages":[{"role":"user","content":"hello"}]}'
```

## Architecture

- **Rust + Tokio**: Memory-safe, async high performance
- **llama.cpp backend**: Industry-standard GGUF inference
- **GPU backend priority**: CUDA → Vulkan → OpenCL → MLX → CPU (fallback)
- **Dynamic port management**: Zero conflicts, auto-assign

## Real-World Test: WSL2 + Intel GPU

### Test Environment

| Item | Value |
|------|-------|
| **CPU** | Intel Core Ultra 7 255H (12 cores) |
| **RAM** | 19GB |
| **GPU** | Intel Arc 140T (Arrow Lake H) |
| **Env** | WSL2 (Linux 6.6.87) |
| **Vulkan** | ✅ Library installed (`libvulkan_intel.so`) |
| **Shimmy** | v1.9.0 (built from source with `llama-vulkan` feature) |

### Test 1: Qwen3.5-0.8B GGUF — ❌ Failed

```
llama_model_load: error loading model: unknown model architecture: 'qwen35'
```

Shimmy v1.9.0 bundles a llama.cpp version that **doesn't support Qwen3.5 yet**. Qwen3.5 uses a hybrid SSM (Mamba) + Transformer architecture requiring a newer llama.cpp.

### Test 2: Qwen2.5 SafeTensors — ⚠️ Loads, no inference

SafeTensors models load successfully, but Shimmy reports "Full transformer inference coming soon!" — inference support is still in development.

### GPU Backend Results

| Backend | Status | Notes |
|---------|--------|-------|
| **CUDA** | ❌ No NVIDIA GPU | N/A |
| **Vulkan** | ⚠️ Initializes but no real GPU | WSL2 only exposes `llvmpipe` software renderer |
| **OpenCL** | ❌ Not compiled | Enable with `--features llama-opencl` |
| **MLX** | ❌ macOS only | N/A |

**Key finding**: `llvmpipe` is Mesa's CPU software renderer — it simulates Vulkan GPU using CPU multithreading. Using `--gpu-backend vulkan` still runs matrix ops on CPU, potentially slower than pure CPU mode due to Vulkan overhead.

```
Device: llvmpipe (LLVM 20.1.2, 256 bits)
Type: CPU  ← Not a real GPU!
Vendor ID: 0x10005 (Mesa software renderer)
```

## Root Cause

The failure isn't Shimmy's fault — it's a **WSL2 + Intel GPU environment limitation**:

1. **WSL2 DXG kernel module incompatible with Intel GPU driver** — dmesg shows persistent ioctl failures
2. **Intel GPU driver outdated** — current 32.0.101.6554, latest 32.0.101.8801 (2026-05-15)
3. **Windows Insider Preview Canary** — build 26200 is pre-release, unstable compatibility

### Next Steps

| Priority | Action |
|----------|--------|
| 1 | Update Intel GPU driver to latest |
| 2 | `wsl --update` |
| 3 | Exit Insider Preview, return to stable |
| 4 | Try Level Zero backend to bypass OpenCL DXG issues |

## Who Should Use Shimmy?

- ✅ **CUDA environment** (NVIDIA GPU): Works out of the box, best performance
- ✅ **macOS Apple Silicon**: MLX backend native support
- ✅ **Existing toolchains needing OpenAI API compatibility**
- ⚠️ **WSL2 + Intel/AMD integrated GPU**: Vulkan backend limited, wait for driver updates
- ❌ **Pure CPU inference追求极致性能**: Ollama may be more mature

## References

- [Shimmy GitHub](https://github.com/Michael-A-Kuykendall/shimmy)
- [Shimmy Crates.io](https://crates.io/crates/shimmy)
- [Intel Arc Graphics Driver Download](https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html)
