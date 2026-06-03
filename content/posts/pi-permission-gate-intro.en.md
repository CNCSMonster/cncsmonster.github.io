+++
title = "Add a Security Gate to Your Pi Coding Agent: pi-permission-gate"
date = 2026-05-30T00:00:00+08:00
slug = "pi-permission-gate-security-extension"
tags = ["Pi", "Extension", "Security", "Code Agent"]
+++

> Worried about accidentally deleting files or leaking API keys while using Pi? Try `pi-permission-gate` — a rule-based permission interceptor that asks before sensitive operations and blocks dangerous commands automatically.

## In One Sentence

Configure rules for your Pi agent to intercept reads/writes on sensitive files and block dangerous commands. It doesn't replace security audits, but does one thing well: **ask before acting**.

## What It Can Do

| ✅ Intercepts | ❌ Doesn't Do |
|--------------|--------------|
| Reading `~/.ssh/` private keys | Audit logging |
| Reading `.env` environment files | MCP permission control |
| Executing `rm -rf` commands | Sub-agent permission forwarding |
| Modifying files outside the project | Complex policy engine |

## Installation

```bash
pi install git:github.com/CNCSMonster/pi-permission-gate
```

## Configuration

### Global Rules (Security Baseline)

Create `~/.pi/agent/permission-rules.json`:

```json
{
  "defaultAction": "ask",
  "rules": [
    {
      "tools": ["read"],
      "pathPattern": "**/.ssh/**",
      "label": "SSH private keys",
      "action": "deny"
    },
    {
      "tools": ["bash"],
      "pathPattern": "**/rm -rf *",
      "label": "Dangerous deletion",
      "action": "deny"
    }
  ]
}
```

### Project Rules (Flexible Overrides)

Create `<project>/.pi/permission-rules.json`:

```json
{
  "trustedPaths": ["./data", "./tmp"],
  "rules": [
    {
      "tools": ["read", "write", "edit"],
      "pathPattern": "**/*",
      "label": "Project files",
      "action": "allow"
    }
  ]
}
```

Configuration changes take effect immediately without restarting pi.

## User Experience

When the agent tries to access a sensitive file:

```
⚠️ Sensitive Operation — SSH private keys

Rule: **/.ssh/**
Tool: read
Target: /home/user/.ssh/id_rsa

Allow?
[Allow Once] [Always Allow] [Deny Once] [Always Deny]
```

- **Always Allow/Deny**: Remember choice, auto-process next time
- **Allow/Deny Once**: Only affects current operation

## Why Keep It Simple

Comparison with `pi-permission-system` (another permission extension):

| | pi-permission-system | pi-permission-gate |
|--|---------------------|-------------------|
| Features | Full (MCP, audit, sub-agents) | Lean (files + commands) |
| Config | JSON schema + YAML | Simple JSON + glob |
| Code | ~2000 lines | ~380 lines |
| Use Case | Teams/Enterprise | Individual developers |

If you just need "ask before acting," `pi-permission-gate` is simpler and more direct.

## Why Rules, Not AI

Security decisions need **determinism**:

- Rule engine: 100% predictable, millisecond response
- AI judgment: May be inconsistent, requires API calls

"Probably should allow" isn't good enough. Security needs explicit allow or deny.

## GitHub

[CNCSMonster/pi-permission-gate](https://github.com/CNCSMonster/pi-permission-gate)

MIT licensed. Feedback welcome.
