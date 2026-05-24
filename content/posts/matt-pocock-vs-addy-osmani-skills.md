+++
title = "工程规范 Skill 对比：已有 Addy Osmani，还要装 Matt Pocock 吗？"
date = 2026-05-25T00:00:00+08:00
slug = "matt-pocock-vs-addy-osmani-skills"
tags = ["AI Coding Agent", "Agent Skills", "工程规范", "Matt Pocock", "Addy Osmani", "工具对比"]
+++

## 这篇解决什么问题

你已经在用 Addy Osmani 的 agent-skills（或 Pi 内置的同源 skill）。最近 Matt Pocock 的 skills 仓库爆火（截至验证时 100K+ Stars），看起来也差不多。

**它们其实是同一类东西——工程规范 skill。** 不是给 agent 加新能力（搜索、部署、画图），而是约束 agent 怎么干活才不烂（先对齐需求、写测试、审查代码）。差别在于封装方式：Addy 把规范嵌入流程管线，Matt 拆成零散的手动命令。

该不该花时间了解？装了会不会跟已有的打架？还是两者可以一起用？

读完这篇你能判断：**装、不装、还是选择性装。**

---

## 一句话结论

**不冲突，一起用效果最好。** Addy 管流程完整性，Matt 补两项 Addy 不够深的：挑战式需求盘问（`/grill-with-docs`，比 spec 询问更深——拿领域模型反问你）和主动架构巡检（`/improve-codebase-architecture`）。两者都有开工前对齐需求，但深度不同。

---

## Q1: 看起来很像，到底有什么区别？

| | [Addy Osmani](https://github.com/addyosmani/agent-skills) | [Matt Pocock](https://github.com/mattpocock/skills) |
|---|---|---|
| **是什么** | 一条完整流水线：从想法到上线 | 一个工具箱：精准打击 vibe coding 的常见翻车 |
| **怎么用** | 按工程阶段调用：spec → plan → build → test → review → ship | 按需调用：`/grill-with-docs` `/tdd` `/diagnose` ... |
| **数量** | 23 个 skill | 10 个 engineering skill |
| **谁做的** | Google Cloud AI 总监 | TypeScript 教育者，前 Vercel |
| **适合** | 团队项目，需要流程规范 | 个人/小团队，需要「别写烂代码」 |

**核心设计理念不同：**

```
Addy = 管线（Pipeline）
  假设你要走完整流程 → 每一步都有对应 skill

Matt = 工具箱（Toolkit）
  假设你最容易在特定环节翻车 → 每个 skill 修一个具体问题
```

这个判断不是凭感觉。两个仓库 README 里的原话已经把定位说得很清楚：

> **Addy Osmani / agent-skills**："Skills encode the workflows, quality gates, and best practices that senior engineers use when building software. These ones are packaged so AI agents follow them consistently across every phase of development."
>
> 关键词是 **workflows / quality gates / every phase of development**。所以 Addy 会覆盖 code review、frontend、security、CI/CD、shipping 这类生产级质量门禁。

> **Matt Pocock / skills**："These skills are designed to be small, easy to adapt, and composable." 以及 "I built these skills as a way to fix common failure modes I see with Claude Code, Codex, and other coding agents."
>
> 关键词是 **small / composable / common failure modes**。所以 Matt 更像一组针对 agent 常见翻车点的补丁，而不是完整软件交付生命周期框架。

---

## Q2: 重叠多少？我已有的够用吗？

| 你需要的 | Addy 有吗 | Matt 有吗 | 结论 |
|----------|:---:|:---:|------|
| 写 PRD/规格 | ✅ spec-driven-development | ✅ /to-prd | 都有，随便用 |
| TDD | ✅ test-driven-development | ✅ /tdd | 都有，随便用 |
| 调试 | ✅ debugging-and-error-recovery | ✅ /diagnose | 都有，随便用 |
| 代码审查 | ✅ code-review-and-quality | ❌ | 用 Addy |
| UI/前端 | ✅ frontend-ui-engineering | ❌ | 用 Addy |
| CI/CD/发布 | ✅ ci-cd, shipping-and-launch | ❌ | 用 Addy |
| 安全 | ✅ security-and-hardening | ❌ | 用 Addy |
| **开工前对齐需求** | ✅ spec-driven-development（询问需求 → 产出 spec） | ✅ `/grill-with-docs`（挑战认知 → 产出术语表 + ADR） | 都有，方向不同 |
| **定期巡检架构** | ❌ code-review 是合并前守门，不是主动巡检 | ✅ `/improve-codebase-architecture` | **Matt 独有** |
| Issue 分类排优 | ❌ | ✅ `/triage` | Matt 独有 |
| 快速原型 | ❌ | ✅ `/prototype` | Matt 独有 |

注意：Matt 没有 code review、frontend、CI/CD、security，不是因为这些不常用，而是因为 Matt 的定位不是覆盖完整软件交付生命周期。它更像“修 agent 常见翻车点的工具箱”。这些生产级质量门禁仍然应该交给 Addy。**所以结论不是“用 Matt 替代 Addy”，而是“Addy 做底座，Matt 做增强插件”。**

两者都要求 agent 问问题，但方向截然不同。以下对比说清楚：

| | Addy spec-driven-development | Matt grill-with-docs |
|---|---|---|
| **起点** | 「列出你的假设」→ 填 spec 模板 | 「先探索代码库」→ 读 CONTEXT.md / ADR / 代码 |
| **提问方式** | 「你要什么？有什么约束？」→ 填 6 段模板 | 「你的术语表说 X 但你指 Y？」「代码和你说法矛盾，哪个对？」→ 逐层追问 |
| **方向** | 从空白 → spec（适合新项目） | 从已有代码/文档 → 对齐认知（适合存量项目） |
| **产出** | 一份结构化 spec 文档 | CONTEXT.md 更新 + ADR + 对齐的认知 |
| **结束条件** | spec 被人审批通过 | 达成共享理解 |

**结论：基础能力两边都有，包括开工前对齐需求。** Matt 独有的是 `/grill-with-docs` 的**挑战式盘问**（拿领域模型和代码反问你，而非填模板）和 `/improve-codebase-architecture` 的**主动巡检**。这两项在 vibe coding 时代最稀缺。

---

## Q3: 会冲突吗？只用一个行不行？

**不会冲突。** 命名不同、触发方式不同、理念互补。

**但只用一个也行。** 如果你已经有 Addy 的完整管线，日常够用——缺的只是盘问和巡检两个能力。如果你没装任何工程规范 skill，从 Matt 开始更轻量。两者一起用效果最好：Addy 兜底流程，Matt 补关键短板。

同时安装的推荐用法：日常走 Addy 管线，在需求对齐和代码质量两个环节切到 Matt——`/grill-with-docs` 作为更深的盘问层（可替代 `spec-driven-development` 的 Specify 阶段，或两者互补），`/improve-codebase-architecture` 补充 `code-review-and-quality`。

---

## 实操建议

```
装哪些：
  ✅ /grill-with-docs       — 最重要。开工前盘问 + 建立术语表
  ✅ /improve-codebase-architecture  — 每几天跑一次
  ✅ /triage                — 如果你用 GitHub issues
  ⚡ /tdd /diagnose         — Addy 已有，可选装

怎么用：
  1. 新需求 → /grill-with-docs（不是 /spec）
  2. 开发 → Addy 管线正常走
  3. 定期 → /improve-codebase-architecture
  4. 收尾 → Addy 的 /review → /ship
```

---

## 附：为什么 Matt Pocock 火了

- 2026-02-03 创建；截至 2026-05-25 验证时为 103K+ Stars / 9.1K+ Forks
- ~60K newsletter 订阅者，TypeScript 教育者，前 Vercel
- 火的原因：反 vibe coding + 小而可组合 + 个人品牌信任
- 社区覆盖：Reddit（r/vibecoding、r/ClaudeAI、r/codex）、Hacker News、掘金、CSDN

---

## 参考文献

1. [mattpocock/skills](https://github.com/mattpocock/skills)
2. [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
3. [GitHub API - Matt Pocock](https://api.github.com/repos/mattpocock/skills)
4. [GitHub API - Addy Osmani](https://api.github.com/repos/addyosmani/agent-skills)
5. [Addy Osmani 个人主页](https://addyosmani.com/)
6. [ExplainaX: Matt Pocock's agent skills](https://explainx.ai/blog/matt-pocock-agent-skills-real-engineers)
7. [r/codex: I tried the grill-me skill](https://www.reddit.com/r/codex/comments/1s8xlja/i_tried_the_grillme_skill_and_it_completely/)
8. [r/ClaudeAI: I deleted most of my Claude skills](https://www.reddit.com/r/ClaudeAI/comments/1sw6rss/i_deleted_most_of_my_claude_skills_last_week/)
9. [掘金：TypeScript 大神的 AI 编程秘籍](https://juejin.cn/post/7633240840346271795)
10. [CSDN：爆火的 Skills 仓库](https://gitcode.csdn.net/69f367f20a2f6a37c5a71245.html)
11. [Knight Li: mattpocock/skills overview](https://www.knightli.com/en/2026/05/01/mattpocock-skills-ai-agent-coding-workflows/)
12. [Medium: Stop Treating as Prompts](https://medium.com/@anup.karanjkar08/stop-treating-matt-pococks-skills-as-prompts-that-s-why-yours-aren-t-working-708f2c74edfc)
