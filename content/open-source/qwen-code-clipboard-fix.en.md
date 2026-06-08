+++
title = 'Qwen Code PR #4647: Fix Linux/WSL2 Clipboard Image Paste'
date = 2026-06-08T03:05:08+08:00
tags = ['Open Source', 'Qwen Code', 'Linux', 'WSL2']
weight = 5
+++

## Contribution Overview

Submitted [PR #4647](https://github.com/QwenLM/qwen-code/pull/4647) to [Qwen Code](https://github.com/QwenLM/qwen-code), fixing clipboard image paste failure on Linux/WSL2.

**Problem**: In WSL2 + WSLg (Wayland) environments, the `@teddyzhu/clipboard` native module uses X11 protocol to access clipboard and cannot read images, causing paste to fail silently.

**Solution**: Replace the native module on Linux with platform-native tools (`wl-paste`/`xclip`), and handle the `image/bmp` format exposed by Windows clipboard.

**Status**: ✅ Merged (2026-06-08)

## Core Changes

### 1. Wayland/X11 Dual Backend Support

- **Wayland**: `wl-paste --list-types` for detection, `wl-paste --type image/png` for saving
- **X11**: `xclip -selection clipboard -t TARGETS -o` for detection, `xclip -selection clipboard -t image/png -o` for saving
- Auto-select backend based on `WAYLAND_DISPLAY` / `DISPLAY` environment variables

### 2. BMP to PNG Conversion

Windows clipboard exposes images as `image/bmp` via WSL2, requiring Python PIL conversion:

```typescript
// Save BMP → call python3 PIL conversion → return PNG path
const bmpPath = tempFilePath.replace('.png', '.bmp');
await saveFromCommand('wl-paste', ['--type', 'image/bmp'], bmpPath);
// python3 -c "from PIL import Image; Image.open(bmp).save(png)"
```

### 3. Security Hardening

- **Symlink attack protection**: `fs.open(filePath, 'wx')` with `O_EXCL` prevents pre-placed symlinks from overwriting arbitrary files
- **Command injection protection**: Python script receives paths via `sys.argv`, avoiding string interpolation
- **Timeout mechanism**: All `spawn()` calls have 5-second timeout to prevent hangs

### 4. Test Coverage

Added 19 tests covering:
- Backend auto-detection (Wayland/X11/none)
- Image detection paths
- Save error paths (timeout, spawn failure, stdout error)
- Cleanup logic (BMP temp files, empty files)

## Tech Stack

- Node.js / TypeScript
- `wl-clipboard` (Wayland) / `xclip` (X11)
- Python 3 + Pillow (BMP conversion)
- Vitest (testing)

## Links

- **PR**: [#4647](https://github.com/QwenLM/qwen-code/pull/4647)
- **Issues**: [#3517](https://github.com/QwenLM/qwen-code/issues/3517), [#2885](https://github.com/QwenLM/qwen-code/issues/2885)
