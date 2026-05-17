+++
title = "Replacing FGM with Mise: A Practical Guide"
date = 2024-12-13T21:15:54+08:00
tags = ["Mise", "Toolchain", "Rust", "DevTools"]
+++

Mise fully covers FGM's features and use cases, and goes far beyond Golang toolchain management — it can manage toolchains for Node.js, Neovim, Java, and more. You can even replace direnv with Mise to handle environment variable loading and unloading when entering and leaving directories.

Here's my experience using Mise across three aspects:

## 1. Installing Mise

**Option 1**: Install via a package manager

```sh
# Requires cargo-binstall and the Rust toolchain
cargo binstall mise
```

**Option 2**: Download a prebuilt binary from the releases page, extract it, and place the `mise` executable in your PATH.

[jdx/mise Releases](https://github.com/jdx/mise/releases)

## 2. Configuring Mise

### 2.1 Shell Initialization

```sh
# For bash
echo 'eval "$(~/.cargo/bin/mise activate bash)"' >> ~/.bashrc

# For zsh
echo 'eval "$(~/.cargo/bin/mise activate zsh)"' >> ~/.zshrc

# For fish
echo '~/.cargo/bin/mise activate fish | source' >> ~/.config/fish/config.fish
```

### 2.2 Configuration File

Mise's config file is `.mise.toml`, placed in your project root or home directory.

```toml
# ~/.mise.toml
[tools]
go = "1.21"
node = "20"
python = "3.12"
```

## 3. Using Mise

```sh
# Install tools
mise install go@1.21
mise install node@20

# Set global version
mise use --global go@1.21

# Set project-specific version (auto-creates .mise.toml)
mise use go@1.21

# List installed versions
mise ls

# Uninstall
mise uninstall go@1.21
```

## 4. Advanced Features

### 4.1 Environment Variable Management

```toml
# .mise.toml
[env]
_.path = ["./bin", "{{config_root}}/scripts"]
API_KEY = "secret"
```

### 4.2 Task Runner

```toml
# .mise.toml
[tasks.build]
description = "Build the project"
run = "make build"

[tasks.test]
description = "Run tests"
run = "go test ./..."
```

### 4.3 Replacing direnv

Mise supports `.envrc` files, fully replacing direnv:

```sh
mise activate direnv
```

Then in `.envrc`:

```bash
use go
use node
```

## Summary

Mise is a powerful toolchain manager with these advantages:

- ✅ Multi-language support (Go, Node.js, Python, Java, Rust, and more)
- ✅ Project-level and global configuration
- ✅ Environment variable management
- ✅ Built-in task runner
- ✅ Compatible with the asdf plugin ecosystem
- ✅ Great performance (written in Rust)
