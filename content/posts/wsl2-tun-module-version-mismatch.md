+++
title = "WSL2 TUN 模块版本脱节：排查与修复"
date = 2026-08-10
description = "WSL2 中 modprobe tun 报 Exec format error 的排查与修复——根因是内核与模块版本脱节（vermagic 不匹配）"
[taxonomies]
tags = ["WSL2", "Linux", "内核模块", "排查"]
+++

# WSL2 TUN 模块版本脱节：排查与修复

## 问题

WSL2 中 `modprobe tun` 报错：

```
modprobe: ERROR: could not insert 'tun': Exec format error
```

如果你也遇到这个错误，本文的解决方案和排查思路都适用于你。

## 快速解决

从新版 WSL 包提取 modules.vhd，替换系统目录的旧版：

```powershell
# Windows 侧（管理员）
# 1. 备份旧版
Copy-Item "C:\Program Files\WSL\tools\modules.vhd" "C:\Users\<user>\Downloads\modules.vhd.bak"

# 2. 从新版 WSL 包提取 modules.vhd（需先解包 msixbundle → msi → 提取）
# 3. 替换
Copy-Item "new-modules.vhd" "C:\Program Files\WSL\tools\modules.vhd" -Force

# 4. 重启 WSL
wsl --shutdown
```

```bash
# WSL 内验证
sudo modprobe tun && echo "MODULE LOAD OK"
```

## 根因

**WSL2 内核与模块版本脱节**：

| 组件 | 版本 | 说明 |
|------|------|------|
| 内核 (kernel) | `6.18.33.2` | 手动更新 |
| modules.vhd（模块包） | `6.6.87.2` | **漏换，旧版** |

之前更新 WSL2 内核时只替换了 `kernel` 和 `system.vhd`，**漏换了 `modules.vhd`**。内核是新版，但 tun.ko 的 vermagic 还是旧版（6.6.87.2），内核拒绝加载——这就是 `Exec format error` 的真正原因。

## 排查链

```
modprobe tun → Exec format error
  ↓
CONFIG_TUN=m → 内核支持 TUN，不是"内核限制"
  ↓
modinfo tun.ko → vermagic: 6.6.87.2
uname -r      → 6.18.33.2
  ↓ 版本不一致 → vermagic 不匹配
  ↓
追溯操作记录：只换了 kernel + system.vhd，漏了 modules.vhd
```

**关键洞察**：`Exec format error` 在内核模块场景 ≠ 文件损坏，是 **vermagic 不匹配**（内核拒绝加载版本不对的 .ko 文件）。

## Exec format error 排查框架

遇到 `modprobe` 报 `Exec format error` 时，按顺序排除：

| 排查门 | 检查方法 | 根因 |
|--------|---------|------|
| ① vermagic 版本号 | `modinfo xxx.ko \| grep vermagic` vs `uname -r` | 内核/模块版本不一致（本案） |
| ② vermagic 后缀 | 比较完整 vermagic 字符串（如 `-tegra` 后缀） | CONFIG_LOCALVERSION 不一致 |
| ③ 编译源码版本 | `git log` vs `uname -r` 对应版本 | 用了错误版本的源码编译模块 |
| ④ GCC 版本 | `gcc --version` vs 内核编译 GCC | 多 GCC 共存导致 vermagic 差异 |
| ⑤ 符号表 | `dmesg \| grep "disagrees about version"` | 内核 ABI 变了，模块需重新编译 |
| ⑥ depmod | `sudo depmod -a` 后重试 | 手动安装模块后没更新依赖索引 |

## WSL2 模块加载机制

WSL2 6.6+ 内核模块的分发方式：

- 模块打包在 `modules.vhd`（Windows 侧文件）
- 启动时挂载为 overlay 的 **lower 层**（只读），路径 `/modules`
- `/usr/lib/modules/<ver>/` 是 overlay 合并视图：

```
overlay → lower = /modules（modules.vhd，只读）
          upper = /lib/modules/.../rw/upper（可写，跨重启保留）
```

## 排查教训

这次排查主要卡在「Exec format error = 文件损坏」的错误假设上，绕了不少弯路。如果一开始就查 vermagic，能节省大量时间。

1. **Exec format error = vermagic 不匹配**，不是"文件损坏"或"内核不支持"
2. **WSL2 内核更新必须换三个文件**：kernel + system.vhd + **modules.vhd**
3. **确认"内核不支持"假设时先查 CONFIG_TUN**：`grep CONFIG_TUN /boot/config-$(uname -r)`，`CONFIG_TUN=m` 表示内核支持，只是模块未加载
