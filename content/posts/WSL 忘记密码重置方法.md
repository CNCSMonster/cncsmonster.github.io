+++
title = 'WSL 忘记密码重置方法'
date = 2026-05-08T00:00:00+08:00
tags = ['WSL', '密码重置', 'Ubuntu']
+++

> 适用：默认 WSL 用户是普通用户，忘记密码无法 `sudo`。如果默认用户是 root，不存在密码问题，本文不适用。
> 
> 💡 如果你使用的是能执行命令的 AI 编码助手（如 Claude Code、Cursor Agent、Pi 等），可直接把本文链接发给它，它会按步骤引导你操作。传统的代码补全工具（如 Copilot）不适用。

## ① 以 root 进入 WSL

在 Windows 的 **PowerShell**（Win 键搜索 "PowerShell"）中执行：

```powershell
wsl -u root
# 或指定发行版：wsl -d Ubuntu-24.04 -u root
```

> 不知道发行版名称？先 `wsl -l -v` 查看列表，再用 `wsl -d <名称> -u root`。
> 成功后提示符变为 `root@...`，说明已在 WSL root 用户下。

## ② 重置密码

当前在 root shell 中，执行：

```bash
# 查看有哪些用户（一般和 Windows 用户名相同）
ls /home
# 输出示例：cncsmonster  lost+found

# 重置密码（用上一步看到的实际用户名替换）
passwd <用户名>
```

> 输入新密码时屏幕**没有任何显示**（连 `*` 都没有），这是 Linux 的正常行为。输完回车，再确认一次，看到 `passwd: password updated successfully` 即成功。

## ③ 验证

```bash
# 退出 root shell，回到 PowerShell
exit
```

回到 PowerShell 后，重新以普通用户登录 WSL：

```powershell
wsl
```

进入 WSL 后测试：

```bash
sudo whoami
# 提示输入密码则输入刚设置的新密码
# 输出 root 表示成功
```
