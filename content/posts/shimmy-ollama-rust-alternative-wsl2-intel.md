+++
title = "Shimmy：Ollama 的 Rust 替代方案实测（WSL2 + Intel 集显）"
date = 2026-06-01T00:00:00+08:00
slug = "shimmy-ollama-rust-alternative-wsl2-intel"
tags = ["Shimmy", "Ollama", "LLM", "Rust", "WSL2", "本地推理"]
+++

想找一个比 Ollama 更轻量的本地 LLM 推理服务器？**Shimmy** 用 Rust 写成，单二进制文件，100% OpenAI API 兼容，零配置启动。本文基于 WSL2 + Intel 集显环境的实测，记录了踩坑过程和问题根因。

> 本文是「本地 LLM 推理环境」系列第一篇。[系列第二篇：WSL2 + Intel 集显跑 LLM 推理的分层诊断 →](/posts/wsl2-intel-gpu-llm-inference-diagnosis/)

## Shimmy 是什么

一句话：**Ollama 的 Rust 平替**——更轻、更快、零依赖。

| 维度 | Shimmy | Ollama |
|------|--------|--------|
| 语言 | Rust | Go |
| 依赖 | 单二进制，无额外依赖 | 需要 llama.cpp 动态库 |
| 许可 | MIT | 非商用限制 |
| GPU 支持 | CUDA / Vulkan / OpenCL / MLX | CUDA / Metal |
| 模型格式 | GGUF + SafeTensors | GGUF |
| API 兼容 | OpenAI 100% | OpenAI + 自有 API |
| 端口分配 | 自动（默认 11435） | 固定（11434） |
| 响应缓存 | LRU + TTL，20-40% 提升 | 无 |

项目地址：https://github.com/Michael-A-Kuykendall/shimmy

## 快速开始

```bash
# Linux x86_64
curl -L https://github.com/Michael-A-Kuykendall/shimmy/releases/latest/download/shimmy-linux-x86_64 -o shimmy && chmod +x shimmy

# macOS ARM64 (含 MLX for Apple Silicon)
curl -L https://github.com/Michael-A-Kuykendall/shimmy/releases/latest/download/shimmy-macos-arm64 -o shimmy && chmod +x shimmy

# Windows x64 (含 CUDA + Vulkan + OpenCL)
curl -L https://github.com/Michael-A-Kuykendall/shimmy/releases/latest/download/shimmy-windows-x86_64.exe -o shimmy.exe

# 启动
./shimmy serve --gpu-backend auto
```

零配置：自动从 HuggingFace 缓存、Ollama 本地目录发现模型。热切换模型无需重启。

启动后即提供 OpenAI 兼容的 `/v1/chat/completions` 接口，现有 OpenAI 工具无需改动即可接入：

```bash
curl http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"your-model","messages":[{"role":"user","content":"hello"}]}'
```

## 技术架构

- **Rust + Tokio**：内存安全，异步高性能
- **llama.cpp 后端**：行业标准 GGUF 推理
- **GPU 后端优先级**：CUDA → Vulkan → OpenCL → MLX → CPU (fallback)
- **动态端口管理**：零冲突，自动分配

## 实测：WSL2 + Intel 集显

### 测试环境

| 项目 | 值 |
|------|-----|
| **CPU** | Intel Core Ultra 7 255H (12 核心) |
| **内存** | 19GB |
| **GPU** | Intel Arc 140T (Arrow Lake H) |
| **环境** | WSL2 (Linux 6.6.87) |
| **Vulkan** | ✅ 库已安装 (`libvulkan_intel.so`) |
| **Shimmy** | v1.9.0 (源码编译，启用 `llama-vulkan` feature) |

### 测试 1: Qwen3.5-0.8B GGUF — ❌ 无法运行

```
llama_model_load: error loading model: unknown model architecture: 'qwen35'
```

原因：Shimmy v1.9.0 内置的 llama.cpp **尚未支持 Qwen3.5 架构**。Qwen3.5 使用混合 SSM (Mamba) + Transformer 架构，需要更新版本的 llama.cpp。

### 测试 2: Qwen2.5 SafeTensors — ⚠️ 可加载，推理未完成

SafeTensors 模型可以成功加载，但 Shimmy 报告 "Full transformer inference coming soon!"，推理支持仍在开发中。

### GPU 后端实测

| 后端 | 状态 | 说明 |
|------|------|------|
| **CUDA** | ❌ 无 NVIDIA GPU | 不适用 |
| **Vulkan** | ⚠️ 可初始化但无真实 GPU | WSL2 中只有 `llvmpipe` 软件渲染器 |
| **OpenCL** | ❌ 未编译 | 可通过 `--features llama-opencl` 启用 |
| **MLX** | ❌ macOS only | 不适用 |

**关键发现**：`llvmpipe` 是 Mesa 的 CPU 软件渲染器，用 CPU 多线程模拟 Vulkan GPU。用 `--gpu-backend vulkan` 实际还是 CPU 做矩阵运算，可能反而更慢。

```
Device: llvmpipe (LLVM 20.1.2, 256 bits)
Type: CPU  ← 不是真正的 GPU！
Vendor ID: 0x10005 (Mesa software renderer)
```

## 问题根因

无法运行不是 Shimmy 的问题，而是 **WSL2 + Intel 集显的环境限制**：

1. **WSL2 DXG 内核模块与 Intel GPU 驱动不兼容** — dmesg 持续报 ioctl 失败
2. **Intel GPU 驱动版本偏旧** — 当前 32.0.101.6554，最新 32.0.101.8801（2026-05-15）
3. **Windows Insider Preview Canary 频道** — 26200 预发布版，兼容性不稳定

### 后续方向

| 优先级 | 方案 |
|--------|------|
| 1 | 更新 Intel GPU 驱动到最新版 |
| 2 | `wsl --update` 更新 WSL2 |
| 3 | 退出 Insider Preview，切回稳定版 |
| 4 | 尝试 Level Zero 路径绕过 OpenCL DXG 问题 |

## 谁适合用 Shimmy？

- ✅ **CUDA 环境**（NVIDIA GPU）：开箱即用，性能最佳
- ✅ **macOS Apple Silicon**：MLX 后端原生支持
- ✅ **需要 OpenAI API 兼容**的现有工具链
- ⚠️ **WSL2 + Intel/AMD 集显**：Vulkan 后端受限，建议等驱动更新
- ❌ **纯 CPU 推理追求极致性能**：Ollama 可能更成熟

## 参考链接

- [Shimmy GitHub](https://github.com/Michael-A-Kuykendall/shimmy)
- [Shimmy Crates.io](https://crates.io/crates/shimmy)
- [Intel Arc Graphics 驱动下载](https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html)
