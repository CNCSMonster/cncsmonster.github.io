+++
title = "gen-mdbook-summary — Auto-generate mdBook SUMMARY.md"
date = 2026-04-07T00:00:00+08:00
tags = ["Rust", "mdBook", "Open Source", "Tool"]
weight = 3
+++

**A tool that automatically generates SUMMARY.md for mdBook projects.**

## What Problem Does This Solve?

Writing a technical book with mdBook — every new chapter means manually editing `SUMMARY.md`?

As chapters grow, keeping the table of contents in sync becomes tedious and error-prone.

## The Solution

This tool **scans your directory structure and generates SUMMARY.md** automatically.

- **Auto-scan** — recursively scans the target directory
- **Smart filtering** — supports `.gmsignore` files
- **One-command generation** — `gms -d src -o src/SUMMARY.md`

## Quick Start

```bash
cargo install gen-mdbook-summary
gms -d src -o src/SUMMARY.md
```

## Project Links

- **GitHub**: [cncsmonster/gen-mdbook-summary](https://github.com/cncsmonster/gen-mdbook-summary)
- **crates.io**: [gen-mdbook-summary](https://crates.io/crates/gen-mdbook-summary)
