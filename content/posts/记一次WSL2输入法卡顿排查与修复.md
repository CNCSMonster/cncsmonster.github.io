+++
title = "记一次 WSL2 输入法卡顿排查与修复"
date = 2026-05-15T00:00:00+08:00
tags = ["WSL2", "输入法", "卡顿", "排查", "swap", "swappiness"]
+++


## 遇到同样的问题？

WSL2 终端里打中文"不跟手"——按键到字符出现有粘滞延迟。

先看下面三行确认是不是同一个问题，然后直接跳到**快速修复**。

在 WSL 中执行：

```bash
cat /proc/sys/vm/swappiness   # 默认 60，内存充裕时 > 10 说明阈值太宽松
free -h | grep Swap           # 空闲内存充裕却占了几百 MB → 疑为历史遗留/抖动
df -h /mnt/c/ | tail -1       # 系统盘 > 80% 时 IME 文件 I/O 容易受影响
```

## 一句话根因

三条线同时卡在键盘到回显的路径上：

```
键盘 → [Windows 输入管道] ← C 盘满，IME 变慢
     → 终端               ← 同上
     → [ConPTY → WSL]    ← autoMemoryReclaim 频繁中断 VM
     → shell → 回显       ← swap 抖动，pty 回显延迟
```

1. **C 盘满** → Windows 侧的输入法框架和终端渲染都变钝
2. **swappiness=60（默认值）** → 明明有 18GB 空闲内存，系统却往 swap 里塞进程
3. **swap 抖动** → 被换出的页面断续被读回，I/O 恰好踩在 pty 回显的时间窗口里

单独一层不卡，三层叠加刚好在你击键到看见字符这几十毫秒里。

## 快速修复

### ① 降 swappiness + 持久化（立刻见效）

在 WSL 中执行：

```bash
sudo sysctl vm.swappiness=10                                          # 立即生效
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf                # systemd 启动时加载
sudo tee -a /etc/wsl.conf << 'EOF'                                    # WSL 原生加载

[sysctl]
vm.swappiness=10
EOF
```

### ⚠️ ② 清 swap（注意 WSL2 的坑）

WSL2 的 swap 不靠 `/etc/fstab`，`swapon -a` 对它无效。

在 WSL 中执行：

```bash
# 1. 先找出谁在占 swap
for pid in /proc/*/status; do
  swp=$(grep VmSwap $pid | awk '{print $2}')
  [ "${swp:-0}" -gt 10000 ] && echo "$swp KB - $(grep Name $pid) (PID=$(basename $(dirname $pid)))"
done | sort -rn
```

输出会列出进程名和 PID，例如 `1039088 KB - node-MainThread (PID=1200819)`。

```bash
# 2. 杀掉占大头的进程（替换为上面输出的 PID）
kill -9 <PID1> <PID2>

# 3. 清空并重建 swap
sudo swapoff -a                   # 关闭 swap（会擦除签名）
sudo mkswap /dev/sdc && sudo swapon /dev/sdc   # 重建签名并重新启用
```

### ③ 清理 C 盘（Windows 侧）

在 Windows PowerShell 中执行：

```powershell
rd /s /q %TEMP%                  # 清临时文件
powercfg /hibernate off          # 关休眠释放 ~16GB
cleanmgr /sagerun:1              # 磁盘清理
```

### ④ autoMemoryReclaim 改为 disabled

在 Windows 中编辑 `C:\Users\<用户名>\.wslconfig`
（或在 WSL 中编辑 `/mnt/c/Users/<用户名>/.wslconfig`）：

`disabled` 意味着 WSL 释放的内存不会还给 Windows，但不影响 WSL 内部复用——20GB 是上限，不是预留。日常 WSL 只用 2-3GB，即使跑完大推理任务后不归还，剩余物理内存仍足够 Windows 正常使用。代价为零，收益是消掉 gradual 带来的 HYP 中断。

```ini
[experimental]
autoMemoryReclaim=disabled
```

### ⑤ 重启（或手动清理残留）

前三刀修完后键盘仍微卡。发现系统里挂着 26 个陈旧 zsh 会话和 8 个 gitstatusd 守护进程（15 天未重启累积），直接重启了电脑，WSL 随系统重启后所有残留清空。

也可以不重启，手动处理：

在 WSL 中执行：

```bash
pkill gitstatusd          # 杀陈旧的 git 监控进程
# 找出 PPID=1 的孤儿 zsh 并杀掉：
ps -eo pid,ppid,cmd | awk '$2==1 && /zsh/ {print $1}' | xargs kill -9
```

## 修复效果

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| swappiness | 60 | **10**（持久化） |
| Swap 使用 | 2.0 GB | **8.6 MB** |
| C 盘 | 81% | **64%** |
| Swap I/O | 持续 > 0 | **0** |
| 输入法 | 明显卡顿 | **跟手** |

---

## 完整排查过程

> 以下是当时逐层排查的真实记录。如果你有兴趣了解"为什么"或者想学习类似的排查方法，可以往下看。

### 症状

WSL2 终端里打中文感觉卡——按下按键到字符出现在屏幕上，有一种粘滞的延迟感。不是完全卡死，而是"不跟手"。

### 踩坑：我一开始不知道完整链路

输入法卡顿，得从击键到回显的整条路径去想。这条链路是事后根据微软文档查证后整理的（Keyboard Input Overview + TSF + ConPTY 架构）：

```
键盘硬件 → [Windows 输入管道] → 终端 → [ConPTY → WSL] → shell → 回显
               ↑ IME 在这里面
```

- **Windows 输入管道**：键盘驱动→扫描码→键盘布局→TSF/IME 处理中文→生成 WM_CHAR 字符消息。IME 不是单独的一步——它挂在输入管道里。
- **终端 → ConPTY → WSL**：Windows Terminal 通过 ConPTY（Windows 伪终端）连接到 WSL2 init，init 再转发给 Linux PTY，抵达 zsh。

但排查时并不知道这些。当时是按"两端排除"的方式一步步摸的——先看 Windows 侧有没有问题，再看 WSL 侧有没有问题。

### 第一步：Windows 任务管理器 → 排除了内存

第一反应是内存满了。按 `Ctrl + Shift + Esc` 打开任务管理器，切到「性能」→「内存」——占用正常，不是它的问题。

### 第二步：WSL 基本指标 → 发现 swap 异常

在 WSL 中执行：

```bash
top -bn1 | head          # 负载 0.19，CPU idle 97%
free -h                  # 空闲内存 18.6GB / 总计 20GB
cat /proc/meminfo        # Swap 占用了 2.6GB ← 扎眼
cat /proc/sys/vm/swappiness  # = 60（默认值）
```

| 指标 | 值 | 含义 |
|------|-----|------|
| swappiness | **60** | 空闲内存低于 8GB 就开始换出，阈值太宽松 |
| Swap 已用 | **2.6 GB** / 8 GB | 历史遗留——之前长会话跑满内存时换出，换出后内核不会主动换回 |
| 14 天内 swap 总量 | 换入换出各 **5000 万次** | swap 不是静躺——过去曾大量读写 |

**Swap 占用（2.6GB）是历史痕迹，swap 抖动才是问题。** 占用本身不卡，卡的是这些页面被断续访问时产生的换入 I/O。

### 第三步：谁在占 swap

在 WSL 中执行：

```bash
for pid in /proc/*/status; do
  swp=$(grep VmSwap $pid | awk '{print $2}')
  [ "$swp" -gt 0 ] && echo "$swp KB - $(grep Name $pid)"
done | sort -rn
```

两个 `qwen`（通义千问 CLI）孤儿进程占了 1.6GB——各自申请 44GB 虚拟地址空间但 RSS 只有 1-2MB，原终端早关了，进程被 systemd（PID 1）收养。

### 第四步：确认 swap 在抖动

在 WSL 中执行：

```bash
vmstat 1                    # si 列持续 > 0
cat /proc/pressure/memory   # some avg10=3.48
cat /proc/pressure/io       # some avg10=3.97
```

### 第五步：C 盘快满了

在 WSL 中执行：

```bash
df -h /mnt/c/   # 196G 用了 159G，剩 38G（81%）
```

系统盘 81% 满时 Windows IME 的词典读写变迟钝。PowerShell 扫描定位到 `AppData\Local\Temp`（8GB）和 `hiberfil.sys`（~16GB）。

### 根因对号入座

```
键盘 → [Windows 输入管道] ← C 盘 81% 满，IME 文件 I/O 变慢
     → 终端               ← 同上
     → [ConPTY → WSL]    ← autoMemoryReclaim=gradual，VM 被频繁暂停
     → shell → 回显       ← swap 抖动，PTY 回显被 I/O 拖慢
```

单层延迟可能无感，三层叠加刚好在击键到回显这几十毫秒里。

### ⚠️ 踩坑记录：WSL2 swap 恢复

`swapoff -a` 之后 `swapon -a` 无事发生——因为 WSL2 的 swap 不靠 `/etc/fstab`（fstab 是空的），而是由 init 直接挂载 `/dev/sdc`。恢复需要 `mkswap /dev/sdc && swapon /dev/sdc`。

## 学到的

- **从两端排查 WSL2 卡顿**：先排除能直接看到的（任务管理器），再深入平时不注意的（swap、PSI、孤儿进程）。
- **空闲内存大 ≠ 不会卡**：swappiness=60 对桌面/WSL 场景太激进。降到 10，内存用满之前不碰 swap。
- **swap 不是"占用"的问题，是"抖动"的问题**：占用 2GB 不卡，每秒小块换入换出才卡。
- **孤儿进程的 swap 也是负担**：进程不活跃但各 44GB VSZ 留在 swap 里，会产生持续缺页中断。

## 相关术语

> 如果下面这些词不熟悉，一两句读懂就行，不影响照着上面修。

**swappiness**：Linux 内核参数（0-100），控制多积极地把内存换到 swap。默认 60，降到 10 后只在内存真的不够时才换出。

**swap（交换空间）**：磁盘上划出来的一块区域，当物理内存不够时，把暂时不用的内存页暂存到磁盘上。WSL2 的 swap 大小在 `.wslconfig` 的 `swap=8G` 中配置。

**PSI（Pressure Stall Information）**：Linux 内核的压力指标。`/proc/pressure/memory` 和 `/proc/pressure/io` 告诉你系统有多少时间被内存或磁盘 I/O 卡住。

**HYP 中断**：Hyper-V 回调中断。WSL2 作为 Hyper-V 虚拟机，宿主机（Windows）通过这种中断跟 VM 通信。数量过亿说明交互非常频繁。

**ConPTY**：Windows 的伪终端（Pseudo Console），Windows Terminal 通过它连接到 WSL2 里的 Linux PTY。

**autoMemoryReclaim**：WSL2 实验性功能，控制 WSL 释放的空闲内存是否归还给 Windows。`gradual` 慢慢还，`disabled` 不还。

## 参考

- [Microsoft Keyboard Input Overview](https://learn.microsoft.com/en-us/windows/win32/inputdev/about-keyboard-input)
- [Windows Text Services Framework (TSF)](https://learn.microsoft.com/en-us/windows/win32/tsf/text-services-framework)
- [WSL2 `.wslconfig` 配置参考](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)
- [Linux swappiness 说明](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [Linux PSI 文档](https://docs.kernel.org/accounting/psi.html)
