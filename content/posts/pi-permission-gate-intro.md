+++
title = "给 Pi 编码代理加一道安全门：pi-permission-gate"
date = 2026-05-30T00:00:00+08:00
slug = "pi-permission-gate-security-extension"
tags = ["Pi", "Extension", "Security", "Code Agent"]
+++

> 如果你用 Pi 写代码时担心误删文件、泄露密钥，试试 `pi-permission-gate` —— 一个基于规则的权限拦截扩展，敏感操作先确认，危险命令自动拒。

## 一句话

为 Pi 代理配置规则，拦截对敏感文件的读写和执行危险命令。不替代安全审计，只做一件事：**操作前问一下**。

## 能做什么

| ✅ 拦截 | ❌ 不做 |
|--------|---------|
| 读取 `~/.ssh/` 私钥 | 审计日志记录 |
| 读取 `.env` 环境变量 | MCP 权限控制 |
| 执行 `rm -rf` 命令 | 子代理权限转发 |
| 修改项目外的文件 | 复杂策略引擎 |

## 安装

```bash
pi install git:github.com/CNCSMonster/pi-permission-gate
```

## 配置

### 全局规则（安全基线）

创建 `~/.pi/agent/permission-rules.json`：

```json
{
  "defaultAction": "ask",
  "rules": [
    {
      "tools": ["read"],
      "pathPattern": "**/.ssh/**",
      "label": "SSH 私钥",
      "action": "deny"
    },
    {
      "tools": ["bash"],
      "pathPattern": "**/rm -rf *",
      "label": "危险删除",
      "action": "deny"
    }
  ]
}
```

### 项目规则（灵活特化）

创建 `<项目>/.pi/permission-rules.json`：

```json
{
  "trustedPaths": ["./data", "./tmp"],
  "rules": [
    {
      "tools": ["read", "write", "edit"],
      "pathPattern": "**/*",
      "label": "项目文件",
      "action": "allow"
    }
  ]
}
```

配置修改后立即生效，无需重启 pi。

## 使用体验

当代理尝试访问敏感文件时：

```
⚠️ 敏感操作 — SSH 私钥

规则: **/.ssh/**
工具: read
目标: /home/user/.ssh/id_rsa

允许吗？
[允许本次] [始终允许] [拒绝本次] [始终拒绝]
```

- **始终允许/拒绝**：记住选择，后续自动处理
- **允许/拒绝本次**：仅影响当前操作

## 为什么简单

与 `pi-permission-system`（另一个权限扩展）对比：

| | pi-permission-system | pi-permission-gate |
|--|---------------------|-------------------|
| 功能 | 全面（MCP、审计、子代理） | 精简（文件 + 命令） |
| 配置 | JSON schema + YAML | 简单 JSON + glob |
| 代码量 | ~2000 行 | ~380 行 |
| 适用 | 团队/企业 | 个人开发者 |

如果你只需要"操作前确认一下"，`pi-permission-gate` 更简单直接。

## 为什么是规则而非 AI

安全决策需要**确定性**：

- 规则引擎：100% 可预测，毫秒级响应
- AI 判断：可能不一致，需要 API 调用

"大概应该允许"不够好，安全需要"明确允许或拒绝"。

## GitHub

[CNCSMonster/pi-permission-gate](https://github.com/CNCSMonster/pi-permission-gate)

MIT 许可证，欢迎试用和反馈。
