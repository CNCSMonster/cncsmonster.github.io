+++
title = "Qwen Code 如何自动学习你的编程习惯？AutoSkill 机制深度解析"
date = 2026-06-01T00:00:00+08:00
slug = "qwen-code-autoskill-deep-dive"
tags = ["Qwen Code", "AI Agent", "AutoSkill", "编程助手"]
+++

在使用 Qwen Code 一段时间后，你可能注意到 `.qwen/skills/` 目录下凭空多出了几个 skill——`skill-review`、`skill-testing`——它们的 frontmatter 里标记着 `source: auto-skill`。这些不是你写的，也没人手动创建过。

这是 Qwen Code 的 **AutoSkill 机制**：一种程序性记忆的自动提炼能力。本文基于源码逆向和设计文档，完整拆解这个机制的工作原理、安全设计和学术渊源。

## AutoSkill 是什么

一句话：**会话结束后，Qwen Code 会在后台自动判断你刚才的操作流程是否值得复用，如果值得，就把它保存为一个项目级 skill。**

它和 Auto Memory 的定位不同：

| 维度 | Auto Memory | AutoSkill |
|------|-------------|-----------|
| 记忆类型 | 陈述性（用户是谁、项目背景） | 程序性（如何做某类任务） |
| 触发时机 | 每次会话结束 | 会话内工具调用 ≥ 20 次 |
| 写入目标 | `.qwen/memory/` | `.qwen/skills/` |
| 内容性质 | 用户偏好、项目上下文 | 可复用的操作步骤、最佳实践 |

简单说，Memory 记住"你是谁"，AutoSkill 记住"你怎么做事"。

## 触发条件

```
会话结束
  ├─ toolCallCount ≥ 20 ?        // 密度不足 → skip
  ├─ skillsModifiedInSession ?   // 本轮已手动操作 skill → skip
  └─ 都满足 → scheduleSkillReview()
               └─ fork 独立子 agent（8 轮上限，2 分钟超时）
```

只有当一次会话中工具调用足够密集（≥ 20 次），且用户没有手动编辑过 skill 文件时，才会触发。这避免了在简单问答会话中产生低质量 skill。

触发后，系统 fork 一个独立的 review agent（不是主对话的延续），最多运行 8 轮、2 分钟超时，对会话内容进行评估和提炼。

## 权限沙箱：核心安全设计

AutoSkill 最精妙的部分是它的安全机制。review agent 被关在一个严格的沙箱里：

| 工具 | 权限 | 安全机制 |
|------|------|----------|
| `read_file` | ✅ 项目根目录内 | 防止读取 `~/.aws/credentials` 等敏感文件并注入到 SKILL.md |
| `ls` | ✅ 项目根目录内 | 同上 |
| `write_file` | ⚠️ 仅 `.qwen/skills/<name>/SKILL.md` | 只能创建**不存在**的文件（防覆盖） |
| `edit` | ⚠️ 仅 `.qwen/skills/` 内 + 目标文件必须含 `source: auto-skill` | 不能改用户手写的 skill |

核心原则：**auto-skill 只能动自己创建的东西，绝不能碰用户手写的 skill。**

### `source: auto-skill` 保护机制

双重防线：

1. **硬约束（权限管理器）**：`edit` 前读取 frontmatter，无 `source: auto-skill` 则拒绝
2. **软约束（system prompt）**："You may ONLY modify skill files that contain 'source: auto-skill'"

用户若将自己创建的 skill 也加上 `source: auto-skill`，即表示允许 review agent 后续自动更新它。

### 防名称冲突覆盖

```typescript
// write_file 只允许创建新文件
try {
  await fs.stat(ctx.filePath);
  return 'deny';  // 文件已存在 → 拒绝
} catch (err) {
  if (err.code === 'ENOENT') return 'allow';  // 不存在 → 允许创建
  return 'deny';
}
```

这意味着：
- 创建新 skill → `write_file` ✅
- 更新已有 auto-skill → 必须用 `edit` ✅
- 覆盖任何已有文件 → 拒绝 ❌

### 防 symlink 穿越

`assertRealProjectSkillPath()` 用 `fs.realpath()` 解析真实路径，确认在 `.qwen/skills/` 内，防止通过符号链接写入项目外的位置。

## 学术渊源

```
Trace2Skill 论文（arXiv: 2603.25158）
    ↓
Hermes Agent（Nous Research，开源）——prompt 原始来源
    ↓ Qwen Code 设计文档："移植自 Hermes _SKILL_REVIEW_PROMPT，只做最小化适配"
Qwen Code AutoSkill
```

Qwen Code 设计文档明确提到：

> review agent 使用的提示语直接移植自 Hermes `_SKILL_REVIEW_PROMPT`，只做最小化适配。

Hermes 的原始 prompt 远比 Qwen 版本详细——包含 CLASS-LEVEL 技能组织、偏好嵌入、protected skills、Do NOT capture 列表等。Qwen 版本做了大幅精简，聚焦于"非平凡方法"和"试错过程"的提炼。

### Hermes vs Qwen Code

| | Hermes | Qwen Code |
|---|---|---|
| 触发时机 | 会话内 agent 直接调用 + 会话后后台 review | 仅会话后后台 fork |
| 保护机制 | ContextVar 追踪写入来源 + tool whitelist + protected skills | `source: auto-skill` frontmatter + 文件级权限管理器 |
| 写入范围 | `~/.hermes/skills/`（全局） | `.qwen/skills/`（项目级） |
| Prompt 复杂度 | 详细（含技能组织、偏好嵌入等） | 精简（聚焦可复用操作流程） |

## 与其他 Agent 对比

| Agent | 自动提炼程序性 skill | 说明 |
|-------|---------------------|------|
| **Hermes Agent** | ✅ 有（会话内 + 会话后） | 最早的开源实现，有 tool whitelist + protected skills |
| **Qwen Code** | ✅ 有（会话后） | 移植 Hermes prompt + 文件级权限沙箱 |
| **Claude Code** | ❌ 没有 | Auto Memory 只记录陈述性知识，不提炼操作流程 |
| **Cursor** | ❌ 没有 | Skills 全部手动创建 |
| **Pi** | ❌ 没有 | Skills 全部手动创建，Memory 手动管理 |
| **Codex CLI** | ❌ 没有 | 内置 skills + AGENTS.md 扩展，无自动提炼 |
| **Gemini CLI** | ❌ 没有 | 手动创建 SKILL.md，Memory 读取 GEMINI.md |

目前只有 Hermes 和 Qwen Code 实现了自动提炼程序性 skill 的能力，其他主流 AI coding agent 都还停留在手动管理阶段。

## 参考链接

- 设计文档：https://github.com/QwenLM/qwen-code/blob/main/docs/design/skill-nudge/skill-nudge.md
- 实现源码：`packages/core/src/memory/skillReviewAgentPlanner.ts`
- 首次提交：2026-05-09（`#3673`），默认开启：2026-05-27（`#4547`）
- Trace2Skill 论文：https://arxiv.org/abs/2603.25158
