+++
title = "WSL2 TUN Module Version Mismatch: Diagnosis and Fix"
date = 2026-08-10
description = "Diagnosing and fixing 'Exec format error' when running modprobe tun in WSL2 — the root cause is kernel/module version mismatch (vermagic mismatch)"
[taxonomies]
tags = ["WSL2", "Linux", "Kernel Module", "Troubleshooting"]
+++

# WSL2 TUN Module Version Mismatch: Diagnosis and Fix

## Problem

Running `modprobe tun` in WSL2 fails with:

```
modprobe: ERROR: could not insert 'tun': Exec format error
```

If you're encountering this error, the solution and diagnostic approach in this article apply to you.

## Quick Fix

Extract modules.vhd from a newer WSL package and replace the outdated version in the system directory:

```powershell
# Windows side (Administrator)
# 1. Backup the old version
Copy-Item "C:\Program Files\WSL\tools\modules.vhd" "C:\Users\<user>\Downloads\modules.vhd.bak"

# 2. Extract modules.vhd from the new WSL package (unpack msixbundle → msi → extract)
# 3. Replace
Copy-Item "new-modules.vhd" "C:\Program Files\WSL\tools\modules.vhd" -Force

# 4. Restart WSL
wsl --shutdown
```

```bash
# Verify in WSL
sudo modprobe tun && echo "MODULE LOAD OK"
```

## Root Cause

**WSL2 kernel and module version mismatch**:

| Component | Version | Note |
|------|------|------|
| Kernel (kernel) | `6.18.33.2` | Manually updated |
| modules.vhd (module package) | `6.6.87.2` | **Missed, outdated** |

When updating the WSL2 kernel previously, only `kernel` and `system.vhd` were replaced — **`modules.vhd` was missed**. The kernel is new, but tun.ko's vermagic is still the old version (6.6.87.2), so the kernel refuses to load it — this is the real cause of `Exec format error`.

## Diagnostic Chain

```
modprobe tun → Exec format error
  ↓
CONFIG_TUN=m → Kernel supports TUN, not "kernel limitation"
  ↓
modinfo tun.ko → vermagic: 6.6.87.2
uname -r      → 6.18.33.2
  ↓ Version mismatch → vermagic mismatch
  ↓
Trace operation history: only replaced kernel + system.vhd, missed modules.vhd
```

**Key insight**: In the kernel module context, `Exec format error` ≠ file corruption, it's **vermagic mismatch** (kernel refuses to load a .ko file with the wrong version).

## Exec format Error Diagnostic Framework

When `modprobe` reports `Exec format error`, rule out in order:

| Check | Method | Root Cause |
|--------|---------|------|
| ① vermagic version | `modinfo xxx.ko \| grep vermagic` vs `uname -r` | Kernel/module version mismatch (this case) |
| ② vermagic suffix | Compare full vermagic string (e.g., `-tegra` suffix) | CONFIG_LOCALVERSION mismatch |
| ③ Source version | `git log` vs `uname -r` corresponding version | Wrong source version used to compile module |
| ④ GCC version | `gcc --version` vs kernel build GCC | Multiple GCC versions causing vermagic difference |
| ⑤ Symbol table | `dmesg \| grep "disagrees about version"` | Kernel ABI changed, module needs recompilation |
| ⑥ depmod | `sudo depmod -a` then retry | Dependency index not updated after manual module install |

## WSL2 Module Loading Mechanism

How WSL2 6.6+ kernel modules are distributed:

- Modules are packaged in `modules.vhd` (Windows-side file)
- Mounted at startup as the overlay's **lower layer** (read-only), path `/modules`
- `/usr/lib/modules/<ver>/` is the overlay merged view:

```
overlay → lower = /modules (modules.vhd, read-only)
          upper = /lib/modules/.../rw/upper (writable, persists across reboots)
```

## Lessons Learned

This diagnosis got stuck on the wrong assumption that "Exec format error = file corruption", wasting significant time. Checking vermagic first would have saved a lot of effort.

1. **Exec format error = vermagic mismatch**, not "file corruption" or "kernel doesn't support it"
2. **WSL2 kernel update requires replacing three files**: kernel + system.vhd + **modules.vhd**
3. **When confirming "kernel doesn't support it", check CONFIG_TUN first**: `grep CONFIG_TUN /boot/config-$(uname -r)`, `CONFIG_TUN=m` means kernel supports it, just module not loaded
