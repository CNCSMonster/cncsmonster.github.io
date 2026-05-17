+++
title = "Python Package Management with UV"
date = 2025-01-03T00:22:09+08:00
tags = ["Python", "UV", "Package Management", "Toolchain"]
+++

UV is a blazing-fast Python package and project manager written in Rust.

## Reference

- [astral-sh/uv](https://github.com/astral-sh/uv)

## Installation

```bash
# Using pip
pip install uv

# Or using the standalone installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using cargo
cargo install uv
```

## Using UV to Run Python Projects

```bash
# Navigate to the project root first
# Initialize UV project configuration
uv init

# Add dependencies
uv add <package-name>

# Run a Python script
uv run python script.py

# Run arbitrary commands
uv run <command>
```

## Common Commands

```bash
# Create a virtual environment
uv venv

# Install packages
uv pip install <package>

# Export dependencies
uv pip compile requirements.in -o requirements.txt

# Sync dependencies
uv pip sync requirements.txt

# Show dependency tree
uv pip tree
```

## Advantages

- 🚀 **Blazing fast**: 10–100× faster than pip
- 📦 **Compatible**: Fully compatible with pip and requirements.txt
- 🔧 **All-in-one**: Combines venv, pip, and pip-tools functionality
- 🦀 **Rust**: Built with Rust — stable and reliable
