+++
title = 'Pi Session Branch Summary Localization Design and Extension Implementation'
date = 2026-10-12T02:22:55+08:00
tags = ['Pi', 'Agent', 'Localization', 'Extension Development']
weight = 10
+++

## 1. What This Article Covers

An analysis of why Pi Coding Agent generates English summaries when switching conversation tree branches (via `/tree` backtracking), and the design and implementation of a global Chinese summary replacement based on the official `session_before_tree` extension lifecycle event.

## 2. Background and Observed Behavior

In Chinese-language technical research and documentation sessions, when the user switches and backtracks a conversation branch with `/tree`, Pi inserts a `<summary>` node into the conversation history as a compressed-context memory.

Even though the entire conversation is in Chinese, the auto-generated summary is still forced into an English structure with English headings:

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

While logically accurate, the native English summary creates a reading barrier in a Chinese context. A fully Chinese structured prompt aims to provide a zero-friction reading experience and preserve information-retrieval efficiency during technical retrospectives.

## 3. Source-Code Probing

Pi is a fully open-source project (official repo: [earendil-works/pi](https://github.com/earendil-works/pi)). Reviewing its core source reveals the underlying mechanism of branch-summary generation:

### 3.1 Hard-Coded Default Prompt

In the core module `packages/coding-agent/src/core/compaction/branch-summarization.ts:258`, Pi defines a constant template `BRANCH_SUMMARY_PROMPT`:

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

Regardless of the system locale or the user's interaction language, the system always assembles its prompt from this English template before sending it to the summary model.

### 3.2 Official Extension Hook and Event Sequence

After the branch switch is confirmed and before the summary-model call is dispatched, the Pi core broadcasts a lifecycle event to the extension layer via its event bus. The overall collaboration sequence is:

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

## 4. Design Choices

Three technical approaches were considered for the localization requirement:

| Approach | Mechanism | Pros | Cons | Verdict |
|----------|-----------|------|------|:-------:|
| **A. Source patch** | Patch the globally-installed npm package directly | Most thorough; no plugin-system dependency | Modifies core source; breaks on host upgrade | ❌ Rejected |
| **B. Extension-provided summary** | Extension intercepts and calls an external model to summarize | Maximum flexibility | Adds extra model-config burden; bypasses built-in token budget and streaming control | ❌ Rejected |
| **C. Full instruction replacement (this approach)** | Use `session_before_tree` to inject `replaceInstructions: true`, making the core fully override the built-in English template with a Chinese prompt | Reuses all of Pi core's retry, budget-truncation, and authenticated-model-call capabilities; relies only on the public event contract, so host upgrades are unlikely to break it | Only works on Pi versions that support the relevant event | ✅ Adopted |

## 5. Core Contract and Engineering Delivery

### 5.1 Minimal Extension Contract

Under approach C, the extension's responsibility is strictly limited to **intercepting and replacing the instructions when the event fires** — it never touches the underlying model inference or network communication.

The core contract only needs to return a control tuple at the `session_before_tree` stage:

```typescript
pi.on("session_before_tree", async () => {
    return {
        replaceInstructions: true,                     // required: declare full override of the default English template
        customInstructions: CHINESE_BRANCH_SUMMARY_PROMPT // inject the equivalent Chinese template
    };
});
```

### 5.2 Prompt Structure Design

The Chinese prompt uses a **1:1 isomorphic translation** of Pi's native template to preserve the logical density and reading experience of the summary.

**Design requirements**:

- **Same skeleton**: retain the five sections — `## 目标` (Goal), `## 约束与偏好` (Constraints & Preferences), `## 进展` (Progress), `## 关键决策` (Key Decisions), `## 下一步` (Next Steps);
- **Consistent hierarchy**: keep the second-level heading structure, leveraging Markdown's collapsible behavior to improve readability.

### 5.3 Implementation

The full implementation is available in the open-source repository:

- Repo: [CNCSMonster/pi-chinese-branch-summary](https://github.com/CNCSMonster/pi-chinese-branch-summary)

## 6. Architectural Takeaway: Replace the Instructions, Not the Engine

The pattern distilled from this approach — "Instruction Replacement over Engine Takeover" — has lasting reusable value:

1. **Minimal invasiveness**: when the host (harness) already has a mature budget manager, retry logic, and network pipeline, extensions should first look for a "prompt/parameter replacement point" rather than a "logic replacement point";
2. **Forward compatibility**: extensions should depend only on the host's public events and parameter contracts, never touching its internal implementation. As long as the contract remains stable, internal refactors and version upgrades in the host should not require changes in the extension;
