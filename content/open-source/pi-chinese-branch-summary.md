+++
title = 'Pi 会话分支摘要本地化设计与扩展实现'
date = 2026-10-12T02:22:55+08:00
tags = ['Pi', 'Agent', '本地化', '扩展开发']
weight = 10
+++

## 1. 这篇讲什么

分析 Pi Coding Agent 在执行会话树分支切换（`/tree` 回溯）时生成英文摘要的底层机理，并基于官方 `session_before_tree` 扩展生命周期事件，设计并落地全局中文摘要指令替换方案。

## 2. 问题背景与现象

在中文技术研发与文档撰写会话中，当用户使用 `/tree` 切换并回溯分支会话时，Pi 会在会话历史中插入一段 `<summary>` 节点作为上下文压缩记忆。

虽然对话全程使用中文，但自动生成的摘要仍强制采用英文结构与英文标题：

```markdown
<summary>
The user explored a different conversation branch before returning here.
Summary of that exploration:

## Goal
[What was the user trying to accomplish in this branch?]

## Constraints & Preferences
- [Any constraints, preferences, or requirements mentioned]
...
```

原生英文摘要虽然逻辑准确，但在中文语境下存在阅读门槛。全中文结构化 Prompt 旨在提供零摩擦的阅读体验，确保技术复盘时的信息获取效率。

## 3. 源码机制探针

Pi 为完全开源项目（官方仓库：[earendil-works/pi](https://github.com/earendil-works/pi)）。经查阅其核心源码实现，厘清了分支摘要生成的底层机制：

### 3.1 默认 Prompt 硬编码

在核心模块 `packages/coding-agent/src/core/compaction/branch-summarization.ts:258` 中，Pi 定义了默认的常量模板 `BRANCH_SUMMARY_PROMPT`：

```typescript
const BRANCH_SUMMARY_PROMPT = `Create a structured summary of this conversation branch for context when returning later.

Use this EXACT format:

## Goal
[What was the user trying to accomplish in this branch?]

## Constraints & Preferences
- [Any constraints, preferences, or requirements mentioned]
- [Or "(none)" if none were mentioned]

## Progress
### Done
- [x] [Completed tasks/changes]

### In Progress
- [ ] [Work that was started but not finished]

### Blocked
- [Issues preventing progress, if any]

## Key Decisions
- **[Decision]**: [Brief rationale]

## Next Steps
1. [What should happen next to continue this work]

Keep each section concise. Preserve exact file paths, function names, and error messages.`;
```

无论当前系统环境语言或用户交互语言为何，系统默认均使用该英文模板组装提示词，投递至摘要模型。

### 3.2 官方扩展劫持链路与时序流向

在分支切换确认后、发起模型摘要调用前，Pi 内核会通过事件总线向扩展层广播生命周期事件。整体协作时序如下：

<div align="center" style="margin: 20px 0;">
<svg viewBox="0 0 800 400" width="100%" height="auto" style="max-width: 800px; font-family: system-ui, -apple-system, sans-serif; background: transparent; border-radius: 8px; border: 1px solid rgba(128,128,128,0.25);" xmlns="http://www.w3.org/2000/svg">
<defs>
<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#38bdf8"/></marker>
<marker id="arrow-orange" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#fb923c"/></marker>
<marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#c084fc"/></marker>
<marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#4ade80"/></marker>
</defs>
<text x="400" y="30" text-anchor="middle" fill="currentColor" font-size="14" font-weight="600" opacity="0.9">Pi 会话分支中文摘要拦截与生成时序</text>
<line x1="110" y1="70" x2="110" y2="365" stroke="rgba(128,128,128,0.3)" stroke-dasharray="4,4" stroke-width="1.5"/>
<line x1="300" y1="70" x2="300" y2="365" stroke="rgba(128,128,128,0.3)" stroke-dasharray="4,4" stroke-width="1.5"/>
<line x1="510" y1="70" x2="510" y2="365" stroke="rgba(128,128,128,0.3)" stroke-dasharray="4,4" stroke-width="1.5"/>
<line x1="700" y1="70" x2="700" y2="365" stroke="rgba(128,128,128,0.3)" stroke-dasharray="4,4" stroke-width="1.5"/>
<rect x="55" y="45" width="110" height="30" rx="6" fill="rgba(56,189,248,0.15)" stroke="#38bdf8" stroke-width="1.5"/>
<text x="110" y="65" text-anchor="middle" fill="#38bdf8" font-size="12" font-weight="600">用户 / TUI</text>
<rect x="240" y="45" width="120" height="30" rx="6" fill="rgba(192,132,252,0.15)" stroke="#c084fc" stroke-width="1.5"/>
<text x="300" y="65" text-anchor="middle" fill="#c084fc" font-size="12" font-weight="600">Pi 扩展层</text>
<rect x="450" y="45" width="120" height="30" rx="6" fill="rgba(251,146,60,0.15)" stroke="#fb923c" stroke-width="1.5"/>
<text x="510" y="65" text-anchor="middle" fill="#fb923c" font-size="12" font-weight="600">Pi 内核引擎</text>
<rect x="645" y="45" width="110" height="30" rx="6" fill="rgba(74,222,128,0.15)" stroke="#4ade80" stroke-width="1.5"/>
<text x="700" y="65" text-anchor="middle" fill="#4ade80" font-size="12" font-weight="600">摘要模型 LLM</text>
<line x1="110" y1="100" x2="500" y2="100" stroke="#38bdf8" stroke-width="1.5" marker-end="url(#arrow)"/>
<text x="305" y="93" text-anchor="middle" fill="#38bdf8" font-size="11">1. 触发 /tree 分支导航</text>
<line x1="510" y1="140" x2="310" y2="140" stroke="#fb923c" stroke-width="1.5" marker-end="url(#arrow-orange)"/>
<text x="410" y="133" text-anchor="middle" fill="#fb923c" font-size="11">2. 广播 session_before_tree</text>
<line x1="300" y1="180" x2="500" y2="180" stroke="#c084fc" stroke-width="1.5" marker-end="url(#arrow-purple)"/>
<text x="400" y="173" text-anchor="middle" fill="#c084fc" font-size="11">3. 返回 { replaceInstructions: true, customInstructions }</text>
<rect x="425" y="205" width="235" height="32" rx="6" fill="rgba(234,179,8,0.12)" stroke="#eab308" stroke-width="1"/>
<text x="542" y="220" text-anchor="middle" fill="#eab308" font-size="11" font-weight="600">4. 判定决策分支</text>
<text x="542" y="232" text-anchor="middle" fill="currentColor" opacity="0.75" font-size="9">彻底覆盖英文模板 · 保留内核预算与重试</text>
<line x1="510" y1="260" x2="690" y2="260" stroke="#fb923c" stroke-width="1.5" marker-end="url(#arrow-orange)"/>
<text x="600" y="253" text-anchor="middle" fill="#fb923c" font-size="11">5. 调度 LLM 发起摘要请求</text>
<line x1="700" y1="300" x2="520" y2="300" stroke="#4ade80" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arrow-green)"/>
<text x="610" y="293" text-anchor="middle" fill="#4ade80" font-size="11">6. 流式返回纯中文结构化摘要</text>
<line x1="510" y1="340" x2="120" y2="340" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
<text x="310" y="333" text-anchor="middle" fill="#38bdf8" font-size="11">7. 写入 &lt;summary&gt; 节点完成分支回溯</text>
</svg>
</div>

## 4. 方案设计与选型

针对本地化需求，存在三种技术路线：

| 方案 | 原理 | 优点 | 缺点 | 结论 |
|------|------|------|------|:----:|
| **A. 源码补丁** | 直接 patch npm 全局安装包代码 | 最彻底，不依赖插件系统 | 直接改写内核源码，宿主升级后即失效 | ❌ 废弃 |
| **B. 扩展提供 summary** | 扩展中拦截并自行调用外部模型完成摘要 | 自由度最高 | 产生额外模型配置负担，破坏内置 token 预算与流式控制 | ❌ 废弃 |
| **C. 指令完全置换（本方案）** | 利用 `session_before_tree` 注入 `replaceInstructions: true`，内核据此彻底覆盖内置英文模板为中文 Prompt | 复用 Pi 内核所有重试、预算截断与已鉴权模型调用能力；只依赖公开事件契约，宿主升级不易失效 | 仅在有对应事件支持的 Pi 版本中生效 | ✅ 采用 |

## 5. 核心机制契约与工程化交付

### 5.1 最小扩展契约（Minimal Contract）

根据方案 C 的决策，扩展的职责仅限于**在事件触发时完成指令拦截与替换**，绝不介入底层的模型推理与网络通信。

核心契约仅需在 `session_before_tree` 阶段返回控制元组：

```typescript
pi.on("session_before_tree", async () => {
    return {
        replaceInstructions: true,                     // 必填：声明彻底覆盖默认英文模板
        customInstructions: CHINESE_BRANCH_SUMMARY_PROMPT // 注入等价中译模板
    };
});
```


### 5.2 提示词结构设计

中文 Prompt 采用与 Pi 原生模板**1:1 同构**的翻译策略，以保持总结的逻辑密度与阅读体验。

**设计要求**：

- **骨架一致**：保留 `## 目标`、`## 约束与偏好`、`## 进展`、`## 关键决策`、`## 下一步` 五个板块；
- **层级统一**：维持二级标题结构，利用 Markdown 折叠特性提升可读性。

### 5.3 实现源码

完整实现见开源仓库：

- 仓库：[CNCSMonster/pi-chinese-branch-summary](https://github.com/CNCSMonster/pi-chinese-branch-summary)

## 6. 架构启示：改指令不改引擎

本方案沉淀出的“改指令不改引擎（Instruction Replacement over Engine Takeover）”模式具有长期的可复用价值：

1. **最小侵入性**：当宿主（Harness）已具备完备的预算管理、重试与网络流水线时，扩展应优先寻找“提示词/参数替换点”，而非“逻辑替代点”；
2. **向前兼容性**：扩展应只依赖宿主公开的事件与参数契约，不触碰其内部实现；契约保持稳定时，宿主的内部重构与版本升级都不需要扩展跟着改；
