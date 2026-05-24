+++
title = "Engineering Discipline Skills Compared: Addy Osmani vs Matt Pocock"
date = 2026-05-25T00:00:00+08:00
slug = "matt-pocock-vs-addy-osmani-skills"
tags = ["AI Coding Agent", "Agent Skills", "Engineering Practices", "Matt Pocock", "Addy Osmani", "Tool Comparison"]
+++

## What This Solves

You're already using Addy Osmani's agent-skills (or their Pi ecosystem equivalents). Matt Pocock's skills repo just exploded (100K+ stars at verification time) and looks similar.

**They're the same type of thing: engineering discipline skills.** Not for adding new capabilities (search, deploy, draw), but for constraining how the agent works (align on requirements, write tests, review code). The difference is packaging: Addy embeds discipline into a process pipeline, Matt breaks it into discrete manual commands.

Should you invest time? Will they conflict? Can you use both?

By the end: **install, skip, or selectively install.**

---

## Bottom Line

**No conflict. Best used together.** Addy covers process completeness. Matt fills two gaps Addy doesn't go deep enough on: adversarial requirement grilling (`/grill-with-docs` — goes beyond spec questioning by cross-referencing your domain model) and proactive architecture inspection (`/improve-codebase-architecture`). Both handle pre-work alignment, but at different depths.

---

## Q1: They look similar — what's the real difference?

| | [Addy Osmani](https://github.com/addyosmani/agent-skills) | [Matt Pocock](https://github.com/mattpocock/skills) |
|---|---|---|
| **What** | A complete pipeline: idea → production | A toolkit: surgical strikes on vibe coding failures |
| **Usage** | By engineering phase: spec → plan → build → test → review → ship | On-demand: `/grill-with-docs` `/tdd` `/diagnose` ... |
| **Count** | 23 skills | 10 engineering skills |
| **Author** | Director, Google Cloud AI | TypeScript educator, ex-Vercel |
| **For** | Teams needing process rigor | Individuals/small teams needing "don't write crap code" |

**Fundamentally different design philosophies:**

```
Addy = Pipeline
  Assumes you're walking the full path → a skill for every step

Matt = Toolkit
  Assumes you fail at specific points → each skill fixes one failure mode
```

This is not just my interpretation. The two READMEs state their positioning directly:

> **Addy Osmani / agent-skills**: "Skills encode the workflows, quality gates, and best practices that senior engineers use when building software. These ones are packaged so AI agents follow them consistently across every phase of development."
>
> The key words are **workflows / quality gates / every phase of development**. That explains why Addy covers code review, frontend, security, CI/CD, and shipping.

> **Matt Pocock / skills**: "These skills are designed to be small, easy to adapt, and composable." And: "I built these skills as a way to fix common failure modes I see with Claude Code, Codex, and other coding agents."
>
> The key words are **small / composable / common failure modes**. Matt is closer to a set of patches for common agent failure modes than a full software delivery lifecycle framework.

---

## Q2: How much overlap? Is what I have enough?

| What you need | Addy | Matt | Verdict |
|---------------|:---:|:---:|---------|
| Write PRD/specs | ✅ spec-driven-development | ✅ /to-prd | Either works |
| TDD | ✅ test-driven-development | ✅ /tdd | Either works |
| Debugging | ✅ debugging-and-error-recovery | ✅ /diagnose | Either works |
| Code review | ✅ code-review-and-quality | ❌ | Use Addy |
| UI/frontend | ✅ frontend-ui-engineering | ❌ | Use Addy |
| CI/CD/shipping | ✅ ci-cd, shipping-and-launch | ❌ | Use Addy |
| Security | ✅ security-and-hardening | ❌ | Use Addy |
| **Pre-work alignment** | ✅ spec-driven-development (ask → produce spec) | ✅ `/grill-with-docs` (challenge → produce glossary + ADRs) | Both, different approaches |
| **Proactive architecture check** | ❌ code-review is a gate, not an inspection | ✅ `/improve-codebase-architecture` | **Matt exclusive** |
| Issue triage | ❌ | ✅ `/triage` | Matt exclusive |
| Rapid prototyping | ❌ | ✅ `/prototype` | Matt exclusive |

Note: Matt does not include code review, frontend, CI/CD, or security because those areas are unimportant. He omits them because his repo is not trying to cover the entire software delivery lifecycle. It is a toolkit for fixing common agent failure modes. Those production-grade quality gates still belong with Addy. **So the conclusion is not "replace Addy with Matt" — it is "use Addy as the backbone and Matt as an enhancement layer."**

Both require the agent to ask questions, but in opposite directions:

| | Addy spec-driven-development | Matt grill-with-docs |
|---|---|---|
| **Starting point** | "Surface your assumptions" → fill spec template | "Explore the codebase first" → read CONTEXT.md / ADRs / code |
| **Question style** | "What do you want? What are the constraints?" → fill 6-section template | "Your glossary says X but you seem to mean Y?" "Your code contradicts what you said — which is right?" → drill down |
| **Direction** | Blank slate → spec (greenfield) | Existing code/docs → aligned understanding (brownfield) |
| **Output** | A structured spec document | CONTEXT.md updates + ADRs + aligned understanding |
| **End condition** | Spec approved by human | Shared understanding reached |

**Conclusion: Both cover the basics, including pre-work alignment.** Matt's exclusives are `/grill-with-docs` for adversarial grilling (challenging you with domain model and code, not just filling a template) and `/improve-codebase-architecture` for proactive inspection. These are what vibe coding misses most.

---

## Q3: Will they conflict? Is one enough?

**No conflict.** Different naming, different triggering, complementary philosophies.

**One is enough.** If you already have Addy's pipeline, you're covered for daily work — you're only missing the grilling and inspection capabilities. If you have no engineering discipline skills, start with Matt for a lighter footprint. Together is best: Addy as process backbone, Matt filling the critical gaps.

Recommended combined usage: follow Addy's pipeline normally, switch to Matt for requirement alignment and code quality — `/grill-with-docs` as a deeper questioning layer (can replace `spec-driven-development`'s Specify phase, or complement it), `/improve-codebase-architecture` to supplement `code-review-and-quality`.

---

## Practical Advice

```
What to install:
  ✅ /grill-with-docs       — Most important. Pre-work grilling + glossary building
  ✅ /improve-codebase-architecture  — Run every few days
  ✅ /triage                — If you use GitHub issues
  ⚡ /tdd /diagnose         — Addy already covers these, optional

How to use together:
  1. New requirement → /grill-with-docs (not /spec)
  2. Development → Addy pipeline as usual
  3. Regularly → /improve-codebase-architecture
  4. Wrap-up → Addy's /review → /ship
```

---

## Appendix: Why Matt Pocock Went Viral

- Created 2026-02-03; verified on 2026-05-25 at 103K+ stars / 9.1K+ forks
- ~60K newsletter subscribers, TypeScript educator, ex-Vercel
- Reasons: anti-vibe-coding stance + small and composable + personal brand trust
- Community: Reddit (r/vibecoding, r/ClaudeAI, r/codex), Hacker News, Juejin, CSDN

---

## References

1. [mattpocock/skills](https://github.com/mattpocock/skills)
2. [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
3. [GitHub API - Matt Pocock](https://api.github.com/repos/mattpocock/skills)
4. [GitHub API - Addy Osmani](https://api.github.com/repos/addyosmani/agent-skills)
5. [Addy Osmani Homepage](https://addyosmani.com/)
6. [ExplainaX: Matt Pocock's agent skills](https://explainx.ai/blog/matt-pocock-agent-skills-real-engineers)
7. [r/codex: I tried the grill-me skill](https://www.reddit.com/r/codex/comments/1s8xlja/i_tried_the_grillme_skill_and_it_completely/)
8. [r/ClaudeAI: I deleted most of my Claude skills](https://www.reddit.com/r/ClaudeAI/comments/1sw6rss/i_deleted_most_of_my_claude_skills_last_week/)
9. [Juejin: TypeScript Master's AI Coding Secrets](https://juejin.cn/post/7633240840346271795)
10. [CSDN: The Skills Repo That Went Viral](https://gitcode.csdn.net/69f367f20a2f6a37c5a71245.html)
11. [Knight Li: mattpocock/skills overview](https://www.knightli.com/en/2026/05/01/mattpocock-skills-ai-agent-coding-workflows/)
12. [Medium: Stop Treating as Prompts](https://medium.com/@anup.karanjkar08/stop-treating-matt-pococks-skills-as-prompts-that-s-why-yours-aren-t-working-708f2c74edfc)
