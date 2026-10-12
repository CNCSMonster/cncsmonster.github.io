+++
title = "Browser Automation MCP Decision: chrome-devtools-mcp vs. Obscura"
date = 2026-09-17T00:00:00+08:00
slug = "browser-automation-mcp-chrome-devtools-vs-obscura"
[taxonomies]
    tags = ["MCP", "Browser Automation", "Chrome", "Agent"]
+++

When equipping an AI coding agent with browser automation capabilities, developers must balance **human-agent collaboration**, **memory overhead**, and **bot-detection resilience**. This post evaluates Google's official `chrome-devtools-mcp` against `Obscura`, a lightweight headless browser built with Rust and V8.

## The Core Verdict

These two tools serve fundamentally different workflows:

- **`chrome-devtools-mcp` is a visual collaborative workspace**: It drives a real desktop Chrome instance. Because a visible desktop window is available, you can observe the agent's actions in real time and **take turns interacting with the browser** (e.g., handling complex filtering, approving security dialogs, or passing CAPTCHAs by hand before letting the agent resume). It also reuses existing login sessions from your everyday Chrome profile. The tradeoff is **heavy memory consumption (~1.5 GB per instance)**.
- **`Obscura` is a silent background batch-runner**: A headless runtime built on Rust + V8, stripped of any GUI frontend. **It does not open desktop windows and cannot support live co-browsing**; however, it has an **exceptionally small memory footprint (idle at just 23 MB, 98% lower)** and conceals obvious headless indicators like `navigator.webdriver`. It is ideal for quiet background documentation lookups, data scraping, and basic form automation.

### Feature Comparison

| Dimension | chrome-devtools-mcp (Official) | Obscura (Rust + V8) |
| :--- | :--- | :--- |
| **Collaboration** | **Visible desktop window**: Human and agent can share the browser session turn-by-turn | **Headless only**: Runs silently in the background without UI handoff |
| **Memory Footprint** | Heavy (idle ~1450 MB, easily stresses concurrent compiler workloads) | **Minimal (idle ~23 MB)** |
| **Bot Detection** | Headless Chrome exposes obvious flags (`webdriver=true`, `HeadlessChrome` in UA) | **Built-in stealth** (masks `webdriver`, synthesizes consistent fake profile) |
| **Form Interactions** | Full support for typing, clicking, navigating, and logging in | Full support for typing, clicking, navigating, and logging in |
| **Session Inheritance** | Can attach to your existing local Chrome profile (reuses logged-in cookies) | Isolated sandbox; cannot directly inherit desktop profiles |
| **Recommendation** | Use when co-browsing, session reuse, or deep DevTools diagnostics are required | Best for concurrent agents, background docs fetching, and mass crawling |

## Benchmark Data

Environment: WSL2 / Ubuntu 24.04, target URL: `example.com`.

### 1. Memory Usage

| State | Obscura `serve` | Chrome headless |
| :---: | :---: | :---: |
| Idle | **23 MB** (1 process) | 1452 MB (14 processes) |
| Post Page Load | **26 MB** | 1561 MB (15 processes) |

The 50x–60x gap in memory footprint is real. While running heavy compilation jobs or orchestrating multiple concurrent sub-agents, Chrome headless can quickly starve system RAM.

### 2. Fingerprinting & Bot Detection

Default headless Chrome leaks two glaring signals:

- `navigator.webdriver === true`
- User-Agent prominently displaying `HeadlessChrome`

Many websites block incoming traffic based on these two checks alone. When started with `--stealth`, Obscura resets `navigator.webdriver` to `false` and presents a consistent Windows / Chrome 145 fingerprint. Note, however, that `getContext('webgl')` evaluates to `null`, which advanced anti-bot systems may still flag.

## Setup & Configuration

### 1. chrome-devtools-mcp

```jsonc
"chrome-devtools": {
  "command": "npx",
  "args": ["-y", "chrome-devtools-mcp@latest"],
  "description": "Chrome DevTools MCP"
}
```

> Defaults to headed mode (visible window). Append `--headless` if you prefer silent execution. Requires local Chrome.

### 2. Obscura Setup

```bash
# Download and unpack the prebuilt stealth binary into ~/.local/bin
curl -L -o obscura.tar.gz "https://github.com/h4ckf0r0day/obscura/releases/download/v0.2.2/obscura-x86_64-linux-stealth.tar.gz"
tar -xzf obscura.tar.gz
mkdir -p ~/.local/bin && mv obscura obscura-worker ~/.local/bin/
chmod +x ~/.local/bin/obscura ~/.local/bin/obscura-worker
```

MCP server configuration:

```jsonc
"obscura": {
  "command": "obscura",
  "args": ["mcp", "--stealth", "--allow-private-network"],
  "description": "Obscura lightweight headless browser MCP"
}
```

> **Clash TUN Mode Gotcha**:  
> In TUN mode, Clash's fake-ip resolver maps all domains to `198.18.x.x`. This triggers Obscura's internal SSRF guard and cuts off outbound requests. Passing `--allow-private-network` is mandatory in such environments to allow normal web access.
