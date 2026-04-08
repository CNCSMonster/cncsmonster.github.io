+++
title = 'WSL2 网络模式与 localhost 互通'
date = 2026-03-03T00:00:00+08:00
tags = ['WSL', '网络配置', 'localhost', 'mirrored']
+++

## 问题

WSL2 运行在轻量虚拟机中，与 Windows 有独立的网络命名空间。默认 NAT 模式下，WSL 中的 `localhost` 
与 Windows 的 `localhost` 不互通，无法直接访问 Windows 上监听 127.0.0.1 的服务。

## 解决方案对比

| 方案 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| **mirrored 网络模式（推荐）** | `.wslconfig` 设置 `networkingMode=mirrored` | 最简洁，localhost 直接互通 | 可能影响 Docker 网络行为 |
| Ollama/服务绑定 0.0.0.0 | Windows 端服务监听所有网卡 | 不改 WSL 网络模式 | 服务暴露到局域网，有安全隐患 |
| netsh 端口转发 | `netsh interface portproxy` 转发端口 | 不改任何服务配置 | 配置繁琐，WSL 重启后 IP 可能变 |
| 直接调用 Windows exe | WSL 中 alias 到 `xxx.exe` | 零改动 | 非原生 Linux 二进制，路径交互受限 |

## 启用 mirrored 模式

编辑 `%USERPROFILE%\.wslconfig`（即 `C:\Users\用户名\.wslconfig`），在 `[wsl2]` 段添加：

```ini
[wsl2]
networkingMode=mirrored
```

然后重启 WSL：

```powershell
wsl --shutdown
```

重新打开 WSL 终端后，WSL 与 Windows 共享 localhost，可直接访问 Windows 上的服务。

### 前提条件

- Windows 10 22H2+ 或 Windows 11
- WSL 版本 >= 2.0（通过 `wsl --version` 检查）

### 验证

```bash
# 假设 Windows 上有服务监听 127.0.0.1:端口号
curl http://localhost:端口号
```

## 回退方法

如果 mirrored 模式导致 Docker 或其他网络服务异常：

1. 删除 `.wslconfig` 中的 `networkingMode=mirrored`
2. 执行 `wsl --shutdown` 重启 WSL
3. 网络恢复为默认的 NAT 模式
