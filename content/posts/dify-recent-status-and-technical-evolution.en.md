+++
title = "Dify Status Check: Where Is It Now?"
date = 2026-10-14T00:00:00+08:00
slug = "dify-recent-status-and-technical-evolution"
[taxonomies]
    tags = ["Dify", "LLMOps", "AI Agent", "Open Source", "Research", "MCP", "Workflow"]
+++

> Baseline version: GitHub `langgenius/dify` v1.17.1  
> Estimated half-life: Quarterly (AI app orchestration and protocol evolution moves fast — keep an eye on plugin and MCP developments)  
> Nature: Personal research notes, sharing what I found  
> Motivation: I hadn't heard much about Dify recently and wondered — did it fall behind, or is it quietly growing somewhere else? So I spent some time digging through public sources and wrote down what I found.

---

## 1. A Feeling: Why Does It Seem Like "No One's Talking About It"?

At least in my own circles, between late 2024 and 2026, I rarely saw anyone discussing Dify. My first reaction was: is it dead?

But after going through the materials, I think this "disappearance" likely comes more from **our own shifting attention** and **Dify's own strategic pivot**:

```
2023 ~ Mid-2024 (Geek Carnival)                    2025 ~ 2026 (Divergence)
[Individual devs / Prompt engineers]             [Code-first camp (geeks/backend)]
      │                                                │
      ▼                                                ▼
Loved GUI drag-and-drop bots / simple KBs    Shifted to Coding Agents (Cursor/Claude Code)
Dify, FastGPT dominating social media         Shifted to code-native state machines (LangGraph/PydanticAI)
                                               
                                               [Dify's actual pivot]
                                                       │
                                                       ▼
                                           International expansion (Japan / North America / Europe)
                                           Deep enterprise (compliance / private deployment / global giants)
```

### 1.1 The Geek World's Attention Shifted

* In 2023 to early 2024, the LLM ecosystem was still figuring out "how to connect models to knowledge bases and prompts." Visual DAG drag-and-drop was the lowest-barrier, most demo-friendly approach;
* Later, the tech community's attention clearly shifted toward **Coding Agents** (Cursor, Claude Code, etc.) and **code-first state machine frameworks** (LangGraph, PydanticAI, etc.). With code, Git management and unit testing feel more native. People on social media stopped posting "wiring diagrams."

### 1.2 Dify's Own重心 Shifted

* From public information, the LangGenius team deliberately reduced their domestic geek marketing volume and poured energy into overseas markets and large enterprise customers;
* The fastest-growing market is **overseas (especially Japan and North America)**. While domestic social media discussion cooled, Dify was holding hundreds-person summits in Japan, joining AWS official channels, and completing private deployments inside multinational enterprise networks.

---

## 2. Publicly Available Business Data

Here are the numbers I found from public sources, for reference:

### 2.1 Funding

* **$30M Series Pre-A (March 2026)**:

  * **Lead**: HSG (HongShan);
  * **Followers**: GL Ventures, 5Y Capital (returning investor), Mizuho Leaguer Investment, Alt-Alpha Capital, and NYX Ventures;
  * Valuation approximately $180M.

### 2.2 Open Source & Community

* **GitHub Stars**: ~**158K** (global Top 60), 1000+ contributors, 861 recent commits, 168 releases;
* **Global self-hosted installations**: Over **1.4 million** machines;
* **Enterprise customers**: Publicly disclosed **280+**, including **Maersk, Volvo, Novartis, ThermoFisher**;
* **Global presence**: Offices in San Francisco Bay Area, Tokyo, Shanghai, and Suzhou;
* **Japan market**: Established the "Japan Association for Dify" (一般社团法人 Dify 协会, founded September 2025 with NTT Data and others), and became an AWS Global Partner (awarded 2025 AWS Social Impact Partner of the Year).

---

## 3. Product & Technical Evolution (v0.x to v1.17+)

From the version history, Dify's product form has clearly moved well beyond the early "visual prompt tuner" stage. The underlying tech stack has gone through multiple deep refactors:

```
                    ┌─────────────────────────────────┐
                    │       Dify Marketplace          │ (Plugin ecosystem / Community assets)
                    └────────────────┬────────────────┘
                                     │
┌───────────────────────────────┐    │    ┌───────────────────────────────┐
│        New Agent App          │    │    │       Workflow Studio         │
│ (Autonomous reasoning /      │◄───┴───►│ (Visual orchestration /       │
│  Skills / Code sandbox)      │         │  Branching / Dynamic routing) │
└───────────────┬───────────────┘         └───────────────┬───────────────┘
                │                                         │
                └───────────────────┬─────────────────────┘
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │   MCP Gateway (Workflow-as-MCP-Server / ClientPassthru)│
       └────────────────────────────┬───────────────────────────┘
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │     Core Engine (Async non-blocking / Sandbox / RBAC)   │
       └────────────────────────────────────────────────────────┘
```

### 3.1 Full MCP (Model Context Protocol) Support

* **Workflow-as-MCP-Server**: Complex business workflows orchestrated inside Dify can be exposed as standard MCP Servers with one click. Whether it's Claude Desktop, an IDE, or an external Coding Agent, they can all call Dify workflows as standard MCP tools;
* **Runtime dynamic header pass-through**: Supports injecting placeholder authentication at request time (e.g., `{{request.headers.X-Custom-Auth}}`), solving the security isolation and identity authentication challenge for multi-tenant enterprises calling third-party tools.

### 3.2 Plugin System & Marketplace — Fully Decoupled

* **No more forking source code**: In the early v0.x days, community developers wanting to integrate a new model or private internal system often had to fork the repo, modify core code, or even maintain their own version. v1.0 (early 2025) restructured the plugin architecture — tools and models are fully decoupled as independent plugins;
* **Marketplace & plugin security governance**: Introduced plugin security levels, signature verification, and sandbox isolation. Enterprise users can deploy private plugin sources on internal networks, balancing extensibility with compliance.

### 3.3 Agent Architecture Rebuild: New Agent App & Sandbox Execution

* **Chat-driven Agent building**: Supports generating and debugging agents through natural language conversation, automatically extracting and distilling structured, reusable Skills;
* **Built-in secure sandbox (DifySandbox)**: Provides isolated Python/Shell execution sandboxes for Code nodes and Tool nodes, supporting secure data transformation, logic decisions, and local script execution;
* **Bidirectional workflow nesting**: You can embed Agent nodes inside Workflows (letting the agent make local autonomous decisions), or have Agents trigger specific Workflows.

### 3.4 Enterprise Core & Compliance

* **Async non-blocking execution engine**: Database writes and long-chain calls are async-ified. Multi-branch parallel execution time is optimized from "simple sum of all branches" to "depends on the longest branch," significantly reducing timeout interruption rates;
* **Enterprise governance certifications**: Two consecutive years of SOC 2 Type II, ISO 27001:2022, and GDPR compliance certifications, with full audit log tracking and fine-grained RBAC permission controls.

---

## 4. My Attempt to Understand Its Positioning

Here's my personal understanding from research — may not be fully accurate, just for reference:

| Dimension | Dify (v1.17+) | Code-First Frameworks (LangGraph etc.) | Pure SaaS Competitors (Coze) |
|:---|:---|:---|:---|
| **Audience I observe** | Cross-functional teams (Business + IT) | Senior backend, AI full-stack engineers | Individual content creators, non-technical ops |
| **Deployment flexibility** | Open-source community / Container private / Multi-cloud | Pure code library, deploy as you wish | Deeply tied to platform ecosystem |
| **Debugging experience** | Good node-level historical I/O inspection UI | Relies on code breakpoints, LangSmith, etc. | Relies on platform logs |
| **Extension approach** | Plugin marketplace + MCP + Custom code nodes | Pure code, unlimited extension | Limited to platform's integration library |
| **Engineering collaboration** | Workflow DSL import/export, weaker Git diffing | Native Git + unit tests | In-platform version management |

### My Personal Scenario Understanding

```
                    Where does your scenario lean?
                              │
         ┌────────────────────┴────────────────────┐
         ▼                                         ▼
【Business-IT collaboration needed】        【Hardcore geek / Algorithm experiments】
• Need to visually present flows to biz    • Logic heavily depends on complex recursion, dynamic backtracking
• Need out-of-box RAG, permissions & audit • Heavily dependent on Git branching & automated testing
• Need multi-model aggregation & MCP GW    • More comfortable with pure code, averse to UI wiring
         │                                         │
         ▼                                         ▼
   Dify might be a good fit             LangGraph / custom code might be handier
```

> This is just my rough personal understanding. Real-world selection is far more complex. Many teams probably use a mix.

---

## 5. Monetization & Team Status

This is what I was curious about: Is it making money? Is the team still alive?

### 5.1 Pricing (Publicly Available)

| Plan | Price | Notes |
|:---|:---|:---|
| **Sandbox** | Free | 200 message credits/month, 1 person, 5 Apps |
| **Professional** | $59/mo ($590/yr) | 5,000 credits/month, 3 people, 50 Apps |
| **Team** | $159/mo ($1,590/yr) | 10,000 credits/month, 50 people, 200 Apps |
| **Enterprise** | Custom quote | SSO/SCIM, private deployment, SLA |
| **AWS Marketplace Enterprise** | **From $150,000/yr** | Listed on AWS Marketplace at this price |
| **Self-hosted community** | Free (open-source) | Users pay for infra + LLM API costs |

### 5.2 Revenue: Not Disclosed, but Profitable

Dify is a pre-Series-A company and hasn't publicly disclosed specific revenue figures. But from a Forbes interview (2026-02-24), one key data point is confirmed:

> "The company built around it employs 100 people, **is profitable** and serves more than 280 enterprise customers."

— **Profitable**, 100-person team. Specific revenue unknown.

Rough estimate (purely personal speculation, no public basis):

- Of 280+ enterprise customers, assuming some go through Enterprise (AWS lists at $150K+/yr), plus Cloud subscription revenue
- 100-person team + four offices, and already profitable — means revenue covers costs
- Notably, Dify's official careers page states "Over 60% of our codebase is built by LLMs" — R&D efficiency is likely far higher than traditional teams

### 5.3 Layoffs: None Found

In Layoffs.fyi and various tech layoff trackers, **no Dify/LangGenius layoff records were found**. Against the backdrop of massive tech industry layoffs in 2025-2026, this is a positive signal.

### 5.4 Hiring: Still Recruiting

Dify's official careers page (join.dify.ai) as of 2026-09-18 still had **4 open positions**:

- LTS Backend Software Engineer (China)
- Backend Development Intern (China)
- UI/UX Designer (China)
- Developer Relations Intern (Community Operations)

Not a large hiring scale, but shows the team is actively running, not frozen.

### 5.5 Development Activity: Very Active

From GitHub data:

- **Recent versions**: v1.17.1 (2026-09-10), v1.15.0 (2026-06-25), v1.14.2 (2026-05-19) — maintaining at least one release per month
- **Weekly activity**: ~615 new Stars, 132 Pushes
- **Issue activity**: New Issues still being filed as recently as 2026-10-13, with active Maintainer responses
- **Contributors**: 1000+, 23.9K Forks

---

## 6. Personal Takeaways

1. **Dify didn't disappear — it just went somewhere I can't easily see**: From the domestic geek community's perspective, it's certainly gone "quiet." But from the overseas enterprise market, Japan ecosystem, and AWS channels, it seems to be running fast on a different track;
2. **Low-code orchestration probably still has its place in enterprise scenarios**: While Code-First is the geek aesthetic mainstream, many real business scenarios need cross-department collaboration, visual auditing, and permission controls — these may not be what pure code frameworks do best;
3. **100 people, profitable, 60%+ code built by LLMs** — this combination is interesting in itself. It might be an early example of AI-native development: using AI to build AI tools, a small team leveraging massive scale;
4. **Missing specific revenue numbers** is the biggest gap in this research. Understandable for a pre-Series-A company. But from "profitable" and the $150K/yr AWS Enterprise price tag, the business model seems to be working at least.

> All of the above is my personal understanding from research — inevitably with some bias. If you see different information, I'd welcome the correction.
