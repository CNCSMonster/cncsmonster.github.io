+++
title = "浏览器自动化 MCP 选型：chrome-devtools-mcp 与 Obscura"
date = 2026-09-17T00:00:00+08:00
slug = "browser-automation-mcp-chrome-devtools-vs-obscura"
[taxonomies]
    tags = ["MCP", "Browser Automation", "Chrome", "Agent"]
+++

给 AI coding agent 配置浏览器访问能力时，核心要在**人机协作体验**、**内存占用**与**反爬表现**之间做权衡。本文对比 Google 官方的 `chrome-devtools-mcp` 与轻量 Rust 实现的 `Obscura`。

## 选型结论

两者在使用体验和定位上是完全不同的两类工具：

- **chrome-devtools-mcp 是“可视化协作工作台”**：它直接运行桌面真实 Chrome。桌面上有可见窗口，你能实时看着 AI 点选，人和 AI 可以**同屏接力操作**（遇到复杂筛选、内部权限确认或验证时，你随手拿鼠标帮 AI 操作一步，AI 接着往下跑；也能直接复用你电脑日常已登录的 Cookie）。代价是**极其吃内存（单实例约 1.5 GB）**。
- **Obscura 是“后台静默批处理工具”**：它是纯 Rust + V8 的无头运行时，专为静默脚本设计。**完全没有桌面窗口，无法直接人机同屏接力**；但**内存极其轻巧（仅 23 MB，降了 98%）**，且自带伪装抹平了 `webdriver` 特征。适合跑在后台安安静静抓数据、查文档、填常规表单。

### 核心对比一览

| 维度 | chrome-devtools-mcp（Google 官方） | Obscura（Rust + V8） |
| :--- | :--- | :--- |
| **协作体验** | **支持桌面可见窗口**：人与 AI 可同屏接力（人操作一步、AI 接着操作） | **无桌面窗口**：纯后台黑盒运行，无法直接接管操作 |
| **内存开销** | 极重（空闲约 1450 MB，容易影响本地编译并发） | **极轻（空闲仅 23 MB）** |
| **反爬特征** | 原生 headless 漏洞明显（`webdriver=true`，UA 带 `HeadlessChrome`） | **自带伪装（隐藏 webdriver，模拟自洽假身份）** |
| **表单与交互** | 完整支持表单录入、点击、导航、账号登录 | 完整支持表单录入、点击、导航、账号登录 |
| **会话继承** | 支持直接挂载本地日常 Chrome Profile（直接复用已有 Cookie） | 纯沙箱环境，无法继承本地日常登录态 |
| **使用建议** | 需要同屏接力、复用日常登录态、做前端深度性能诊断时选用 | 后台批量查文档、抓取网页、自动化填表、多 Agent 并发时首选 |

## 关键实测数据

测试环境：WSL2 / Ubuntu 24.04，测试目标为 `example.com`。

### 1. 内存实测

| 运行状态 | Obscura `serve` | Chrome headless |
| :---: | :---: | :---: |
| 空闲状态 | **23 MB**（1 进程） | 1452 MB（14 进程） |
| 页面加载后 | **26 MB** | 1561 MB（15 进程） |

两者有约 50~60 倍的量级差异。在机器跑大型编译任务或多 Agent 并发访问时，Chrome 对系统资源的抢占非常明显。

### 2. 反爬指纹实测

Chrome 原生 headless 有两个最经典的特征暴露点：

- `navigator.webdriver === true`；
- User-Agent 明晃晃带着 `HeadlessChrome`。

很多站点以此直接拦截流量。Obscura 开启 `--stealth` 后，将 `webdriver` 抹平为 `false`，并输出了一套自洽的 Windows / Chrome 145 身份配置。但需注意其实测 `getContext('webgl')` 返回 `null`，面对高阶硬件级 WAF 仍有暴露可能。

## 快速配置

### 1. chrome-devtools-mcp

```jsonc
"chrome-devtools": {
  "command": "npx",
  "args": ["-y", "chrome-devtools-mcp@latest"],
  "description": "Chrome DevTools MCP"
}
```

> 默认即为有头模式（可见窗口）；若希望纯后台静默，可追加 `--headless`。要求本机已安装桌面 Chrome。

### 2. Obscura（安装与配置）

```bash
# 下载 stealth 预编译包解压至 ~/.local/bin
curl -L -o obscura.tar.gz "https://github.com/h4ckf0r0day/obscura/releases/download/v0.2.2/obscura-x86_64-linux-stealth.tar.gz"
tar -xzf obscura.tar.gz
mkdir -p ~/.local/bin && mv obscura obscura-worker ~/.local/bin/
chmod +x ~/.local/bin/obscura ~/.local/bin/obscura-worker
```

MCP 配置：

```jsonc
"obscura": {
  "command": "obscura",
  "args": ["mcp", "--stealth", "--allow-private-network"],
  "description": "Obscura lightweight headless browser MCP"
}
```

> **避坑提示（Clash TUN 模式）**：  
> 若本机开启了 Clash TUN 模式，fake-ip 机制会将域名解析到 `198.18.x.x`，会撞上 Obscura 内置的 SSRF 防护而断网。配置中必须传入 `--allow-private-network` 才能正常联网。
