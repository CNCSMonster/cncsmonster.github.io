+++
title = 'Dotfiles - 笔者的开发环境配置'
date = 2026-04-07T00:00:00+08:00
tags = ['Dotfiles', '开发环境', '自动化']
weight = 1
+++

**笔者的开发环境配置集合，一键搭建完善的开发环境。**

## 解决什么问题

拿到新电脑（或重装系统）后，如何快速恢复熟悉的开发环境？

逐个安装软件、配置文件？需要几小时甚至几天。

## 核心方案

这个项目是**笔者的开发环境自动化配置脚本**。

- **一键部署** - `./setup.sh` 自动完成所有配置
- **完整工具链** - Helix、Zsh、Rust、Go、Node.js 等
- **环境一致** - 固定版本号，确保可复现

你可以：
- **直接使用** - 获得与笔者一致的环境
- **参考借鉴** - 了解如何组织 dotfiles
- **二次定制** - Fork 后打造你的配置

## 快速体验

```bash
git clone https://github.com/cncsmonster/dotfiles.git
cd dotfiles && ./setup.sh
```

一键完成所有配置，约 20-50 分钟（取决于电脑性能和网络环境）。

## 项目链接

- **GitHub**: [cncsmonster/dotfiles](https://github.com/cncsmonster/dotfiles)

---

欢迎 Star 和 PR！ ⭐
