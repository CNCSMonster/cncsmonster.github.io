+++
title = "Qwen Code Auto Mode Classifier: Two-Stage LLM Approval Mechanism"
date = 2026-07-29T00:00:00+08:00
slug = "qwen-code-auto-mode-classifier-en"
[taxonomies]
    tags = ["Qwen Code", "AI Agent", "LLM", "Security", "Coding Assistant"]
+++

> This article is based on reverse-engineered source code from Qwen Code `0.20.1-preview.7215`. Preview version internals may change across releases.

Qwen Code offers five approval modes: `plan`, `default`, `auto-edit`, `auto`, and `yolo`. In this version, **new installations default to auto mode** — tool calls are automatically approved through a multi-layer filtering system rather than requiring manual confirmation for each one. I also recommend auto mode for daily use; it strikes a good balance between efficiency and safety. This article dissects the mechanism and its configuration.

## Architecture Overview

Auto mode's approval mechanism consists of four parts:

1. **Rule layer**: Deterministic rules (tool default permissions, user-defined rules, allowlists, regex blocking) that quickly filter clearly safe or clearly dangerous operations
2. **LLM judgment layer**: Two-stage Classifier that handles ambiguous cases the rules can't cover
3. **Fail-closed**: When the classifier fails (timeout, API error, malformed response), it defaults to blocking — better safe than sorry
4. **Safety net**: Denial Tracking detects deadlocks between the LLM and classifier, falling back to manual confirmation when thresholds are reached

Complete lifecycle of a tool call:

```
LLM returns [A, B, C]
  → Each independently goes through the approval flow:
    ①-⑤ Rule layer → ⑥ LLM judgment layer
    → A approved → executes → returns result
    → B blocked → skipped
    → C approved → executes → returns result
  → All results sent back to the LLM together
  → LLM sees the full picture and decides what to do next
```

## Rule Layer: ①-⑤

Before Qwen Code executes a tool call (reading files, running commands, editing code, etc.), it passes through these checkpoints:

```
Tool call
  → ① Tool's default permission (e.g., read_file is safe by default, shell commands need approval)
  → ② PermissionManager (user-defined rules)
  → ③ acceptEdits fast-path (if in acceptEdits mode, workspace edits auto-approved)
  → ④ Safe-tool allowlist (read_file, grep, glob, etc. auto-approved)
  → ⑤ Guard (regex blocks dangerous command patterns like git clean, rm -rf — no LLM)
  → ⑥ LLM Classifier (two-stage LLM judgment, see below)
```

② is a user-configurable rules engine with four outcomes:

- `allow` → approved immediately (skips ③-⑥)
- `deny` → blocked immediately
- `ask` → prompts the user for manual confirmation
- `default` (no matching rule) → continue to ③-⑥

## Two-Stage Classifier

The first five checkpoints are deterministic rules — fast and free, but they can't cover every case. The remaining tool calls are handed to an LLM. The classifier receives the tool name, parameters, and current conversation context, then runs in two stages:

### Stage 1: Fast Judgment

- Model: fastModel (falls back to main model if not configured)
- Output: `{shouldBlock: boolean}` only
- Timeout: 10 seconds
- Behavior: allow → approve immediately; block → proceed to Stage 2

### Stage 2: Review

- Model: same as Stage 1
- Output: `{thinking, shouldBlock, reason}`
- Timeout: 30 seconds
- Behavior: allow → approve; block → reject

The `thinking` field in Stage 2's output is a plain-text explanation written by the model (e.g., "user is only reading a file, safe"), helping developers understand why the classifier made its decision.

### Fail-Closed: Better Safe Than Sorry

Any non-abort failure (API error, timeout, malformed response) returns `shouldBlock: true`. This means **when the classifier is down, all approval-required tools are blocked**. This is not a bug — it's a deliberate security design.

### Model Priority

```javascript
override → config.getFastModel() → config.getModel() → DEFAULT_QWEN_MODEL
```

The classifier uses fastModel. Without it, it falls back to the main model — which is typically slower, adding a few hundred milliseconds to a few seconds per Stage 1 judgment, which adds up over a session.

## Denial Tracking: Preventing Infinite Loops

If the classifier persistently blocks (LLM stuck in a dead end), the system won't loop forever:

| Counter | Threshold | Effect |
|---------|-----------|--------|
| Consecutive blocks | 3 | Next call skips classifier, goes straight to manual confirmation |
| Consecutive unavailable | 2 | Same as above |
| Total denials | 20 | Session-wide cap triggered |

These thresholds are hardcoded and not configurable. All counters reset when switching approval modes.

Key details:

- **Counted per tool call**, not per batch — 2 blocked calls in one batch increments by 2
- **Fallback happens before the classifier** — after 3 consecutive blocks, the 4th call skips the LLM call entirely and asks the user directly
- **Counters reset on user approval**, resuming auto mode; rejection keeps them, so the next call also goes to manual
- **Accumulates across turns** — the LLM sees each rejection, tries a different approach, gets blocked again, and after 3 consecutive blocks the system falls back to manual confirmation

## Configuration Recommendations

```json
{
  "fastModel": "qwen3-coder-plus",
  "tools": {
    "autoMode": {
      "classifier": {
        "timeouts": { "stage1Ms": 10000, "stage2Ms": 30000 },
        "thinking": { "stage2Enabled": false }
      }
    }
  }
}
```

**Key setting**: `fastModel` is the classifier's core dependency. Without it, the classifier falls back to the main model — which is typically slower, meaning every auto-mode tool call that requires classifier judgment will wait longer.

For model selection, pick a **fast** model. The classifier only needs to output a boolean or a short text — no deep reasoning required. Non-thinking models (like `qwen3-coder-plus`) are a natural fit; thinking-capable models (like `deepseek-v4-flash`) work too — the classifier disables API thinking mode in both stages by default, so the model won't do extra internal reasoning and stays fast. If you have sufficient local resources, a small local model as fastModel works too — zero API cost and fast response.

The only models to avoid: those that **force thinking on** (can't be disabled via parameters) — every judgment would waste time and tokens on unnecessary reasoning. Also, since the classifier sees conversation context and tool parameters, the fastModel's service provider should be at least as trustworthy as your main model's.

`stage2Enabled` controls whether Stage 2 uses API-level deep reasoning mode (slower, more tokens). The default `false` is fine — it doesn't affect the `thinking` output field, which is just a plain-text explanation the model writes regardless.

## Summary

Qwen Code's auto mode isn't a simple "execute everything automatically" switch. It's a carefully designed safety valve: the rule layer filters first, the LLM classifier handles ambiguous cases, fail-closed ensures errors don't allow dangerous actions, and denial tracking prevents infinite loops. The cost is an extra LLM call (and tokens) for every tool invocation requiring judgment.
