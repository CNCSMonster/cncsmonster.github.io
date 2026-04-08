+++
title = 'FGM - Go 工具链版本管理器（已归档）'
date = 2024-09-21T23:35:50+08:00
tags = ['Go', 'Rust', '工具链', '开源项目']
weight = 1
+++

> ⚠️ **注意：这个项目已归档**
>
> FGM 已被 [Mise](https://github.com/jdx/mise) 取代，不再维护。
>
> 推荐阅读：[使用 Mise 替换 FGM](/posts/shi-yong-mise-ti-huan-fgm/)

---

# FGM

**Go 工具链版本管理器，用 Rust 编写。**

## 设计意图

在不同项目之间切换时，经常需要使用不同版本的 Go 工具链。

FGM 提供一个简单的命令行工具，帮助你**快速切换 Go 版本**，支持多项目并行开发。

## 核心方案

- **搜索可用版本** - `fgm list-remote`
- **安装指定版本** - `fgm install 1.21`
- **切换版本** - `fgm use 1.21`
- **项目级别配置** - 每个项目使用不同 Go 版本
- **本地版本缓存** - 避免重复下载

与同类工具对比：
- **vs gvm** - 更轻量，无依赖
- **vs goenv** - 配置更简单
- **vs Mise** - 功能单一，只管理 Go

## 快速体验

```bash
# 安装（需要 Rust 工具链）
cargo install fgm

# 或者使用 cargo-binstall
cargo binstall fgm

# 初始化环境变量
eval $(fgm init)

# 查看可用版本
fgm list-remote

# 安装版本
fgm install 1.21

# 切换版本
fgm use 1.21

# 查看已安装版本
fgm ls
```

## 项目链接

- **GitHub**: [cncsmonster/fgm](https://github.com/cncsmonster/fgm)（已归档）
- **替代方案**: [jdx/mise](https://github.com/jdx/mise)

---

**FGM 已完成历史使命，推荐使用 Mise 作为替代方案。**
