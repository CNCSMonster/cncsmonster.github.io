+++
title = "Dotfiles — My Development Environment Configuration"
date = 2026-04-07T00:00:00+08:00
tags = ["Dotfiles", "Dev Environment", "Automation"]
weight = 1
+++

**A collection of development environment configurations — set up a complete dev environment with one command.**

## What Problem Does This Solve?

You get a new machine (or reinstall the OS). How do you quickly restore your familiar development environment?

Install software and configure files one by one? That takes hours or even days.

## The Solution

This project is an **automated development environment setup script**.

- **One-command deploy** — `./setup.sh` handles everything automatically
- **Complete toolchain** — Helix, Zsh, Rust, Go, Node.js, and more
- **Reproducible** — pinned versions ensure consistent setups

You can:
- **Use it directly** — get an environment matching mine
- **Learn from it** — see how dotfiles can be organized
- **Customize it** — fork it and build your own

## Quick Start

```bash
git clone https://github.com/cncsmonster/dotfiles.git
cd dotfiles && ./setup.sh
```

Completes in ~20–50 minutes depending on machine specs and network speed.

## Project Link

- **GitHub**: [cncsmonster/dotfiles](https://github.com/cncsmonster/dotfiles)

---

Star and PRs welcome! ⭐
