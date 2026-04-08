+++
title = 'xdotter - 轻量级点文件管理器'
date = 2026-04-07T00:00:00+08:00
tags = ['Python', '开源项目', '点文件管理']
weight = 2
+++

**零依赖、单文件的点文件管理工具。**

## 解决什么问题

换新电脑时，如何快速恢复所有的配置文件（`.bashrc`、`.gitconfig` 等）？

手动复制？容易遗漏。用现有工具？依赖复杂，配置繁琐。

## 核心方案

xdotter 的答案：**一个配置文件夹 + 符号链接**。

- **零依赖** - 单个 `.pyz` 文件，下载即用
- **声明式配置** - TOML 文件定义映射关系
- **一键部署** - `xd deploy` 自动创建所有链接

与 dotter 对比：
- **更简单** - 不支持多种部署方式（链接/复制），只做符号链接
- **零依赖** - 无需编译 Rust 项目，Python 预装即可用
- **配置直观** - 单一 TOML 文件，无复杂模板语法

## 快速体验

```bash
# 下载
gh release download --repo cncsmonster/xdotter --pattern xd.pyz --output ~/.local/bin/xd

# 创建配置并部署
xd new && xd deploy
```

## 项目链接

- **GitHub**: [cncsmonster/xdotter](https://github.com/cncsmonster/xdotter)

---

欢迎 Star、Issue 和 PR！ ⭐
