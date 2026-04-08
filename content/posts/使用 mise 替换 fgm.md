+++
title = '使用 Mise 替换 FGM'
date = 2024-12-13T21:15:54+08:00
tags = ['Mise', '工具链', 'Rust', 'DevTools']
+++

Mise 能够完全覆盖 FGM 的功能和使用场景，而且不仅仅能够用来管理 Golang 工具链，还能够用来管理其他语言的工具链，比如 Node.js、Neovim、Java 等等。
甚至我们还能够用 Mise 来替换 direnv，实现管理进入退出目录时的环境变量加载和卸载。

下面将从三方面带你感受笔者使用 Mise 的体验：

## 一、下载 Mise

**方式 1**: 通过包安装管理器安装 Mise

```sh
# 需要先安装 cargo-binstall 和 Rust 工具链
cargo binstall mise
```

**方式 2**: 从仓库预编译版本下载资源列表中下载，解压缩后把 mise 可执行文件放到可执行文件目录即可

[jdx/mise Releases](https://github.com/jdx/mise/releases)

## 二、配置 Mise

### 2.1 初始化 Shell

```sh
# 对于 bash
echo 'eval "$(~/.cargo/bin/mise activate bash)"' >> ~/.bashrc

# 对于 zsh
echo 'eval "$(~/.cargo/bin/mise activate zsh)"' >> ~/.zshrc

# 对于 fish
echo '~/.cargo/bin/mise activate fish | source' >> ~/.config/fish/config.fish
```

### 2.2 配置文件

Mise 的配置文件是 `.mise.toml`,可以放在项目根目录或者家目录。

```toml
# ~/.mise.toml
[tools]
go = "1.21"
node = "20"
python = "3.12"
```

## 三、使用 Mise

```sh
# 安装工具
mise install go@1.21
mise install node@20

# 设置全局版本
mise use --global go@1.21

# 设置项目版本 (会自动创建 .mise.toml)
mise use go@1.21

# 列出已安装版本
mise ls

# 卸载
mise uninstall go@1.21
```

## 四、高级功能

### 4.1 环境变量管理

```toml
# .mise.toml
[env]
_.path = ["./bin", "{{config_root}}/scripts"]
API_KEY = "secret"
```

### 4.2 Task 运行器

```toml
# .mise.toml
[tasks.build]
description = "Build the project"
run = "make build"

[tasks.test]
description = "Run tests"
run = "go test ./..."
```

### 4.3 替换 direnv

Mise 支持 `.envrc` 文件，可以完全替换 direnv:

```sh
mise activate direnv
```

然后在 `.envrc` 中:

```bash
use go
use node
```

## 总结

Mise 是一个功能强大的工具链管理器，具有以下优势:

- ✅ 支持多种语言 (Go, Node.js, Python, Java, Rust 等)
- ✅ 支持项目级别和全局配置
- ✅ 支持环境变量管理
- ✅ 内置 Task 运行器
- ✅ 兼容 asdf 插件生态
- ✅ 性能优秀 (Rust 编写)
