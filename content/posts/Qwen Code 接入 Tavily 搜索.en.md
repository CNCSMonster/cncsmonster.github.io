+++
title = "Getting Qwen Code to Work with Tavily Search"
date = 2026-05-05T00:00:00+08:00
slug = "qwen-code-tavily-mcp-setup"
tags = ["Qwen Code", "MCP", "Tavily"]
+++

## 1. Get an API Key

Sign up at [Tavily](https://tavily.com/) and copy your API key.

## 2. Set the Environment Variable

Persist `TAVILY_API_KEY` as a system environment variable (replace `tvly-xxxxxxxx` with your actual key).

**Linux / macOS:**

```bash
echo 'export TAVILY_API_KEY="tvly-xxxxxxxx"' >> ~/.profile
source ~/.profile
```

> If you've already set this before, open `~/.profile` in an editor to replace or remove the old entry — avoid duplicate lines.

**Windows (PowerShell):**

```powershell
[Environment]::SetEnvironmentVariable("TAVILY_API_KEY", "tvly-xxxxxxxx", "User")
```

No admin privileges required. This writes a persistent environment variable for the current user, but doesn't modify the already-open PowerShell process — close and reopen the terminal for it to take effect.

After reopening PowerShell, verify:

```powershell
$env:TAVILY_API_KEY
```

If you want to continue testing immediately in the current PowerShell window without reopening, sync it once:

```powershell
$env:TAVILY_API_KEY = [Environment]::GetEnvironmentVariable("TAVILY_API_KEY", "User")
```

> Your API key grants access to a paid tier. Run the commands above yourself — don't let an AI agent do it for you.

## 3. Install Tavily MCP

Tell Qwen Code:

```
Please install Tavily MCP using the qwen mcp add command, then search for something to verify it works.
```

Done.

---

> Verified: 2026-05-05, Qwen Code 0.15.6 + tavily-mcp 0.2.19
