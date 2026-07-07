+++
title = "Git for Windows 操作 bare 仓库 SSH 别名无效？——内嵌 SSH 不读 ~/.ssh/config"
description = "Git for Windows 内嵌 SSH 只读 Git 安装目录下的 ssh_config，操作 bare 仓库时 Host 别名不生效。改用系统 OpenSSH 即可解决。"
date = 2026-07-08T22:00:00+08:00
draft = false
tags = ["git", "windows", "ssh", "troubleshooting"]
categories = ["DevOps"]
toc = true
+++

## 问题现象

在 Windows 上配置了 `~/.ssh/config` 的 SSH 远程别名（Host alias），用于连接远端服务器上的 Git bare 仓库。终端里直接 `ssh <alias>` 可以正常连接，但 `git clone`、`git fetch` 等 Git 操作却报 `Could not resolve hostname`，别名完全不生效。

```text
$ git clone git@my-server:user/repo.git
Cloning into repo...
ssh: Could not resolve hostname my-server: Name or service not known
fatal: Could not read from remote repository.
```

明明 `ssh my-server` 能通，Git 操作却找不到这个主机——为什么？

## 排查结论

**Git for Windows 捆绑的 MSYS2/MinGW 内嵌 SSH 客户端（`Git\usr\bin\ssh.exe`）只读取 Git 安装根目录下的 `etc/ssh/ssh_config`（即 `C:\Program Files\Git\etc\ssh\ssh_config`），完全忽略用户的 `~/.ssh/config`，因此你在其中配置的 Host 别名对 Git 操作无效。**

解决方案：让 Git 改用 Windows 系统自带的 OpenSSH 即可。

```bash
git config --global core.sshCommand "C:/Windows/System32/OpenSSH/ssh.exe"
```

系统 OpenSSH 会正确读取用户的 `~/.ssh/config`，别名配置立即生效。

> 如果 Windows 用户名为中文（如 `username`），MSYS2 运行时路径转换失败会进一步加剧此问题。

## 排查过程

### 1. 确认 Git 使用的 SSH 是谁

```powershell
# 查看 Git 可执行文件路径
powershell -Command "Get-Command git | Select-Object Source"
# → C:\Program Files\Git\cmd\git.exe
```

Git for Windows 来自 winget / 官网安装，捆绑了自己的 MSYS2 环境。

### 2. 诊断内嵌 SSH 读取了哪些配置

```powershell
powershell -Command "& 'C:\Program Files\Git\usr\bin\ssh.exe' -vvv -G <你的别名> 2>&1 | Select-String config"
```

输出中**只出现** `etc/ssh/ssh_config` 而没有 `~/.ssh/config` —— 这里的 `etc/ssh/ssh_config` 是 MSYS2 根相对路径，实际文件位于 Git 安装目录 `C:\Program Files\Git\etc\ssh\ssh_config`。说明内嵌 SSH 根本不会去看用户的 `~/.ssh/config`。

### 3. 对比系统 OpenSSH

Windows 10/11 自带 OpenSSH 位于 `C:\Windows\System32\OpenSSH\ssh.exe`，它的行为是标准的——读取用户的 `~/.ssh/config`。因此直接用系统 OpenSSH 替代即可根治。

### 4. 修复验证

```bash
# 配置 Git 使用系统 OpenSSH
git config --global core.sshCommand "C:/Windows/System32/OpenSSH/ssh.exe"

# 再次尝试
git clone git@my-server:user/repo.git
```

克隆成功，不再报错。

## 总结

| 项目 | 内容 |
|---|---|
| 症状 | `ssh` 别名正常，Git 操作报 Host 解析失败 |
| 根因 | Git for Windows 内嵌 SSH 只读 `Git\etc\ssh\ssh_config`，忽略 `~/.ssh/config` |
| 一句话修复 | `git config --global core.sshCommand "C:/Windows/System32/OpenSSH/ssh.exe"` |
| 适用场景 | winget / 官网安装的 Git for Windows，Windows 10/11 |
