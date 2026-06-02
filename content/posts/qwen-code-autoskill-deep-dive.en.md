+++
title = "How Qwen Code Learns Your Coding Habits: AutoSkill Mechanism Deep Dive"
date = 2026-06-01T00:00:00+08:00
slug = "qwen-code-autoskill-deep-dive-en"
tags = ["Qwen Code", "AI Agent", "AutoSkill", "Coding Assistant"]
+++

After using Qwen Code for a while, you might notice unfamiliar skills appearing in `.qwen/skills/` — `skill-review`, `skill-testing` — each tagged with `source: auto-skill` in their frontmatter. You didn't create them. Nobody did manually.

This is Qwen Code's **AutoSkill mechanism**: an automatic distillation system for procedural knowledge. This article reverse-engineers the mechanism from source code and design documents, covering its architecture, security model, and academic origins.

## What is AutoSkill

In one sentence: **after a session ends, Qwen Code automatically evaluates whether your workflow is worth reusing, and if so, saves it as a project-level skill.**

It differs from Auto Memory in focus:

| Dimension | Auto Memory | AutoSkill |
|-----------|-------------|-----------|
| Knowledge type | Declarative (who you are, project context) | Procedural (how you do things) |
| Trigger | Every session end | Sessions with ≥ 20 tool calls |
| Write target | `.qwen/memory/` | `.qwen/skills/` |
| Content | User preferences, project context | Reusable workflows, best practices |

Memory remembers *who you are*. AutoSkill remembers *how you work*.

## Trigger Conditions

```
Session ends
  ├─ toolCallCount ≥ 20 ?        // Too few calls → skip
  ├─ skillsModifiedInSession ?   // User edited skills this round → skip
  └─ Both pass → scheduleSkillReview()
               └─ Fork standalone agent (8-turn limit, 2-min timeout)
```

The threshold ensures only sessions with substantial tool usage trigger review — avoiding low-quality skills from simple Q&A sessions. The review runs in an independent agent (not a continuation of your conversation), capped at 8 turns and 2 minutes.

## Permission Sandbox: The Core Security Design

The most elegant part of AutoSkill is its security model. The review agent is locked in a strict sandbox:

| Tool | Permission | Security Mechanism |
|------|-----------|-------------------|
| `read_file` | ✅ Within project root | Prevents reading `~/.aws/credentials` and injecting into SKILL.md |
| `ls` | ✅ Within project root | Same as above |
| `write_file` | ⚠️ Only `.qwen/skills/<name>/SKILL.md` | Can only create **non-existent** files (prevents overwriting) |
| `edit` | ⚠️ Only `.qwen/skills/` + target must contain `source: auto-skill` | Cannot modify user-authored skills |

Core principle: **auto-skill can only touch what it created — never user-authored skills.**

### The `source: auto-skill` Protection

Two layers of defense:

1. **Hard constraint (permission manager)**: `edit` reads frontmatter first; no `source: auto-skill` → rejected
2. **Soft constraint (system prompt)**: "You may ONLY modify skill files that contain 'source: auto-skill'"

If you add `source: auto-skill` to your own skill, you're opting in to automatic updates by the review agent.

### Preventing Name Collision Overwrites

```typescript
// write_file only allows creating new files
try {
  await fs.stat(ctx.filePath);
  return 'deny';  // File exists → reject
} catch (err) {
  if (err.code === 'ENOENT') return 'allow';  // Doesn't exist → allow creation
  return 'deny';
}
```

- Creating a new skill → `write_file` ✅
- Updating an existing auto-skill → must use `edit` ✅
- Overwriting any existing file → rejected ❌

### Anti-symlink Traversal

`assertRealProjectSkillPath()` uses `fs.realpath()` to resolve the actual path, confirming it stays within `.qwen/skills/` — preventing writes to arbitrary locations via symlinks.

## Academic Origins

```
Trace2Skill paper (arXiv: 2603.25158)
    ↓
Hermes Agent (Nous Research, open-source) — original prompt source
    ↓ Qwen Code design doc: "ported from Hermes _SKILL_REVIEW_PROMPT, minimal adaptation"
Qwen Code AutoSkill
```

The Qwen Code design document explicitly states:

> The review agent's prompt is directly ported from Hermes `_SKILL_REVIEW_PROMPT` with minimal adaptation.

Hermes's original prompt is far more detailed — including CLASS-LEVEL skill organization, preference embedding, protected skills, and Do NOT capture lists. Qwen's version is significantly streamlined, focusing on "non-trivial approaches" and "trial-and-error processes."

### Hermes vs Qwen Code

| | Hermes | Qwen Code |
|---|---|---|
| Trigger | In-session agent call + post-session review | Post-session background fork only |
| Protection | ContextVar tracking + tool whitelist + protected skills | `source: auto-skill` frontmatter + file-level permission manager |
| Write scope | `~/.hermes/skills/` (global) | `.qwen/skills/` (project-level) |
| Prompt complexity | Detailed (skill organization, preference embedding, etc.) | Streamlined (focused on reusable workflows) |

## Comparison with Other Agents

| Agent | Auto-distills procedural skills | Notes |
|-------|--------------------------------|-------|
| **Hermes Agent** | ✅ Yes (in-session + post-session) | First open-source implementation, with tool whitelist + protected skills |
| **Qwen Code** | ✅ Yes (post-session) | Ported Hermes prompt + file-level permission sandbox |
| **Claude Code** | ❌ No | Auto Memory records declarative knowledge only |
| **Cursor** | ❌ No | Skills are entirely manual |
| **Pi** | ❌ No | Skills entirely manual, Memory managed manually |
| **Codex CLI** | ❌ No | Built-in skills + AGENTS.md extension, no auto-distillation |
| **Gemini CLI** | ❌ No | Manual SKILL.md creation, Memory reads GEMINI.md |

Currently only Hermes and Qwen Code implement automatic procedural skill distillation. All other major AI coding agents remain in manual-management territory.

## References

- [Design doc](https://github.com/QwenLM/qwen-code/blob/main/docs/design/skill-nudge/skill-nudge.md)
- Source: `packages/core/src/memory/skillReviewAgentPlanner.ts`
- First commit: 2026-05-09 (`#3673`), enabled by default: 2026-05-27 (`#4547`)
- [Trace2Skill paper](https://arxiv.org/abs/2603.25158)
