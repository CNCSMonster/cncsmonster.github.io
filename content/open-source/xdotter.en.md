+++
title = "xdotter — A Lightweight Dotfile Manager"
date = 2026-04-07T00:00:00+08:00
tags = ["Python", "Open Source", "Dotfile Management"]
weight = 2
+++

**Zero-dependency, single-file dotfile manager.**

## What Problem Does This Solve?

New machine — how do you quickly restore all your config files (`.bashrc`, `.gitconfig`, etc.)?

Copy them manually? Easy to miss something. Use existing tools? Complex dependencies, tedious setup.

## The Solution

xdotter's answer: **one config folder + symlinks**.

- **Zero dependencies** — single `.pyz` file, download and run
- **Declarative config** — TOML file defines the mapping
- **One-command deploy** — `xd deploy` creates all symlinks

Compared to dotter:
- **Simpler** — symlinks only, no copy/other deployment modes
- **Zero deps** — no Rust compilation needed, Python comes pre-installed
- **Intuitive config** — single TOML file, no complex templating

## Quick Start

```bash
# Download
gh release download --repo cncsmonster/xdotter --pattern xd.pyz --output ~/.local/bin/xd

# Create config and deploy
xd new && xd deploy
```

## Project Link

- **GitHub**: [cncsmonster/xdotter](https://github.com/cncsmonster/xdotter)

---

Stars, issues, and PRs welcome! ⭐
