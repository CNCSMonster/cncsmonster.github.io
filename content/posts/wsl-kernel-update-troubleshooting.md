+++
title = "WSL 内核更新踩坑实录：从 403 错误到 CVE-2026-31431 修复"
date = 2026-06-29T00:00:00+08:00
tags = ["WSL", "内核更新", "安全漏洞", "CVE-2026-31431", "排查", "403", "MSI"]
+++

> 记录一次 WSL 内核更新的完整排查过程，涵盖 403 错误、MSI 缓存损坏、两层安装路径冲突等问题的定位与解决。

## 背景

WSL 内核版本 **6.6.87.2** 存在 **CVE-2026-31431**（Copy Fail）本地提权漏洞，需要更新到 **6.18.x** 以上版本修复（来源：微软安全通告 [MSRC Advisory](https://msrc.microsoft.com/update-guide) / [NVD 公告](https://nvd.nist.gov/vuln/detail/CVE-2026-31431)）。

在执行 `wsl --update` 时遇到 HTTP 403 错误，随后展开了一系列排查。

## 问题现象

```powershell
PS> wsl --update
正在检查更新。
已禁止 (403)。
错误代码: Wsl/UpdatePackage/0x80190193
```

曾尝试切换不同代理节点，但无论哪个节点，`wsl --update` 始终返回 403。

## 排查过程

### 第一步：检查当前状态

```powershell
# WSL 版本
PS> wsl --version
WSL 版本: 2.6.3.0
内核版本: 6.6.87.2-1

# AppX 包版本（已下载但未生效）
PS> Get-AppxPackage -Name *WindowsSubsystemForLinux* | Select-Object Version
Version
-------
2.7.3.0

# 注册表中的安装版本
PS> Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" |
    Where-Object { $_.DisplayName -match "WSL|Linux" } |
    Select-Object DisplayName, DisplayVersion, InstallDate

DisplayName                 DisplayVersion InstallDate
-----------                 -------------- -----------
Windows Subsystem for Linux 2.6.3.0        20260212
```

**发现矛盾**：AppX 包显示 2.7.3.0，但实际运行的仍是 2.6.3.0。说明 Store 下载了新版包，但安装过程被阻塞。

### 第二步：查找阻塞原因

检查 MSI 安装日志：

```powershell
PS> Get-Content "$env:TEMP\MSIf13a6.LOG"
Error 1714. The older version of Windows Subsystem for Linux cannot be removed.
Contact your technical support group. System Error 1612.
```

**Error 1612** = "安装源不可用"。进一步检查：

```powershell
# 旧版 MSI 缓存文件
PS> Test-Path "C:\Windows\Installer\12f16c6.msi"
False  # 文件不存在！
```

**根因 1**：旧版 WSL 2.6.3.0 的 MSI 缓存文件 `C:\Windows\Installer\12f16c6.msi` 被删除了（可能是磁盘清理工具误删），导致 Windows Installer 无法卸载旧版本，新版本无法安装。

### 第三步：分析 403 错误

检查 Store 日志发现关键线索：

```
16:55:21  Network connectivity level changed to 0x0   ← 网络断开
16:55:15  Task canceled, reason: 'ResourceRevocation'  ← Store 任务被撤销
17:14:29  Network connectivity level changed to 0x3   ← 网络恢复
```

请求中的关键参数：

```
market=CN
productId=9NZKPSTSNW4P
licensing.md.mp.microsoft.com
```

**根因 2（初步假设）**：`wsl --update` 走的是 Microsoft Store 许可验证通道（`licensing.md.mp.microsoft.com`），怀疑是中国区 Store 服务不稳定导致 403。

**验证过程**：从 GitHub 下载 WSL 安装包完全正常（494MB 成功），说明网络本身没问题。

**进一步排查 — 定位真正根因**：

当时环境使用了代理，出口 IP 与账户所在市场区域不一致。Store 许可请求中包含参数 `market=CN`：

```
leaseUri: licensing.md.mp.microsoft.com/...&market=CN&...
```

> 微软 Store 许可服务器会校验请求来源 IP 与市场区域的匹配性。

| 场景 | 出口 IP 区域 | market | 结果 |
|---|---|---|---|
| 使用代理 | 非 CN 区域 | CN | **403 — IP 与 market 不匹配** |
| 直连（无代理） | CN | CN | ✅ 下载正常开始（不再 403） |

**最终确认的根因 2**：代理改变了出口 IP 的地理位置，与 Store 账户的市场区域（CN）不匹配，微软许可服务器返回 403 拒绝请求。关掉代理后 `wsl --update` 能正常开始下载（不再报 403），但后续仍然因网络问题无法完成。

**补充验证**：关掉代理直连后，`wsl --update` 虽然解决了 403，但下载速度极慢且多次中断：

- 第一次：下载到 ~1% 时连接重置（`0x80072eff`）
- 后续：不支持断点续传，每次都需从头开始
- 结论：在本文网络环境下，`wsl --update` 不具备实际可用性

### 第四步：为什么新版装了却不生效？

前面两步解释了 `wsl --update` 为何失败（MSI 缓存缺失、403 错误）。但还有一个问题：**第一步中看到 AppX 2.7.3.0 已经下载了，为什么系统实际运行的还是 2.6.3.0？**

检查 WSL 的调用链路：

```powershell
# 系统版 wsl.exe（薄壳转发器，负责将命令转发给 WSLService）
PS> (Get-Item "C:\Windows\System32\wsl.exe").VersionInfo.ProductVersion
10.0.26100.8457

# Store 版 wsl.exe（在 WindowsApps 中）
PS> (Get-Item "C:\Program Files\WindowsApps\...\wsl.exe").VersionInfo.ProductVersion
2.7.3.0

# 旧版 MSI 安装的 WSL（实际生效中的版本）
PS> (Get-Item "C:\Program Files\WSL\wsl.exe").VersionInfo.ProductVersion
2.6.3.0

# WSLService 服务指向哪里？
PS> Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\WSLService" |
    Select-Object ImagePath
ImagePath : "C:\Program Files\WSL\wslservice.exe"  ← 指向旧版！
```

调用链路如下：

```
wsl.exe (System32, 薄壳转发器)
       │
       ▼
WSLService 服务 ──→ C:\Program Files\WSL\wslservice.exe  (2.6.3.0)
```

**根因 3（补充）**：Store 将新版安装到了 `C:\Program Files\WindowsApps\...\`，但 WSLService 始终指向 MSI 安装路径 `C:\Program Files\WSL\`。两者是互不感知的独立路径——即使 Store 更新"安装成功"，WSLService 也不会自动切换过去，系统继续运行旧版本。

## 转折：观察文件结构，找到另一条路

排查到这里，三条路都走不通：`wsl --update` 被 403 阻断、Store 更新被 MSI 缓存问题卡住、直连下载慢且无断点续传。标准方案全部失效。

但我们手头有一个东西能用：从 GitHub 下载的完整安装包（msixbundle）。

解压这个包看看里面有什么：

```powershell
# 先将 msixbundle 中的 MSI 提取出来
msiexec /a "C:\Program Files\WindowsApps\...\wsl.msi" `
  /qb TARGETDIR="$env:TEMP\wsl_msi_extract"

# 查看提取出的文件结构
PS> Get-ChildItem "$env:TEMP\wsl_msi_extract\PFiles64\WSL" -Recurse | Select-Object FullName

PFiles64\WSL\wsl.exe
PFiles64\WSL\wslservice.exe
PFiles64\WSL\system.vhd          ← 374MB，Linux 内核镜像
PFiles64\WSL\tools\kernel        ← 17MB，内核引导文件
PFiles64\WSL\...
```

对比系统上正在运行的 WSL 目录：

```powershell
PS> Get-ChildItem "C:\Program Files\WSL" | Select-Object Name

wsl.exe
wslservice.exe
system.vhd                       ← 同名文件！
tools\kernel                     ← 同名文件！
...
```

**关键发现**：`PFiles64\WSL\` 的文件布局和 `C:\Program Files\WSL\` 完全一致——前者是 MSI 的安装映射，后者是实际的安装位置。其中 `system.vhd` 和 `tools\kernel` 就是内核层的全部文件。

反观第四步的结论：WSLService 指向 `C:\Program Files\WSL\`，这里才是内核实际生效的位置。那么：

> 如果把新版 MSI 中提取的 `system.vhd` 和 `tools\kernel` 覆盖到 `C:\Program Files\WSL\`，能不能只更新内核，不动管理程序？

WSL 的管理层（wsl.exe / wslservice.exe）和内核层（system.vhd + kernel）是独立运作的——管理层负责与 Windows 通信，内核层负责运行 Linux。这正是架构分层带来的可能性：**替换内核层不需要触碰管理层**。

于是决定一试。结果：一次成功，内核从 6.6.87.2 更新到 6.18.33.2，所有数据完好。

## 解决方案

### 核心思路

基于上述发现，整理出以下操作步骤。核心思路：**从 GitHub 下载完整包，从中提取内核文件，替换到 WSLService 指向的安装目录**。

> **注意**：手动替换内核文件是**非官方方法**，依赖 WSL 内部文件结构（微软未在文档中说明此做法）。未来 WSL 更新可能改变文件布局，导致此方法失效。长期应修复网络环境以使用 `wsl --update` 正常更新。

### 步骤 1：从 GitHub 下载完整安装包

```powershell
# 下载 WSL 2.7.10（约 494MB）
curl.exe -L -o "$env:TEMP\WSL_2.7.10.msixbundle" `
  "https://github.com/microsoft/WSL/releases/download/2.7.10/Microsoft.WSL_2.7.10.0_x64_ARM64.msixbundle"
```

### 步骤 2：安装 AppX 包

```powershell
# 先关闭所有 WSL 进程
wsl --shutdown

# 安装（需要管理员权限）
Add-AppxPackage -Path "$env:TEMP\WSL_2.7.10.msixbundle" -ForceApplicationShutdown
```

### 步骤 3：从 MSI 中提取内核文件

```powershell
# 解压 wsl.msi（管理安装模式，不实际安装）
msiexec /a "C:\Program Files\WindowsApps\MicrosoftCorporationII.WindowsSubsystemForLinux_2.7.10.0_x64__8wekyb3d8bbwe\wsl.msi" `
  /qb TARGETDIR="$env:TEMP\wsl_msi_extract"

# 提取出的关键文件：
# - PFiles64\WSL\system.vhd      (374MB, 包含 Linux 内核)
# - PFiles64\WSL\tools\kernel    (17MB, 内核引导文件)
```

### 步骤 4：替换内核文件

```powershell
# 以管理员身份执行
$extractDir = "$env:TEMP\wsl_msi_extract\PFiles64\WSL"
$targetDir = "C:\Program Files\WSL"

Copy-Item "$extractDir\system.vhd" "$targetDir\system.vhd" -Force
Copy-Item "$extractDir\tools\kernel" "$targetDir\tools\kernel" -Force
```

### 步骤 5：验证

```powershell
# 重启 WSL
wsl --shutdown
wsl

# 检查内核版本
PS> wsl -e uname -r
6.18.33.2-microsoft-standard-WSL2  ✅

# 检查数据完整性
PS> wsl -e cat /etc/os-release
PRETTY_NAME="Ubuntu 24.04.4 LTS"  ✅
```

## 关键知识点

### WSL 架构分层

```
┌─────────────────────────────────────────
│  用户层 (Ubuntu 系统)                    │
│  ext4.vhdx — 你的所有文件和数据          │
├─────────────────────────────────────────┤
│  内核层 (Linux 内核)                     │
│  system.vhd + tools/kernel              │
├─────────────────────────────────────────┤
│  管理层 (Windows 服务)                   │
│  wslservice.exe / wsl.exe               │
└─────────────────────────────────────────┘
```

**数据与内核完全分离**：更新内核不影响任何用户数据。

### 内核更新只需替换两个文件

| 文件 | 位置 | 作用 |
|---|---|---|
| `system.vhd` | `C:\Program Files\WSL\` | 包含 Linux 内核 + 驱动模块 |
| `tools/kernel` | `C:\Program Files\WSL\tools\` | 内核引导文件 |

不需要改注册表、不需要改服务配置、不需要卸载重装。

### `wsl --update` 失败的可能原因

| 错误码 | 含义 | 常见原因 |
|---|---|---|
| `0x80190193` (403) | 服务器拒绝 | **代理节点 IP 与 Store market 不匹配**（代理改变出口 IP 后与账户区域不一致） |
| `0x80072eff` | 连接被重置 | 直连 Store CDN 时网络丢包/不稳定，下载中断 |
| `0x80073D02` | 应用正在使用 | WSL 进程未完全关闭 |
| Error 1714/1612 | 安装源不可用 | MSI 缓存文件被删除 |

### 两种更新方法对比

| | `wsl --update` | 手动替换内核文件 |
|---|---|---|
| **官方支持** | ✅ 微软官方更新方式 | ❌ 非官方内部行为，依赖文件结构，未来可能不被维护 |
| **更新范围** | 整个 WSL 包（管理程序 + 内核） | 只替换内核文件（system.vhd + kernel），管理程序不动 |
| **下载量** | 完整包（管理程序 + 内核，体积更大） | 同样下载完整 msixbundle，但只提取内核文件使用 |
| **下载速度** | ❌ 极慢，20 秒不到 1%（Store CDN 问题） | ✅ 快，GitHub CDN ~3 分钟完成 |
| **失败模式 1** | ❌ 403 错误 — 请求直接被拒（代理 IP 与 market 不匹配） | ✅ 无此问题 |
| **失败模式 2** | ❌ 连接重置 (0x80072eff) — 下载中途断开（网络不稳定） | ✅ 无此问题 |
| **断点续传** | ❌ 不支持，每次从头开始 | ✅ curl 支持断点续传 |
| **成功完成时间** | 慢且不稳定，容易中断 | ~5 分钟（下载 3 分钟 + 替换 2 分钟） |

**本环境实测结论**：

- `wsl --update` 是本环境下的**首选推荐**方式，但实测速度慢（20 秒不到 1%），容易遇到 403（代理/market 不匹配）、0x80072eff（连接重置）等错误导致下载中断，且不支持断点续传
- 手动替换内核文件是**非官方的临时应急方案**：依赖 WSL 内部文件结构，微软未在文档中说明或支持此做法，未来版本可能失效。仅在本环境网络条件下 `wsl --update` 确实无法完成时作为备选，**5 分钟内完成**
- 长期建议：修复网络环境以使用 `wsl --update` 正常更新

### 注意事项

1. **`C:\Windows\Installer\` 下的文件不要手动删除** — 它们是系统安装/卸载/修复所必需的
2. **磁盘清理工具可能误删 MSI 缓存** — 使用清理工具时需谨慎
3. **Store 版和 MSI 版不要混用** — 会导致服务指向混乱
4. **国内使用 `wsl --update` 的常见坑**：
   - **代理 IP 与 Store market 不匹配** → 403。关掉所有代理/加速器即可
   - **直连下载慢且易中断** → `0x80072eff` 连接重置，且不支持断点续传
5. **手动替换内核文件是非官方方法**：微软未在文档中说明或支持此做法，依赖的内部文件结构可能在未来版本中变化

## 参考

- [CVE-2026-31431 (Copy Fail)](https://nvd.nist.gov/vuln/detail/CVE-2026-31431) — CVSS 7.8 HIGH，已被 CISA 列入已知利用漏洞目录
- [WSL GitHub Releases](https://github.com/microsoft/WSL/releases) — 完整安装包下载
- [copy.fail](https://copy.fail) — 漏洞详情网站
