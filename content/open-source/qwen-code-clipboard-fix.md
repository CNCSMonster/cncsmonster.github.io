+++
title = 'Qwen Code PR #4647：修复 Linux/WSL2 剪贴板图片粘贴'
date = 2026-06-08T03:05:08+08:00
tags = ['开源贡献', 'Qwen Code', 'Linux', 'WSL2']
weight = 5
+++

## 贡献概述

向 [Qwen Code](https://github.com/QwenLM/qwen-code) 提交 PR #4647，修复 Linux/WSL2 环境下剪贴板图片粘贴失败的问题。

**问题**：WSL2 + WSLg（Wayland）环境中，`@teddyzhu/clipboard` 原生模块使用 X11 协议访问剪贴板，无法读取图片，导致粘贴无响应。

**方案**：用平台原生工具（`wl-paste`/`xclip`）替换 Linux 上的原生模块，并处理 Windows 剪贴板暴露的 `image/bmp` 格式。

**状态**：✅ 已合并（2026-06-08）

## 核心改动

### 1. Wayland/X11 双后端支持

- **Wayland**：`wl-paste --list-types` 检测图片类型，`wl-paste --type image/png` 保存
- **X11**：`xclip -selection clipboard -t TARGETS -o` 检测，`xclip -selection clipboard -t image/png -o` 保存
- 自动根据 `WAYLAND_DISPLAY` / `DISPLAY` 环境变量选择后端

### 2. BMP 转 PNG

Windows 剪贴板通过 WSL2 暴露为 `image/bmp`，需要 Python PIL 转换为 PNG：

```typescript
// 保存 BMP → 调用 python3 PIL 转换 → 返回 PNG 路径
const bmpPath = tempFilePath.replace('.png', '.bmp');
await saveFromCommand('wl-paste', ['--type', 'image/bmp'], bmpPath);
// python3 -c "from PIL import Image; Image.open(bmp).save(png)"
```

### 3. 安全加固

- **Symlink 攻击防护**：`fs.open(filePath, 'wx')` 使用 `O_EXCL`，防止预置 symlink 覆盖任意文件
- **命令注入防护**：Python 脚本通过 `sys.argv` 传参，避免字符串插值
- **超时机制**：所有 `spawn()` 调用增加 5 秒超时，防止挂死

### 4. 测试覆盖

新增 19 个测试，覆盖：
- 后端自动检测（Wayland/X11/无）
- 图片检测路径
- 保存错误路径（超时、spawn 失败、stdout 错误）
- 清理逻辑（BMP 临时文件、空文件）

## 技术栈

- Node.js / TypeScript
- `wl-clipboard`（Wayland）/ `xclip`（X11）
- Python 3 + Pillow（BMP 转换）
- Vitest（测试）

## 项目链接

- **PR**：[#4647](https://github.com/QwenLM/qwen-code/pull/4647)
- **Issue**：[#3517](https://github.com/QwenLM/qwen-code/issues/3517)、[#2885](https://github.com/QwenLM/qwen-code/issues/2885)
