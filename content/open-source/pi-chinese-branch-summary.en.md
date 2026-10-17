+++
title = 'Pi Session Summary Localization: Design and Extension Implementation'
date = 2026-10-12T02:22:55+08:00
updated = 2026-10-17T00:00:00+08:00
tags = ['Pi', 'Agent', 'Localization', 'Extension Development']
weight = 10
+++

## 1. What This Article Covers

Pi writes **two kinds** of structured summary into a session, and both templates are hard-coded in English in the core: the **branch summary** written when you backtrack with `/tree`, and the **compaction summary** written when a long session is compacted. The result is English headings showing up inside a Chinese conversation.

This article takes both paths apart and gives a localization approach for each: the branch summary goes through **instruction replacement** (swap the prompt, nothing else), while the compaction summary goes through **takeover** (the core offers no "swap the words" slot, so the extension must call the model itself and hand back a finished summary).

## 2. Background and Observed Behavior

**Case one: branch backtracking.** In Chinese-language technical research and documentation sessions, when the user switches and backtracks a branch with `/tree`, Pi inserts a `<summary>` node into the conversation history as context memory. Although the whole conversation is in Chinese, the summary is still forced into an English structure:

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

**Case two: context compaction.** In a long session, once the context approaches the window limit (or on a manual `/compact`), Pi folds the earlier history into a checkpoint summary, after which only "system prompt + summary + recent messages" are carried forward. That summary has an English skeleton too:

```markdown
## Goal
## Constraints & Preferences
## Critical Context
```

Both kinds appear in the same Chinese conversation, reading as continuous mixed Chinese-English text. The native English summaries are logically sound; they simply add a reading barrier in a Chinese-language context.

## 3. Source-Code Probing

Pi is a fully open-source project (official repo: [earendil-works/pi](https://github.com/earendil-works/pi)). The line numbers below were measured against the locally installed v1.0.4 `dist/`.

### 3.1 Branch Backtracking: Hard-Coded Default Prompt

The branch summary template is the core constant `BRANCH_SUMMARY_PROMPT` (`dist/core/compaction/branch-summarization.js`):

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

Independent of the system locale and the user's interaction language, the core assembles its prompt from this English template by default.

### 3.2 Branch Backtracking: Interception Path and Sequence

After the branch switch is confirmed and before the summary-model call is dispatched, the core broadcasts a lifecycle event to the extension layer over its event bus:

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

### 3.3 Context Compaction: Triggers and One Hard-Coded English Template

- **Triggers** (`dist/core/agent-session.js`): manual `/compact` (`reason="manual"`, :2221), context reaching the threshold (`"threshold"`, :2512), and other automatic paths.
- **Templates** (`dist/core/compaction/compaction.js`): the main `SUMMARIZATION_PROMPT` (:379) demanding "Use this EXACT format"; plus `UPDATE_SUMMARIZATION_PROMPT` (:447) for incremental updates and `TURN_PREFIX_SUMMARIZATION_PROMPT` (:663) for split prefixes.

In other words, whether a compaction summary comes out in English or Chinese has nothing to do with the conversation language — only with the core template.

### 3.4 The Key Difference: One Path Has a "Swap the Words" Slot, the Other Does Not

| Dimension | Branch backtracking (`session_before_tree`) | Context compaction (`session_before_compact`) |
|---|---|---|
| Result contract | `SessionBeforeTreeResult`: accepts `customInstructions` + `replaceInstructions` | `SessionBeforeCompactResult`: only `cancel` and `compaction` |
| Semantics | **Swap-the-words slot**: the core runs its own pipeline, you only replace the prompt | **Hand-in-a-finished-product slot**: either abort, or hand the whole summary to the core |
| Minimum extension duty | Supply a Chinese prompt | Call the model yourself and fill in the contract fields |

(Line numbers: `dist/core/extensions/types.d.ts:1102` for the compact result, `:1106-1116` for the tree result.)

In one sentence: **a branch summary can "just swap the words"; a compaction summary can only "compute it yourself and hand in the paper."**

### 3.5 Failure Means Fallback: Degrade, Do Not Corrupt

The core consumes `result?.compaction` (`agent-session.js:2201`); when it is empty, `_runDefaultCompaction` (:2140) runs the English default. If an extension handler throws, the event bus catches it, reports it, and leaves the result undefined — the same fallback. In short: **when in doubt, let the core finish in English.** The session never breaks or stalls; the only cost is that this one summary is not Chinese.

## 4. Design Choices

### 4.1 Branch Summary: Three Routes

| Approach | Mechanism | Pros | Cons | Verdict |
|------|------|------|------|:----:|
| **A. Source patch** | Patch the installed npm package directly | Most thorough; no dependency on the plugin system | Rewrites core source; breaks on host upgrade | ❌ Rejected |
| **B. Extension-provided summary** | Extension intercepts and calls a model itself | Maximum flexibility | Extra model configuration burden; bypasses the core's token budget and streaming control | ❌ Rejected |
| **C. Full instruction replacement (this approach)** | Inject `replaceInstructions: true` via `session_before_tree`, so the core fully replaces the English template with a Chinese prompt | Reuses the core's retry, budget truncation, and authenticated model calls | Only works on Pi versions supporting that event | ✅ Adopted |

### 4.2 Compaction: No Swap Slot, Only Takeover

The same three-route analysis collapses into one for compaction:

- Source patch: rejected, same reason as above;
- **Takeover**: formally the same as route B, but this time it is not "most flexible, therefore best" — it is the **only path that does not patch the core**. The official `docs/compaction.md` documents the `return { compaction: {...} }` usage, and `examples/extensions/custom-compaction.ts` is a complete reference implementation.

The cost moves with the responsibility: the core no longer covers for you, so the contract fields (`firstKeptEntryId`, `tokensBefore`, `usage`, file lists) and failure degradation are all yours. Sections 5.3–5.6 exist because of that cost.

## 5. Core Contract and Engineering Delivery

### 5.1 Branch Summary: Minimal Extension Contract

The extension's only job is to **intercept and replace the instructions when the event fires**; it never touches model inference or networking:

```typescript
pi.on("session_before_tree", async () => {
    return {
        replaceInstructions: true,                     // required: declare a full override of the default English template
        customInstructions: CHINESE_BRANCH_SUMMARY_PROMPT // inject the equivalent Chinese template
    };
});
```

> **Note**: `replaceInstructions: true` must be set explicitly; otherwise the core appends the Chinese prompt after the English template and produces mixed-language output.

### 5.2 Prompt Structure Design

The Chinese prompt is **1:1 isomorphic** with the core template — same skeleton, different language: it keeps the five sections (`## 目标`, `## 约束与偏好`, `## 进展`, `## 关键决策`, `## 下一步`) and the second-level heading structure. The consumer is an LLM, so structural fidelity is what preserves recovery quality; the visible result is all-Chinese.

### 5.3 Compaction: The Four Steps of Takeover

```typescript
pi.on("session_before_compact", async (event, ctx) => {
  // 1) Guard: missing preparation contract fields → notify + hand back to the English default
  // 2) Gather: messagesToSummarize + turnPrefixMessages (split) covered in one pass
  // 3) Generate: serialize with convertToLlm + serializeConversation → Chinese template → model
  // 4) Submit: { compaction: { summary, firstKeptEntryId, tokensBefore, usage, details } }
});
```

Two things **must reuse the core rather than be reinvented**:

- Serialization goes through the package exports `convertToLlm` + `serializeConversation`, keeping the same truncation behavior as the core;
- `firstKeptEntryId` and `tokensBefore` come straight from `preparation` — never compute them yourself.

### 5.4 Split Turn: Takeover Must Cover Both Input Blocks

`findCutPoint` picks the cut point by accumulating `keepRecentTokens` (20k by default) from newest to oldest, and never cuts inside a tool result. When the cut lands inside a turn, the discarded content comes in two blocks: `messagesToSummarize` (earlier history) and `turnPrefixMessages` (the partial turn before the cut). The core merges both into a single summary.

If an extension summarizes only the first block, the second is **discarded and absent from the summary — the half-turn's scene silently disappears**. A takeover implementation must therefore cover `[...messagesToSummarize, ...turnPrefixMessages]` in one call (exactly what the official example does). The trade-off: a single call must budget output for both blocks, so on very long spans the summary granularity is slightly coarser.

### 5.5 Accounting and File Lists: Omissions Fail Silently

- **`usage` must be filled in**: the session totals only read the entry field (`dist/core/usage-totals.js:58` reads `entry.usage` for `compaction` entries); there is no side channel for accounting. Omitting it makes that spend vanish — with no error.
- **File lists must be maintained by the extension**: for `fromHook` summaries, the core does not automatically attach the `<read-files>/<modified-files>` block, so skipping it breaks the cumulative chain across compactions. The implementation therefore replicates `computeFileLists` / `formatFileOperations` against the core's `FileOperations{read,written,edited}` semantics.

### 5.6 Failure Philosophy and the Fallback Matrix

The rule: **when anything is uncertain → notify + hand back to the core's English default**.

| Condition | Handling |
|---|---|
| Split turn | No longer falls back (§5.4 single-pass coverage) |
| Empty summary / model call error / aborted signal | Notify + fall back |
| Contract field drift (Pi upgrade) | Guard probe + notify + fall back |
| Handler throws an unknown error | Event bus catches → falls back |
| Normal takeover | One info notification (message count / tokensBefore / split or not) |

Every fallback emits a warning notification; there is no silent fallback — otherwise you would believe you are reading Chinese while it has been English all along.

### 5.7 Implementation and Tests

- Branch backtracking: `extensions/chinese-branch-summary.ts`
- Context compaction: `extensions/chinese-compaction.ts`
- Tests: `node --test --experimental-strip-types tests/*.test.ts`, 10/10 green (covering full split coverage, merging `/compact` instructions, and the failure/fallback family)
- Repository: [CNCSMonster/pi-chinese-branch-summary](https://github.com/CNCSMonster/pi-chinese-branch-summary)

## 6. Architectural Takeaways

**One — the two modes are decided by the host contract's "slot type."** It is not a question of which mode is better, but of which slot the host offers: with a swap slot you only swap the words — less work, forward-compatible, the core keeps covering for you; with only a finished-product slot you must take over — more freedom, but contract fidelity and failure degradation are entirely yours.

**Two — there is only one criterion: depend on public event contracts, never on core internals.** As long as the contract holds, the core can be refactored freely; when the contract changes, the guard probe falls back visibly instead of failing silently.

**Three — the classic takeover mistake is to rewrite the core's work on the side.** Serialization, token budgets, file lists, usage semantics — the core already defines each of them; reusing them is more faithful than reinventing them.

## 7. Evidence Notes

Verified against v1.0.4 in this round: `compaction.js:379/447/663`, `types.d.ts:1102/1106-1116`, `agent-session.js:2140/2201/2221/2512`, `usage-totals.js:58`, plus 10/10 tests passing.

Not re-verified line by line; carried over from earlier records: the branch-summary template line number (recorded as `branch-summarization.ts:258` back on v0.48.x, not re-verified on 1.0.4), the third trigger path `overflow`, and the event bus's try/catch details for handler errors.
