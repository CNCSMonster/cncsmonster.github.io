+++
title = 'SSH 暴力破解入侵与安全加固复盘'
date = 2026-05-23T00:00:00+08:00
tags = ['安全', 'SSH', '入侵', '复盘']
+++

## 事件概述

WSL 通过 rathole 内网穿透将 SSH 暴露到公网（非标准端口）。5 月 22 日晚，攻击者通过字典暴力破解 `test` 用户的弱密码，成功登录并植入门罗币矿机。到 5 月 23 日凌晨被发现时，矿机已满负荷运行约一天，占用 2.4 GiB 内存。

## 攻击路径

```
公网扫描器 → 公网入口:非标准端口 (rathole 穿透)
                  ↓
            WSL SSH (内网)
                  ↓ 字典爆破
            test 用户 (弱密码)
                  ↓
            部署矿机 + crontab 后门
```

## 受害程度

| 项目 | 情况 |
|------|------|
| 矿机进程 | 伪装成 `systemd-udevdar`，吃满 CPU（1062%），占 2.4 GiB 内存。疑似 XMRig/RandomX 挖门罗币 |
| 后门 | crontab `@reboot /var/tmp/.sys_cache_94`（清理时空文件，未部署完） |
| 密码 | 攻击者登录后立刻改了 test 密码 |
| API Key 泄露 | `~/.bashrc` 中 DeepSeek API Key 明文存储，可能被窃取 |
| 数据 | 无法确认攻击者是否读取/拷贝了文件 |

## 漏洞清单

| # | 问题 | 严重度 |
|---|------|--------|
| 1 | **SSH 允许密码登录** — 根本原因 | 🔴 |
| 2 | **test 账户密码太弱** — 字典一撞就进 | 🔴 |
| 3 | **多余系统账户** — 系统中存在不止一个弱密码的非核心账户 | 🟡 |
| 4 | **非标准端口不防扫描** — 全端口扫描不挑端口号 | 🟡 |
| 5 | **无 fail2ban** — 1412 次失败尝试无任何自动阻断 | 🟡 |
| 6 | **API Key 明文放 bashrc** — 被入侵即泄露 | 🟡 |

## 核心教训

### 1. 安全不靠隐藏，靠密钥

换端口是障眼法。masscan/zmap 这类工具可以在几分钟内扫描整个 IPv4 的指定端口段——攻击者不需要知道你的具体端口，扫一遍全网就全出来了。非标准端口只是少了一些噪声级别的攻击，真正的扫描器照样能找到。**只有禁用密码、强制密钥认证能真正挡住。**

### 2. 每一个系统账户都是入口

系统上有多个用户（包括一个弱密码的 `test`）。攻击者试到 `test` 就成了。任何暴露到公网的服务，所有本地用户都同时暴露在攻击面下——只要有一个密码弱，整个系统就门户大开。

### 3. 公网暴露 = 零信任

rathole 把内网服务直接映射到公网，等同于把 SSH 直接放到互联网上。**必须假设公网流量 100% 是恶意的。**

### 4. 被入侵后要查持久化

攻击者做了三件事：**矿机、改密码、留 crontab**。如果只杀进程不动 crontab，重启矿机又复活。排查时至少检查：
- `crontab -l` / `/var/spool/cron/crontabs/`
- `~/.ssh/authorized_keys` 是否多了不明密钥
- `~/.bashrc` / `~/.profile` 是否有后门代码
- systemd user services
- `/tmp` / `/var/tmp` / `/dev/shm` 可疑文件

### 5. 密钥文件注意权限和泄露面

API Key 放 `~/.bashrc` 作为环境变量用本身没问题——攻击者如果已经拿到你的 shell，`env` 一样能看到，存哪都一样。真正要防的是**非入侵场景的泄露**：`~/.bashrc` 是否被提交到了 dotfiles 公开仓库？是否在其他地方被分享或备份？至少确保 `chmod 600`，只允许本用户读取。防线应该在"不让别人登录"上，不在"登录后怎么藏密钥"。

## 修复措施

```bash
# 1. 关闭密码登录（全局，所有用户）
sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# 2. 锁定失陷账户
sudo passwd -l test

# 3. 杀掉恶意进程
sudo pkill -KILL -u test

# 4. 清除 crontab 后门
sudo rm /var/spool/cron/crontabs/test

# 5. 删除后门脚本
sudo rm /var/tmp/.sys_cache_94
```

## 事后清单：入侵后该做什么

如果发现被入侵，按这个顺序过一遍：

1. **杀进程止血** — `pkill -KILL -u <失陷用户>` 先把矿机/后门进程停掉
2. **查持久化** — crontab、authorized_keys、bashrc/profile、systemd user services、/tmp 和 /var/tmp 隐藏文件
3. **吊销泄露的凭证** — 入侵者可能已经读走了配置文件中的 API Key、token，到对应平台后台全部吊销换新
4. **关密码改密钥** — 这是根本防线，不是换端口
5. **清理多余账户** — 回顾系统上有哪些用户、哪些有弱密码、哪些根本不需要
