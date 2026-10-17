+++
title = 'Pi 会话摘要本地化设计与扩展实现'
date = 2026-10-12T02:22:55+08:00
updated = 2026-10-17T00:00:00+08:00
tags = ['Pi', 'Agent', '本地化', '扩展开发']
weight = 10
+++

## 1. 这篇讲什么

Pi 会在会话里自动写入**两类**结构化摘要，且两类都写死英文模板：用 `/tree` 回溯分支时写入的**分支回溯摘要**，以及会话变长触发压缩时写入的**上下文压缩摘要**（compaction）。结果是中文会话里冒出英文小标题。

本文拆开两条链路的机制，给出各自的中文化方案：分支摘要走**指令置换**（只换提示词），压缩摘要走**接管式交成品**（内核没有换词档，扩展只能自己调模型再交回去）。

## 2. 问题背景与现象

**现象一：分支回溯。** 在中文技术研发与文档撰写会话中，使用 `/tree` 切换并回溯分支时，Pi 会在会话历史中插入一段 `<summary>` 节点作为上下文记忆。虽然对话全程中文，摘要仍强制采用英文结构：

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

**现象二：上下文压缩。** 长会话里，上下文接近窗口上限（或手动 `/compact`）时，Pi 会把较早的历史折叠成一段检查点摘要，后续只带"系统提示 + 摘要 + 近期消息"。这段摘要同样是英文骨架：

```markdown
## Goal
## Constraints & Preferences
## Critical Context
```

两类摘要出现在同一条中文会话里，读起来是连续的中英混排。原生英文摘要逻辑没问题，但中文语境下多了一层阅读门槛。

## 3. 源码机制探针

Pi 为完全开源项目（官方仓库：[earendil-works/pi](https://github.com/earendil-works/pi)）。以下行号对照本机安装的 v1.0.4 `dist/` 实测。

### 3.1 分支回溯：默认提示词硬编码

分支摘要模板是核心里的常量 `BRANCH_SUMMARY_PROMPT`（`dist/core/compaction/branch-summarization.js`）：

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

与系统环境语言、用户交互语言均无关，内核默认用这份英文模板组装提示词。

### 3.2 分支回溯的劫持链路与时序

分支切换确认后、发起摘要模型调用前，内核通过事件总线向扩展层广播生命周期事件。整体时序如下：

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

### 3.3 上下文压缩：三个触发口、一份写死的英文模板

- **触发口**（`dist/core/agent-session.js`）：手动 `/compact`（`reason="manual"`，:2221）、上下文达阈值（`"threshold"`，:2512）等自动档。
- **模板**（`dist/core/compaction/compaction.js`）：主提示 `SUMMARIZATION_PROMPT`（:379）写明 "Use this EXACT format"；另有迭代更新用的 `UPDATE_SUMMARIZATION_PROMPT`（:447）与 split 前缀用的 `TURN_PREFIX_SUMMARIZATION_PROMPT`（:663）。

即：压缩摘要用英文还是中文，跟会话语言无关，只跟核心模板有关。

### 3.4 关键差异：一条有「换词档」，一条没有

| 维度 | 分支回溯（`session_before_tree`） | 上下文压缩（`session_before_compact`） |
|---|---|---|
| 结果契约 | `SessionBeforeTreeResult`：可传 `customInstructions` + `replaceInstructions` | `SessionBeforeCompactResult`：只有 `cancel` 与 `compaction` |
| 语义 | **换词档**：内核照跑自己的管线，只把提示词换掉 | **交成品档**：要么掐断，要么把整份摘要交给内核 |
| 扩展的最小职责 | 递一份中文提示词 | 自己调模型生成摘要，并回填契约字段 |

（行号：`dist/core/extensions/types.d.ts:1102`（compact 结果）/ `:1106-1116`（tree 结果））

一句话：**分支摘要可以"只换词"，压缩摘要只能"自己算完交卷"。**

### 3.5 失败即回退：降级，而不是损坏

内核消费的是 `result?.compaction`（`agent-session.js:2201`），为空就走 `_runDefaultCompaction`（:2140）跑英文默认；扩展 handler 抛错由事件总线捕获后仅上报、不中断流程，结果保持 undefined → 同样回退。

也就是说：**拿不准就让内核用英文跑完**——会话不会坏、不会卡，代价只是那一次不是中文。

## 4. 方案设计与选型

### 4.1 分支回溯摘要：三条路线

| 方案 | 原理 | 优点 | 缺点 | 结论 |
|------|------|------|------|:----:|
| **A. 源码补丁** | 直接 patch npm 安装包代码 | 最彻底，不依赖插件系统 | 改写内核源码，宿主升级后即失效 | ❌ 废弃 |
| **B. 扩展提供 summary** | 扩展拦截后自行调用模型完成摘要 | 自由度最高 | 额外模型配置负担，绕过内核 token 预算与流式控制 | ❌ 废弃 |
| **C. 指令完全置换（本方案）** | 用 `session_before_tree` 注入 `replaceInstructions: true`，内核据此用中文 Prompt 彻底覆盖英文模板 | 复用内核的重试、预算截断与已鉴权模型调用 | 仅在支持该事件的 Pi 版本生效 | ✅ 采用 |

### 4.2 上下文压缩：没有换词档，只剩接管

同样的三分法在压缩上塌缩成一条：

- 源码补丁：否决，理由同上；
- **接管式**：形式上等价于方案的 B，但这次不是"最自由所以最好"，而是**唯一不 patch 内核的路径**——官方 `docs/compaction.md` 明列 `return { compaction: {...} }` 用法，`examples/extensions/custom-compaction.ts` 就是完整参考实现。

代价随职责转移：内核不再兜底，契约字段（`firstKeptEntryId`、`tokensBefore`、`usage`、文件清单）与失败降级都要自己扛。§5.3–5.6 讲的就是这些代价。

## 5. 核心机制契约与工程化交付

### 5.1 分支回溯：最小扩展契约

扩展的职责仅限于**在事件触发时完成指令拦截与替换**，不介入模型推理与网络通信：

```typescript
pi.on("session_before_tree", async () => {
    return {
        replaceInstructions: true,                     // 必填：声明彻底覆盖默认英文模板
        customInstructions: CHINESE_BRANCH_SUMMARY_PROMPT // 注入等价中译模板
    };
});
```

> **注意**：必须显式设置 `replaceInstructions: true`，否则内核会把中文 Prompt 追加在英文模板之后，输出中英混杂。

### 5.2 提示词结构设计

中文 Prompt 与内核模板**1:1 同构**，只换语言不换骨架：保留 `## 目标`、`## 约束与偏好`、`## 进展`、`## 关键决策`、`## 下一步` 五个板块与二级标题结构。消费者是 LLM，结构保真才是恢复质量的来源；观感上则全中文。

### 5.3 上下文压缩：接管式四步

```typescript
pi.on("session_before_compact", async (event, ctx) => {
  // 1) 守卫：preparation 契约字段缺失 → 通知 + 交还英文默认
  // 2) 取料：messagesToSummarize + turnPrefixMessages（split）一次全覆盖
  // 3) 生成：convertToLlm + serializeConversation 序列化 → 中文模板 → 模型
  // 4) 交卷：{ compaction: { summary, firstKeptEntryId, tokensBefore, usage, details } }
});
```

两处**必须复用内核、不要自造**：

- 序列化用包导出的 `convertToLlm` + `serializeConversation`，与内核保持同样的截断口径；
- `firstKeptEntryId`、`tokensBefore` 直接取自 `preparation`，禁止自算。

### 5.4 split-turn：接管必须覆盖两块原料

`findCutPoint` 由 `keepRecentTokens`（默认 20k）从新到旧定切点，且绝不切在工具结果中间。当切点落在 turn 内部时，被丢弃的内容分两块：`messagesToSummarize`（更早历史）+ `turnPrefixMessages`（切点之前的半截 turn）。内核的处理是把两块拼成一份摘要。

如果扩展只摘要前者，后者就**既被丢弃又不在摘要里——半截 turn 的现场静默消失**。所以接管式实现必须 `[...messagesToSummarize, ...turnPrefixMessages]` 一次性覆盖（官方示例同款）。取舍是：单次调用的输出预算要同时盖住两块，超长 span 时摘要颗粒度略粗。

### 5.5 账目与清单：漏了不报错，只会静默丢

- **`usage` 必回填**：会话总账只认条目字段（`dist/core/usage-totals.js:58` 对 `compaction` 条目读 `entry.usage`），没有旁路记账。漏回填 = 这笔消耗凭空消失，且不报错。
- **文件清单要自维护**：`fromHook` 生成的摘要，内核不自动附带 `<read-files>/<modified-files>` 块，不补就断了跨轮累积链。实现里按内核 `FileOperations{read,written,edited}` 的口径复刻了 `computeFileLists` / `formatFileOperations`。

### 5.6 失败哲学与回退矩阵

原则：**一切拿不准 → 通知 + 交还内核英文默认**。

| 条件 | 处置 |
|---|---|
| split turn | 不再回退（§5.4 单次全覆盖） |
| 空摘要 / 模型调用异常 / 信号中止 | 通知 + 回退 |
| 契约字段漂移（Pi 升级） | 守卫探针 + 通知 + 回退 |
| handler 抛未知错误 | 事件总线兜底 → 回退 |
| 正常接管 | 通知一行（条数 / tokensBefore / 是否 split） |

每次回退都落一条 warning 通知，不留静默回退——否则"你以为在中文、其实一直在英文"。

### 5.7 实现与测试

- 分支回溯：`extensions/chinese-branch-summary.ts`
- 上下文压缩：`extensions/chinese-compaction.ts`
- 测试：`node --test --experimental-strip-types tests/*.test.ts`，10 项全绿（含 split 全覆盖、`/compact` 自带指令并入、异常回退族）
- 仓库：[CNCSMonster/pi-chinese-branch-summary](https://github.com/CNCSMonster/pi-chinese-branch-summary)

## 6. 架构启示

**一、两种模式由宿主契约的"档位"决定。** 不是哪种模式更好，而是宿主给了哪一档：有换词档就只换词——省事、向前兼容、内核继续兜底；只给交成品档就只能接管——自由，但契约保真与失败降级全归扩展。

**二、判据只有一条：只依赖公开事件契约，不碰内核实现。** 契约不变，内核怎么重构都不用改扩展；契约变了，守卫探针显性回退，而不是静默出错。

**三、接管式最容易犯的错，是把内核的活顺手重写一遍。** 序列化、token 预算、文件清单、usage 口径，内核都已有既成标准，复用它比自造保真。

## 7. 证据说明

本轮对照 v1.0.4 实测确认：`compaction.js:379/447/663`、`types.d.ts:1102/1106-1116`、`agent-session.js:2140/2201/2221/2512`、`usage-totals.js:58`，以及测试 10/10 通过。

未逐行复验、沿用既有记录的项：分支摘要模板行号（旧记录基于 v0.48.x 的 `branch-summarization.ts:258`，1.0.4 未复验）、第三个触发档 `overflow`、事件总线对 handler 抛错的 try/catch 细节。
