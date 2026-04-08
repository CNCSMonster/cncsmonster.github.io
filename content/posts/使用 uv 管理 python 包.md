+++
title = '使用 UV 管理 Python 包'
date = 2025-01-03T00:22:09+08:00
tags = ['Python', 'UV', '包管理', '工具链']
+++

UV 是一个用 Rust 编写的极速 Python 包管理器和项目管理器。

## 参考资料

- [astral-sh/uv](https://github.com/astral-sh/uv)

## 安装 UV

```shell
# 使用 pip
pip install uv

# 或者使用 standalone installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或者使用 cargo
cargo install uv
```

## 使用 UV 运行 Python 项目

```shell
# 首先进入项目根目录
# 初始化 UV 工程配置
uv init

# 加入所需依赖
uv add <python 包名>

# 运行 Python 脚本
uv run python script.py

# 运行任意命令
uv run <command>
```

## 常用命令

```shell
# 创建虚拟环境
uv venv

# 安装包
uv pip install <package>

# 导出依赖
uv pip compile requirements.in -o requirements.txt

# 同步依赖
uv pip sync requirements.txt

# 显示依赖树
uv pip tree
```

## 优势

- 🚀 **极速**: 比 pip 快 10-100 倍
- 📦 **兼容**: 完全兼容 pip 和 requirements.txt
- 🔧 **一体**: 包含 venv、pip、pip-tools 的功能
- 🦀 **Rust**: 用 Rust 编写，稳定可靠
