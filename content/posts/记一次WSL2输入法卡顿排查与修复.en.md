+++
title = "How I Fixed WSL2 Input Method Lag — A Debugging Story"
date = 2026-05-15T00:00:00+08:00
tags = ["WSL2", "IME", "Lag", "Troubleshooting", "swap", "swappiness"]
+++

## Running into the Same Problem?

Typing Chinese in a WSL2 terminal feels "sluggish" — a sticky delay between keystroke and character appearing on screen.

Run these three lines first to confirm it's the same issue, then jump straight to **Quick Fix**.

Inside WSL:

```bash
cat /proc/sys/vm/swappiness   # Default 60. >10 with plenty of free RAM → threshold too loose
free -h | grep Swap           # Plenty of free RAM but hundreds of MB in swap → likely legacy/thrashing
df -h /mnt/c/ | tail -1       # System drive >80% → IME file I/O affected
```

## Root Cause in One Sentence

Three separate lines all bottlenecked on the keystroke-to-echo path:

```
Keystroke → [Windows Input Pipeline] ← C: drive full, IME sluggish
          → Terminal                ← same as above
          → [ConPTY → WSL]         ← autoMemoryReclaim interrupts VM frequently
          → shell → echo           ← swap thrashing, PTY echo delayed
```

1. **C: drive near full** → Windows input method framework and terminal rendering both slow down
2. **swappiness=60 (default)** → system pushes processes into swap despite 18 GB of free RAM
3. **swap thrashing** → swapped-out pages are intermittently read back, I/O lands right in the PTY echo window

One layer alone wouldn't be noticeable. Three layers stacked, landing in the tens of milliseconds between keystroke and echo.

## Quick Fix

### ① Lower swappiness + persist (immediate effect)

Inside WSL:

```bash
sudo sysctl vm.swappiness=10                                          # Takes effect immediately
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf                # Loaded by systemd on boot
```

> ⚠️ Before editing `/etc/sysctl.conf`, check if a `vm.swappiness` entry already exists — modify it if present, append if not. Avoid duplicate lines.

### ⚠️ ② Clear swap (watch out for WSL2 specifics)

WSL2's swap isn't managed by `/etc/fstab` — `swapon -a` does nothing for it.

Inside WSL:

```bash
# 1. Find what's occupying swap
for pid in /proc/*/status; do
  swp=$(grep VmSwap $pid | awk '{print $2}')
  [ "${swp:-0}" -gt 10000 ] && echo "$swp KB - $(grep Name $pid) (PID=$(basename $(dirname $pid)))"
done | sort -rn
```

This lists process names and PIDs, e.g. `1039088 KB - node-MainThread (PID=1200819)`.

```bash
# 2. Kill the biggest offenders (replace with actual PIDs from the output above)
kill -9 <PID1> <PID2>

# 3. Wipe and rebuild swap
sudo swapoff -a                   # Deactivate swap (clears the signature)
sudo mkswap /dev/sdc && sudo swapon /dev/sdc   # Rebuild signature and re-enable
```

### ③ Clean up the C: drive (Windows side)

In Windows PowerShell:

```powershell
rd /s /q %TEMP%                  # Clear temp files
powercfg /hibernate off          # Disable hibernation, frees ~16 GB
cleanmgr /sagerun:1              # Disk cleanup
```

### ④ Set autoMemoryReclaim to disabled

Edit `C:\Users\<username>\.wslconfig` on Windows (or `/mnt/c/Users/<username>/.wslconfig` inside WSL):

`disabled` means WSL won't return freed memory to Windows, but internal WSL reuse is unaffected — 20 GB is a cap, not a reservation. Actual memory usage depends entirely on your workload. The benefit of `disabled` is eliminating the HYP interrupts caused by `gradual`, making WSL more stable. The only cost: freed idle memory inside WSL won't be immediately returned to Windows (internal reuse remains unaffected).

```ini
[experimental]
autoMemoryReclaim=disabled
```

### ⑤ Reboot (or manually clean up leftover processes)

After the first four fixes, the keyboard still felt slightly off. Turned out there were 26 stale zsh sessions and 8 gitstatusd daemons accumulated over 15 days without a reboot. A full system reboot cleared everything with WSL restarting.

Or, without rebooting, manually handle it inside WSL:

```bash
pkill gitstatusd          # Kill stale git monitoring processes
# Find orphan zsh sessions (PPID=1) and kill them:
ps -eo pid,ppid,cmd | awk '$2==1 && /zsh/ {print $1}' | xargs kill -9
```

## Results

| Metric | Before | After |
|--------|--------|-------|
| swappiness | 60 | **10** (persisted) |
| Swap used | 2.0 GB | **8.6 MB** |
| C: drive | 81% | **64%** |
| Swap I/O | constant > 0 | **0** |
| Input method | noticeably laggy | **responsive** |

---

## Full Troubleshooting Log

> What follows is the real-time record of the layer-by-layer investigation. Read on if you're curious about the "why" or want to learn the debugging approach.

### Symptoms

Typing Chinese in a WSL2 terminal felt laggy — a sticky, delayed sensation between pressing a key and seeing the character appear. Not a full freeze, just "not responsive."

### Pitfall: I didn't know the full pipeline at first

IME lag requires tracing the entire keystroke-to-echo path. I reconstructed this pipeline after the fact using Microsoft documentation (Keyboard Input Overview + TSF + ConPTY architecture):

```
Keyboard hardware → [Windows Input Pipeline] → Terminal → [ConPTY → WSL] → shell → echo
                          ↑ IME lives here
```

- **Windows Input Pipeline**: keyboard driver → scan codes → keyboard layout → TSF/IME processes Chinese → generates WM_CHAR character messages. IME isn't a standalone step — it's embedded in the input pipeline.
- **Terminal → ConPTY → WSL**: Windows Terminal connects to WSL2 init via ConPTY (Windows Pseudo Console), which forwards to the Linux PTY, arriving at zsh.

But I didn't know any of this during the investigation. I approached it by checking both ends — Windows side, then WSL side.

### Step 1: Windows Task Manager → ruled out RAM

First instinct was memory pressure. `Ctrl + Shift + Esc` → Performance → Memory — usage was normal. Not the problem.

### Step 2: WSL basic metrics → found swap anomaly

Inside WSL:

```bash
top -bn1 | head          # Load 0.19, CPU idle 97%
free -h                  # Free RAM 18.6 GB / Total 20 GB
cat /proc/meminfo        # Swap used: 2.6 GB ← red flag
cat /proc/sys/vm/swappiness  # = 60 (default)
```

| Metric | Value | Meaning |
|--------|-------|---------|
| swappiness | **60** | Swapping starts when free RAM drops below ~8 GB — threshold too loose |
| Swap used | **2.6 GB** / 8 GB | Historical — swapped out during earlier long sessions when RAM was full; kernel doesn't proactively swap back |
| 14-day swap activity | ~50M page-ins, ~50M page-outs | Swap wasn't sitting idle — massive historical read/write volume |

**Swap usage (2.6 GB) is historical. Swap thrashing is the problem.** The usage itself doesn't cause lag. The intermittent page-in I/O from thrashing does.

### Step 3: Who's in swap

Inside WSL:

```bash
for pid in /proc/*/status; do
  swp=$(grep VmSwap $pid | awk '{print $2}')
  [ "$swp" -gt 0 ] && echo "$swp KB - $(grep Name $pid)"
done | sort -rn
```

Two orphan `qwen` (Tongyi Qianwen CLI) processes held 1.6 GB — each had allocated 44 GB of virtual address space but only 1–2 MB RSS. Their original terminals were long gone; the processes were adopted by systemd (PID 1).

### Step 4: Confirmed swap thrashing

Inside WSL:

```bash
vmstat 1                    # si column consistently > 0
cat /proc/pressure/memory   # some avg10=3.48
cat /proc/pressure/io       # some avg10=3.97
```

### Step 5: C: drive nearly full

Inside WSL:

```bash
df -h /mnt/c/   # 196 GB capacity, 159 GB used, 38 GB free (81%)
```

At 81% full, Windows IME's dictionary reads and writes become sluggish. PowerShell scanning identified `AppData\Local\Temp` (8 GB) and `hiberfil.sys` (~16 GB) as the main culprits.

### Root Cause Mapping

```
Keystroke → [Windows Input Pipeline] ← C: drive 81% full, IME file I/O slowed
          → Terminal                ← same as above
          → [ConPTY → WSL]         ← autoMemoryReclaim=gradual, VM frequently paused
          → shell → echo           ← swap thrashing, PTY echo delayed by I/O
```

A single layer's delay might be imperceptible. All three stacked, landing in the few dozen milliseconds between keystroke and echo.

### ⚠️ Pitfall: WSL2 swap recovery

After `swapoff -a`, `swapon -a` does nothing — because WSL2's swap isn't managed by `/etc/fstab` (fstab is empty). Instead, WSL2 init directly mounts `/dev/sdc`. Recovery requires `mkswap /dev/sdc && swapon /dev/sdc`.

## Lessons Learned

- **Debug WSL2 lag from both ends**: rule out the obvious (Task Manager) first, then dig into what you normally overlook (swap, PSI, orphan processes).
- **Large free RAM ≠ no lag**: swappiness=60 is too aggressive for desktop/WSL use. Lower it to 10 — don't touch swap until RAM is truly needed.
- **Swap is about thrashing, not usage**: 2 GB of swap usage doesn't cause lag. Small, frequent page-in/page-out bursts do.
- **Orphan process swap is a liability too**: inactive processes with 44 GB VSZ each in swap generate continuous page faults.

## Glossary

> Skim these if unfamiliar — not required to follow the fix above.

**swappiness**: Linux kernel parameter (0–100) controlling how aggressively memory is swapped out. Default is 60. At 10, the kernel only swaps when RAM is truly scarce.

**swap (swap space)** : a disk partition used as overflow when physical RAM runs low. WSL2 swap size is configured via `swap=8G` in `.wslconfig`.

**PSI (Pressure Stall Information)** : Linux kernel pressure metrics. `/proc/pressure/memory` and `/proc/pressure/io` show how much time the system spends stalled on memory or disk I/O.

**HYP interrupt**: Hyper-V callback interrupt. WSL2 runs as a Hyper-V VM, and the host (Windows) communicates with the VM through these interrupts. A count in the hundreds of millions indicates extremely frequent interaction.

**ConPTY**: Windows Pseudo Console — Windows Terminal connects to the Linux PTY inside WSL2 through this.

**autoMemoryReclaim**: WSL2 experimental feature controlling whether freed WSL memory is returned to Windows. `gradual` returns it slowly; `disabled` never returns it.

## References

- [Microsoft Keyboard Input Overview](https://learn.microsoft.com/en-us/windows/win32/inputdev/about-keyboard-input)
- [Windows Text Services Framework (TSF)](https://learn.microsoft.com/en-us/windows/win32/tsf/text-services-framework)
- [WSL2 `.wslconfig` Reference](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)
- [Linux swappiness Documentation](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [Linux PSI Documentation](https://docs.kernel.org/accounting/psi.html)
