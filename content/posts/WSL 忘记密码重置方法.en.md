+++
title = "How to Reset a Forgotten Password in WSL"
date = 2026-05-08T00:00:00+08:00
tags = ["WSL", "Password Reset", "Ubuntu"]
+++

> **Applies to:** Default WSL user is a regular user and you've forgotten the password (can't sudo).
> **Does not apply to:** Default user is root (no password problem exists).
>
> If you use an AI coding agent that can execute commands (Claude Code, Cursor Agent, Pi, etc.), just share the link to this article — it will guide you through the steps. Traditional code completion tools (e.g. Copilot) are not applicable.

## 1. Enter WSL as Root

Run the following in Windows PowerShell (Win key → search "PowerShell"):

```powershell
wsl -u root
# Or specify the distro: wsl -d Ubuntu-24.04 -u root
```

> `wsl.exe` is a Windows-side tool that can launch WSL as any Linux user — it bypasses the Linux authentication system, so the old password isn't needed.
>
> Don't know your distro name? Run `wsl -l -v` first to list them, then use `wsl -d <name> -u root`.
> When it succeeds, your prompt should change to `root@...`.

## 2. Reset the Password

Now in a root shell, run:

```bash
# See which users exist (usually matches your Windows username)
ls /home
# Example output: cncsmonster  lost+found

# Reset the password (use the actual username from the step above)
passwd <username>
```

> `passwd` executed as root allows you to set a new password directly — no old password required.
> When typing the new password, nothing shows on screen (not even asterisks) — this is normal Linux behavior. Press Enter after typing, confirm it once more, and you'll see `passwd: password updated successfully`.

## 3. Verify

```bash
# Exit the root shell, back to PowerShell
exit
```

Back in PowerShell, log into WSL as your regular user:

```powershell
wsl
```

Inside WSL, test:

```bash
sudo whoami
# Enter your new password when prompted
# Output should be: root
```
