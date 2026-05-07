+++
title = "Qwen Code 接入 Tavily 搜索"
date = 2026-05-05T00:00:00+08:00
slug = "qwen-code-tavily-mcp-setup"
tags = ["Qwen Code", "MCP", "Tavily"]
+++

## 1. 获取 API Key

注册 [Tavily](https://tavily.com/)，复制 API key。

## 2. 设置环境变量

将 `TAVILY_API_KEY` 持久化到系统环境变量中（`tvly-xxxxxxxx` 替换为你的 key）。

**Linux / macOS：**

```bash
echo 'export TAVILY_API_KEY="tvly-xxxxxxxx"' >> ~/.profile
source ~/.profile
```

> 如果之前已经设置过，用编辑器打开 `~/.profile` 替换或删除旧值，避免重复行。

**Windows（PowerShell）：**

```powershell
[Environment]::SetEnvironmentVariable("TAVILY_API_KEY", "tvly-xxxxxxxx", "User")
```

无需管理员权限。这个命令会写入当前用户的持久化环境变量，但不会修改已经打开的 PowerShell 进程；关闭并重新打开终端后生效。

重新打开 PowerShell 后可验证：

```powershell
$env:TAVILY_API_KEY
```

如果想在当前这个 PowerShell 窗口里立刻继续测试，也可以临时同步一次：

```powershell
$env:TAVILY_API_KEY = [Environment]::GetEnvironmentVariable("TAVILY_API_KEY", "User")
```

> API key 涉及付费额度，自己手动执行以上命令，不要让 AI 代劳。

## 3. 安装 Tavily MCP

发给 Qwen Code：

```
请帮我用 qwen mcp add 命令安装 Tavily MCP，然后搜索验证是否正常。
```

结束。

---

> 验证时间：2026-05-05，Qwen Code 0.15.6 + tavily-mcp 0.2.19
