+++
title = "Karpathy 的 LLM Wiki 方法论学习笔记"
date = 2026-05-26
slug = "karpathy-llm-wiki"

+++

---

## 它解决什么问题

**你和 LLM 协作时，知识不积累。**

现在的 Code CLI（Claude Code、OpenCode、Pi 等）已经能自己读文件、搜目录、grep 内容，不需要你手动粘贴上下文。但问题在于：每次新会话，LLM 都要从原始文件重新推导理解——读一遍、综合一遍、形成判断。上一次会话里产生的分析、比较、洞见，全都丢在聊天历史里，下次又从零开始。

这就像一个每次都重新读原材料的厨师，而不是站在已经整理好的备料台上继续做菜。

**LLM Wiki 模式** 的不同之处：让 LLM 把知识编译成结构化的 wiki，跨会话积累，一次摄入多次复用。新会话不用从 raw 重新推导，直接站在 wiki 上继续。

---

## 核心思想

Karpathy 原文的关键句是:

> **The knowledge is compiled once and then kept current, not re-derived on every query.**

也就是:知识先被 LLM 编译成 wiki,并持续保持更新;不是每次查询时再从 raw documents 重新推导。

另一个关键句:

> **The wiki is a persistent, compounding artifact.**

wiki 不是一次性摘要,而是一个持久、复利增长的知识产物。

与 RAG 的本质区别:

| | RAG | LLM Wiki |
|---|---|---|
| 理解时机 | 每次查询时检索 raw chunks,再临时综合 | 新资料进入时先编译进 wiki,后续保持更新 |
| 知识形态 | 原始文档片段 | 结构化、交叉链接的 Markdown wiki |
| 跨会话 | 多数不积累 | 每次 ingest/query 都能让 wiki 变厚 |
| 可控性 | 多依赖索引和检索策略 | 人可直接读、审、改 wiki 文件 |

一句话:**RAG 是查资料;LLM Wiki 是养一个会长大的知识库。**

### 我的理解:RAG 与 LLM Wiki 的差别

普通 RAG 的核心是 **query-time retrieval**:回答问题时,根据当前问题从原始资料的 chunk 中检索相关片段,再交给 LLM 临时综合。它的问题不是"不能回答",而是回答过程中形成的新综合通常不会回流到知识库,因此知识不积累。

Karpathy 的 LLM Wiki 核心是 **ingest-time compilation + query-time writeback**:新资料进入时,LLM 先把 raw sources 编译成结构化、交叉链接的 wiki;查询时,LLM 基于 wiki 继续综合回答;如果这次 query 产生了新的比较、判断或洞见,就把它 filed back into the wiki。

因此,LLM Wiki 不是"从 wiki 中提取现成答案",而是让 wiki 成为持续维护的中间知识层:它降低每次 query 的重新理解成本,并通过写回机制让知识复利增长。

### 我的理解:persistent 与 compounding

Karpathy 说 wiki 是一个 **persistent, compounding artifact**,可以拆开理解:

- **persistent**:wiki 不是临时聊天上下文,而是落在文件系统里的持久 Markdown 知识库。它会保存 raw sources 被编译后的结构化知识,也会保存后续讨论中产生的有价值洞见。会话结束后,这些知识仍然存在,可被下一次 LLM 会话继续读取和维护。
- **compounding**:wiki 不只是一次性整理好的资料夹。每次 ingest 新资料,wiki 会更新;每次 query 产生新的比较、判断或连接,也可以 filed back into the wiki。后一次使用 wiki,会站在前一次积累的基础上继续增长。

如果没有 query 后的写回机制,LLM Wiki 就会退化成静态资料整理:它可能比 raw documents 更整齐,但不会因为每次探索而复利增长。

复利增长不是简单"资料越堆越多"。线性积累只是不断增加摘要和材料;复利增长是过去积累下来的认知会被重新关联、比较和修正,进而产生更好的综合结论。新的综合结论再被写回 wiki,成为下一次理解的基础。

---

## 三层架构

Karpathy 原文定义三层:

```
raw/          ← Raw sources:原始资料,只增不改
wiki/         ← The wiki:LLM 生成并维护的 Markdown 知识库
schema        ← The schema:告诉 LLM 如何维护 wiki 的规则文件
```

### raw：证据层

原文说 raw sources 是 immutable:LLM 可以读取,但不修改。它们是证据层,是追溯链的起点。

### 我的思考:raw 里进了错误材料怎么办?

Karpathy 的设计有一个隐含假设:靠入口管控防止垃圾进入。原文说 raw 层的资料选择权应由人掌握,也就是你在放进 raw 之前已经筛选过了。

但这个假设不能完全解决问题:人也会犯错,可能放进了一份当时觉得没问题但后来发现有误的材料;也可能放进了一份后来被证伪的论文或数据。这时候 raw immutable 的规则就变成了一个问题--如果只增不改不删,错误材料会永远留在那里,LLM 每次 ingest 都会读到它,wiki 里可能因此产生错误的综合结论。

原文没有直接回答这个问题。以下是我们的补充思路:

**1. raw 可以删,用 git 保留删除记录**

raw 的 immutable 本意是"不篡改已有的源文件内容",不是"不能删除错误的源文件"。用 git 管理 raw 目录,删除操作本身有记录,随时能恢复。比起维护一套废弃标记机制,直接删更简单。

**2. 在 wiki 里写纠正**

即使 raw 里的错误材料没删,wiki 里可以写明:某份来源的某个结论已被证伪,此来源不可靠。这样 LLM 下次读 wiki 时会看到这个纠正,不会被错误材料误导。

**3. lint 时检查矛盾**

lint 不只是格式检查,还应该检查 wiki 内部是否互相矛盾。如果两份来源给出了相反的结论,lint 应该标记出来,让人决定哪个可信。

### wiki:LLM-owned layer

原文说:

> **The LLM owns this layer entirely.**

这点很关键。Karpathy 的 wiki 不是人的正式笔记,而是 **LLM 负责写、更新、交叉引用和维护的一层中间知识库**。人主要阅读、审查、指导方向。

### schema:让 LLM 变成 wiki maintainer 的规则

schema 可以是 `CLAUDE.md`、`AGENTS.md` 等,定义:
- wiki 的目录结构
- 页面命名和 frontmatter 规则
- ingest/query/lint 工作流
- 引用和更新规范

### 我的理解:schema 保证跨会话一致性

如果没有 schema,wiki 的内容会逐渐变得没有结构。不同会话中的 LLM 可能按不同习惯创建页面、放置内容、维护链接和记录来源,时间久了就会积累出多种互不一致的结构。后续会话很难知道前面内容放在哪里,也很难沿用前面已经维护好的组织方式。

schema 的作用是把 wiki 维护方式固定下来。前面的会话、后面的会话、未来的新会话,都按照同一套结构和流程积累内容。这样 wiki 才方便扩展,也方便后续查询、关联和维护。

更准确地说,schema 不只规定"文件怎么放",还规定"LLM 应该怎么操作":ingest 时更新哪些页面,query 后什么内容值得写回,index 和 log 如何维护,lint 时检查什么。它把 LLM 从自由发挥的聊天机器人,变成有纪律的 wiki maintainer。

**三层之间是单向编译关系**:raw → wiki。raw 是证据,wiki 是解释和综合。

### 我的理解:LLM owns this layer entirely

Karpathy 说 "The LLM owns this layer entirely",不是说人完全不用管 wiki,而是说 wiki 层的具体维护劳动主要由 LLM 执行:创建页面、更新摘要、维护实体页/概念页、补充交叉链接、更新 `index.md` 和 `log.md`、做 lint 检查。

人的角色不是亲手整理每一页,而是通过对话指挥 LLM:提供资料来源、提出问题、决定探索方向、给出判断和洞察,并筛选哪些内容符合自己的需要。

更准确的分工是:

```text
LLM 负责:wiki 的书写、整理、交叉引用、更新和维护劳动。
Human 负责:资料选择、方向判断、问题提出、价值判断和可信度决策。
```

人不能完全放手,因为 LLM 可能误读资料、产生幻觉、做出错误关联,或者把推论写成事实。人需要用判断力对 wiki 的方向、可信度和后续使用做筛选。

特别重要的是,**raw 层的资料选择权应由人掌握**。LLM 可以建议还需要补充哪些资料,但哪些 source 进入 raw,应由人基于目标、质量和可信度决定。wiki 层由 LLM 维护,但它最好基于经过人选择或确认的 raw sources 进行编译和综合。

---

## 三个核心工作流

### Ingest(摄入)

LLM 读一份新原始资料 → 和人讨论 key takeaways → 写摘要页 → 更新相关概念/实体页 → 更新索引 → 记录日志。

Karpathy 原文提到,一份 source 可能触发 **10-15 个 wiki 页面** 的创建或更新。

### Query(查询)

LLM 先读 `index.md` → 定位相关页 → 综合作答,引用具体来源。

关键不是只回答问题。Karpathy 原文说:

> **good answers can be filed back into the wiki as new pages.**

也就是:有价值的 query 结果可以作为新页面或更新写回 wiki。

### Lint(定期健康检查)

定期让 LLM 检查 wiki 健康状态:
- 页面之间是否矛盾
- 新 source 是否推翻旧 claim
- 是否有 orphan pages
- 重要概念是否被提到但没有独立页面
- 是否缺少 cross-reference
- 是否存在 data gaps,值得继续搜索资料

### 我的理解:lint 是防腐机制

LLM 在维护 wiki 的过程中可能因为幻觉、误读或过度综合,写入错误内容;也可能在不断积累新知识后,没有把新旧知识之间的关系补上,导致页面变成孤立节点,后续查询时很难找到相关内容。

因此,LLM Wiki 需要定期 lint。这里的 lint 不只是格式化检查,而是 wiki 的健康检查:检查页面之间是否互相矛盾,是否有多种口径并存,是否缺少来源,是否存在孤立页面,概念之间是否缺少 cross-reference,以及当前结构是否仍然清晰、方便维护。

如果没有 lint,wiki 会越来越臃肿,也可能不断积累不一致的内容和维护债务。lint 的作用是提供一个固定流程,让 LLM 按照 schema 对 wiki 做一致性检查、证据链检查、关联结构检查,并提出修复建议。

---

## 关键洞察:Query 结果要 filed back

Karpathy 没有把 query 看成一次性消费。query 中产生的比较、分析、连接、洞见,都可以写回 wiki。

这就是 LLM Wiki 复利增长的关键:

```text
ingest source → wiki 变厚
query wiki    → 产生新综合
file back     → wiki 再变厚
```

如果没有这个写回机制,LLM Wiki 很容易退化成"整理过的 RAG":资料虽然被摘要过,但每次新洞见仍然丢在聊天历史里,不能积累。

---

## 风险与我的保留意见

LLM Wiki 的 compounding 机制是双刃剑。它可以让知识复利增长,也可能让幻觉复利增长。

风险链条是:

```text
LLM ingest 时误读 raw source
  ↓
错误内容进入 wiki
  ↓
后续 query 把 wiki 中的错误当成已知事实
  ↓
新的综合继续建立在旧错误之上
  ↓
幻觉被积累和放大
```

因此,wiki 不是最终权威。**raw 是证据层,wiki 是 LLM 基于证据做出的解释和综合。**

为了降低幻觉复利风险,LLM Wiki 应该有这些约束:

1. **保留 raw sources,不修改原始证据**
2. **重要 claim 尽量带来源或证据链接**
3. **区分事实、解释、推论和待验证内容**
4. **query 后的写回不能无脑进入高置信知识层**
5. **lint 不只检查孤立页和坏链接,也要检查无来源 claim、过时判断和可能被写实的推论**

我对 Karpathy 方法的保留意见是:原文说 "The LLM owns this layer entirely",这适合作为 wiki 维护分工,但不等于 wiki 中所有内容都天然可信。更稳妥的原则应是:

```text
LLM owns wiki maintenance;
Human owns trust and promotion decisions.
```

也就是:LLM 可以维护 wiki,但人决定哪些内容可信、哪些内容可以被当作高置信结论继续使用,哪些内容适合进入更正式的输出。

---

## index.md 和 log.md

Karpathy 特别提到两个特殊文件。

### index.md:内容导向

`index.md` 是 wiki 的目录和地图。每个页面有链接、一句话摘要,也可以带日期、source count 等元信息。

LLM query 时先读 index,再进入相关页面。Karpathy 认为在中等规模下(约 100 个 sources、数百个页面),这个方式已经很好用,甚至可以暂时不需要 embedding-based RAG。

### log.md:时间导向

`log.md` 是 append-only 的时间线,记录 ingest、query、lint 发生了什么。

原文建议用一致标题格式,例如:

```markdown
## [2026-04-02] ingest | Article Title
```

这样可以用简单 unix 工具查询:

```bash
grep "^## \[" log.md | tail -5
```

### 我的理解:空间导航与时间导航

`index.md` 是 wiki 的内容地图,不只是文件目录。它记录页面链接、一句话摘要和分类,帮助人和 LLM 快速定位相关页面。它回答的是:"这个 wiki 里有什么?相关内容在哪里?"

`log.md` 是 wiki 的演化时间线,不只是 git diff。它按时间记录 ingest、query、lint 等操作,帮助后续会话理解最近发生了什么、为什么更新、哪些内容刚被处理、下一步可以接什么。

可以这样区分:

```text
index.md = 空间导航:wiki 里有什么,去哪找
log.md   = 时间导航:最近发生了什么,为什么变
```

这两个文件对 LLM 特别重要,因为 LLM 每次新会话都会失忆。`index.md` 帮它恢复空间记忆,`log.md` 帮它恢复时间记忆。

---

## Obsidian 比喻

Karpathy 的心智模型很像软件开发:

> **Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.**

也就是说:
- Obsidian 只是浏览和编辑环境
- LLM 是实际维护 wiki 的"程序员"
- wiki 是知识代码库

这个比喻说明:LLM Wiki 的重点不是把笔记写漂亮,而是让一个 Markdown 知识库能像 codebase 一样持续维护、重构和增长。

---

## 适用场景与边界

### Karpathy 原文明确举例

Karpathy 原文认为这个模式适合任何"知识会随时间积累,并且希望被组织起来而不是散落各处"的场景,包括:

- **Personal**:个人目标、健康、心理、自我提升等长期记录
- **Research**:围绕一个主题持续数周或数月深入阅读和综合
- **Reading a book**:边读书边构建人物、主题、情节、概念之间的 wiki
- **Business/team**:由 Slack、会议记录、项目文档、客户访谈等喂养的内部 wiki
- **Competitive analysis / due diligence / trip planning / course notes / hobby deep-dives** 等

---

## 参考

- [Karpathy 原始 Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- `CLAUDE.md` / `AGENTS.md`：Karpathy 原文举例，可作为 schema 文件
- Obsidian：Karpathy 使用 Obsidian 作为 wiki 的浏览和编辑环境，用 graph view 查看知识关联
- [qmd](https://github.com/tobi/qmd)：Karpathy 原文提到的可选 Markdown 本地搜索工具，适合 wiki 规模变大后辅助检索
