+++
title = 'gen-mdbook-summary - mdBook 目录生成工具'
date = 2026-04-07T00:00:00+08:00
tags = ['Rust', 'mdBook', '开源项目', '工具']
weight = 3
+++

**为 mdBook 项目自动生成 SUMMARY.md 文件的工具。**

## 解决什么问题

用 mdBook 写技术书时，每次添加新章节都要手动修改 `SUMMARY.md`？

章节多了之后，维护目录结构变得繁琐且容易出错。

## 核心方案

这个工具**自动扫描目录结构，生成 SUMMARY.md**。

- **自动扫描** - 递归扫描指定目录
- **智能过滤** - 支持 `.gmsignore` 文件
- **一键生成** - `gms -d src -o src/SUMMARY.md`

## 快速体验

```bash
cargo install gen-mdbook-summary
gms -d src -o src/SUMMARY.md
```

## 项目链接

- **GitHub**: [cncsmonster/gen-mdbook-summary](https://github.com/cncsmonster/gen-mdbook-summary)
- **crates.io**: [gen-mdbook-summary](https://crates.io/crates/gen-mdbook-summary)
