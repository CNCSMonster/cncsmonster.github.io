+++
title = "Qwen Code Auto Mode 深度分析"
date = 2026-09-07T00:00:00+08:00
slug = "qwen-code-auto-mode-deep-dive"
[taxonomies]
    tags = ["Qwen Code", "AI Agent", "自动审批", "Classifier", "Coding Assistant"]
+++

> **代码基准**：[QwenLM/qwen-code](https://github.com/QwenLM/qwen-code) `main` 分支的 commit [`9c320cb0c`](https://github.com/QwenLM/qwen-code/commit/9c320cb0cc328dc91b362516b630ae4a3dcdd15d)；文中源码路径均相对此版本仓库根目录。

---

## 一、Auto Mode 的整体流程

**Auto Mode 是 Qwen Code 的一种审批模式**，与 Default、YOLO 等模式并列；当前选定的模式决定工具调用如何获得执行许可。启用 Auto 模式后，除规则直接处理的调用外，工具调用会先交给 **Classifier** 使用模型进行自动审批。一个好的自动审批机制不仅要避免高风险调用被误放行，还要尽量减少不必要的人工确认，并控制审批带来的延迟和 Token 成本；同时，用户应能为自己关心的操作收紧确认边界。本文从**安全性、自动化程度、审批延迟与成本、用户可控性**四个角度分析 Auto Mode 的设计。

下图是这套分流流程的总览，也是后文分析各项设计的基础。它是对源码处理逻辑的归纳，不是项目官方定义的架构层级：

<style scoped>
#qwen-auto-mode-approval-flow {
  --doc-text: #111827;
  --doc-muted: #1f2937;
  --doc-border: #9ca3af;
  --doc-card: #f9fafb;
  --doc-soft: #f3f4f6;
  --doc-brand: #2563eb;
  --doc-brand-soft: #dbeafe;
  --doc-green: #15803d;
  --doc-green-soft: #dcfce7;
  --doc-green-border: #86efac;
  --doc-yellow: #a16207;
  --doc-yellow-soft: #fef9c3;
  --doc-yellow-border: #fde047;
  --doc-red: #b91c1c;
  --doc-red-soft: #fee2e2;
  --doc-red-border: #fca5a5;
  --doc-shadow: 0 1px 3px rgb(0 0 0 / 0.1);
  --flow-line: var(--doc-muted);
  --flow-card: var(--doc-card);
  --flow-border: var(--doc-border);
  margin: 2rem 0;
  color: var(--doc-text);
  font-family: Inter, ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.5;
}

#qwen-auto-mode-approval-flow * {
  box-sizing: border-box;
}

#qwen-auto-mode-approval-flow .flow-start,
#qwen-auto-mode-approval-flow .flow-decision,
#qwen-auto-mode-approval-flow .flow-review,
#qwen-auto-mode-approval-flow .flow-result {
  border: 1px solid var(--flow-border);
  border-radius: 0.75rem;
  background: var(--flow-card);
  box-shadow: var(--doc-shadow);
}

#qwen-auto-mode-approval-flow .flow-start {
  width: fit-content;
  margin: 0 auto;
  padding: 0.65rem 1.25rem;
  border-color: var(--doc-brand);
  font-weight: 700;
  text-align: center;
}

#qwen-auto-mode-approval-flow .flow-connector {
  display: flex;
  min-height: 2.25rem;
  align-items: center;
  justify-content: center;
  color: #111827;
  font-size: 1.35rem;
  font-weight: 800;
  line-height: 1;
}

#qwen-auto-mode-approval-flow .flow-step {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(9rem, 0.34fr);
  gap: 1rem;
  align-items: center;
}

#qwen-auto-mode-approval-flow .flow-decision {
  padding: 1rem 1.15rem;
  text-align: center;
  font-weight: 600;
}

#qwen-auto-mode-approval-flow .flow-branch {
  display: flex;
  gap: 0.55rem;
  align-items: center;
}

#qwen-auto-mode-approval-flow .flow-branch-label,
#qwen-auto-mode-approval-flow .flow-down-label {
  flex: 0 0 auto;
  border-radius: 999px;
  padding: 0.15rem 0.6rem;
  background: var(--doc-soft);
  color: #111827;
  font-size: 0.85rem;
  font-weight: 800;
}

#qwen-auto-mode-approval-flow .flow-branch-arrow {
  color: #111827;
  font-size: 1.1rem;
  font-weight: 800;
}

#qwen-auto-mode-approval-flow .flow-result {
  flex: 1;
  padding: 0.7rem 0.85rem;
  text-align: center;
  font-weight: 700;
}

#qwen-auto-mode-approval-flow .flow-result--allow {
  border-color: var(--doc-green-border);
  background: var(--doc-green-soft);
  color: var(--doc-green);
}

#qwen-auto-mode-approval-flow .flow-result--manual {
  border-color: var(--doc-yellow-border);
  background: var(--doc-yellow-soft);
  color: var(--doc-yellow);
}

#qwen-auto-mode-approval-flow .flow-result--block {
  border-color: var(--doc-red-border);
  background: var(--doc-red-soft);
  color: var(--doc-red);
}

#qwen-auto-mode-approval-flow .flow-next {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(9rem, 0.34fr);
  gap: 1rem;
  min-height: 3rem;
}

#qwen-auto-mode-approval-flow .flow-down {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #111827;
  font-size: 1.05rem;
  font-weight: 800;
  line-height: 1.1;
}

#qwen-auto-mode-approval-flow .flow-review {
  padding: 1rem 1.15rem;
  border-color: var(--doc-brand);
  background: var(--doc-brand-soft);
  text-align: center;
}

#qwen-auto-mode-approval-flow .flow-review strong {
  display: block;
  margin-bottom: 0.25rem;
}

#qwen-auto-mode-approval-flow .flow-review span {
  color: var(--doc-muted);
  font-size: 0.9rem;
}

#qwen-auto-mode-approval-flow .flow-section-note {
  display: block;
  margin-top: 0.4rem;
  color: #374151;
  font-size: 0.85rem;
  font-weight: 600;
}

#qwen-auto-mode-approval-flow .flow-outcomes {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

#qwen-auto-mode-approval-flow .flow-outcome {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  align-items: center;
}

#qwen-auto-mode-approval-flow .flow-manual-route {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px dashed var(--flow-border);
}

#qwen-auto-mode-approval-flow .flow-manual-route-intro {
  display: block;
  margin-bottom: 0.75rem;
  color: #111827;
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.6;
  opacity: 1;
  text-align: center;
}

#qwen-auto-mode-approval-flow .flow-manual-decision {
  width: fit-content;
  margin: 0 auto;
  padding: 1rem 1.15rem;
  border: 1px solid var(--flow-border);
  border-radius: 0.75rem;
  background: var(--flow-card);
  box-shadow: var(--doc-shadow);
  font-weight: 600;
  text-align: center;
}

#qwen-auto-mode-approval-flow .flow-manual-branches {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

#qwen-auto-mode-approval-flow .flow-manual-branch {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  align-items: center;
}

#qwen-auto-mode-approval-flow .flow-manual-branch-arrow {
  color: var(--flow-line);
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1;
}

#qwen-auto-mode-approval-flow .flow-manual-branch-label {
  color: #111827;
  font-size: 0.9rem;
  font-weight: 600;
}

#qwen-auto-mode-approval-flow code {
  white-space: nowrap;
  padding: 0;
  border-radius: 0;
  background: transparent;
  color: inherit;
  font-size: inherit;
}

@media (max-width: 640px) {
  #qwen-auto-mode-approval-flow .flow-step {
    grid-template-columns: 1fr;
  }

  #qwen-auto-mode-approval-flow .flow-branch {
    justify-content: center;
  }

  #qwen-auto-mode-approval-flow .flow-next {
    display: block;
    min-height: 3rem;
  }

  #qwen-auto-mode-approval-flow .flow-down {
    min-height: 3rem;
  }

  #qwen-auto-mode-approval-flow .flow-outcomes {
    grid-template-columns: 1fr;
  }
}

@media (prefers-color-scheme: dark) {
  #qwen-auto-mode-approval-flow,
  #qwen-auto-mode-transcript-construction,
  #qwen-auto-mode-two-stage-review,
  #qwen-auto-mode-fallback-timeline {
    --doc-text: #e5e7eb;
    --doc-muted: #e5e7eb;
    --doc-border: #6b7280;
    --doc-card: #1f2937;
    --doc-soft: #374151;
    --doc-brand: #60a5fa;
    --doc-brand-soft: #1e3a5f;
    --doc-green: #86efac;
    --doc-green-soft: #14532d;
    --doc-green-border: #4ade80;
    --doc-yellow: #fde68a;
    --doc-yellow-soft: #713f12;
    --doc-yellow-border: #facc15;
    --doc-red: #fca5a5;
    --doc-red-soft: #7f1d1d;
    --doc-red-border: #f87171;
    --doc-shadow: 0 1px 3px rgb(0 0 0 / 0.4);
  }
}
</style>

<div id="qwen-auto-mode-approval-flow" role="img" aria-label="Auto Mode 工具调用审批流程">
  <div class="flow-start">待审批的工具调用</div>
  <div class="flow-connector" aria-hidden="true">↓</div>

  <div class="flow-step">
    <div class="flow-decision">
      是否为 workspace 内的普通 <code>edit</code> / <code>write_file</code>，且没有匹配 <code>permissions.ask</code>？
      <small class="flow-section-note">第二节 · 快速通道</small>
    </div>
    <div class="flow-branch">
      <span class="flow-branch-label">是</span>
      <span class="flow-branch-arrow" aria-hidden="true">→</span>
      <span class="flow-result flow-result--allow">放行</span>
    </div>
  </div>
  <div class="flow-next">
    <div class="flow-down"><span class="flow-down-label">否</span><span aria-hidden="true">↓</span></div>
  </div>

  <div class="flow-step">
    <div class="flow-decision">是否属于静态安全工具白名单，且没有匹配 <code>permissions.ask</code>？<small class="flow-section-note">第二节 · 快速通道</small></div>
    <div class="flow-branch">
      <span class="flow-branch-label">是</span>
      <span class="flow-branch-arrow" aria-hidden="true">→</span>
      <span class="flow-result flow-result--allow">放行</span>
    </div>
  </div>
  <div class="flow-next">
    <div class="flow-down"><span class="flow-down-label">否</span><span aria-hidden="true">↓</span></div>
  </div>

  <div class="flow-step">
    <div class="flow-decision">Shell 类调用是否命中确定性破坏性命令拦截规则？</div>
    <div class="flow-branch">
      <span class="flow-branch-label">是</span>
      <span class="flow-branch-arrow" aria-hidden="true">→</span>
      <span class="flow-result flow-result--block">拒绝本次调用</span>
    </div>
  </div>
  <div class="flow-next">
    <div class="flow-down"><span class="flow-down-label">否</span><span aria-hidden="true">↓</span></div>
  </div>

  <div class="flow-step">
    <div class="flow-decision">是否命中用户明确配置的 <code>permissions.ask</code>？</div>
    <div class="flow-branch">
      <span class="flow-branch-label">是</span>
      <span class="flow-branch-arrow" aria-hidden="true">→</span>
      <span class="flow-result flow-result--manual">需要人工确认</span>
    </div>
  </div>
  <div class="flow-next">
    <div class="flow-down"><span class="flow-down-label">否</span><span aria-hidden="true">↓</span></div>
  </div>

  <div class="flow-step">
    <div class="flow-decision">写入类工具的目标路径是否位于工作区外？</div>
    <div class="flow-branch">
      <span class="flow-branch-label">是</span>
      <span class="flow-branch-arrow" aria-hidden="true">→</span>
      <span class="flow-result flow-result--manual">需要人工确认</span>
    </div>
  </div>
  <div class="flow-next">
    <div class="flow-down"><span class="flow-down-label">否</span><span aria-hidden="true">↓</span></div>
  </div>

  <div class="flow-step">
    <div class="flow-decision">此前是否累计阻断与不可用共 20 次，或连续阻断 3 次，或连续不可用 2 次？<small class="flow-section-note">第五节 · 失败计数与降级</small></div>
    <div class="flow-branch">
      <span class="flow-branch-label">是</span>
      <span class="flow-branch-arrow" aria-hidden="true">→</span>
      <span class="flow-result flow-result--manual">需要人工确认</span>
    </div>
  </div>
  <div class="flow-next">
    <div class="flow-down"><span class="flow-down-label">否</span><span aria-hidden="true">↓</span></div>
  </div>

  <div class="flow-review">
    <strong>构造审查上下文 Transcript</strong>
    <span>过滤会话内容、改写历史调用、投影当前参数</span>
    <small class="flow-section-note">第三节 · Transcript 构造</small>
  </div>
  <div class="flow-connector" aria-hidden="true">↓</div>

  <div class="flow-review">
    <strong>两阶段 Classifier 审查</strong>
    <span>Stage 1 快速判断；明确返回阻断时进入 Stage 2 复核</span>
    <small class="flow-section-note">第四节 · 两阶段审查</small>
  </div>
  <div class="flow-connector" aria-hidden="true">↓</div>

  <div class="flow-outcomes">
    <div class="flow-outcome">
      <span class="flow-outcome-label">判定可执行</span>
      <span class="flow-result flow-result--allow">放行</span>
    </div>
    <div class="flow-outcome">
      <span class="flow-outcome-label">明确判定不应执行</span>
      <span class="flow-result flow-result--block">拒绝本次调用</span>
    </div>
    <div class="flow-outcome">
      <span class="flow-outcome-label">Classifier 不可用</span>
      <span class="flow-result flow-result--manual">需要人工确认</span>
    </div>
  </div>

  <div class="flow-manual-route">
    <div class="flow-manual-route-intro">所有“需要人工确认”的分支在此汇合</div>
    <div class="flow-connector" aria-hidden="true">↓</div>
    <div class="flow-manual-decision">是否可交互确认？<small class="flow-section-note">第四节 · 审查不可用时转人工确认</small></div>
    <div class="flow-manual-branches">
      <div class="flow-manual-branch">
        <span class="flow-manual-branch-label">可以（交互式会话）</span>
        <span class="flow-manual-branch-arrow" aria-hidden="true">↙</span>
        <span class="flow-result flow-result--manual">弹出确认，交给用户决定</span>
      </div>
      <div class="flow-manual-branch">
        <span class="flow-manual-branch-label">不可以（普通非交互运行）</span>
        <span class="flow-manual-branch-arrow" aria-hidden="true">↘</span>
        <span class="flow-result flow-result--block">无法确认，拒绝本次调用</span>
      </div>
    </div>
  </div>
</div>

自动审批可能因三类情况变得不可靠：

- **外部内容影响判断**：代码、文件、网页或工具返回中的恶意指令可能通过间接 Prompt 注入影响模型；
- **模型推理出错**：模型可能因幻觉或错误推理，提出误删文件、覆盖敏感配置或强推 Git 分支等越权调用；
- **用户没有表达完整边界**：用户可能遗漏限制条件、表达含糊，或直接提出高风险操作。调用即使字面符合输入，也未必适合不经确认自动执行。

Auto 模式先由确定性规则决定放行、阻断或人工确认，再将仍需判断的调用交给 Classifier；审查不可用或失败计数达到阈值时，转入人工确认流程。

后文分别分析快速通道、Transcript、两阶段 Classifier 与连续失败计数如何支撑这套自动审批流程。

---

## 二、快速通道：哪些调用不必经过 Classifier

Auto Mode 要自动审批工具调用，首先要回答：哪些调用不需要理解自然语言意图，也能被规则可靠判断？如果所有工具调用都进入 Classifier，读文件、搜索文件和普通代码编辑也要等待模型响应，Auto Mode 会失去流畅性。快速通道把这类边界清晰的调用直接放行，把 Classifier 留给必须理解用户意图或工具参数的调用。

源码提供两类快速通道：

- **工作区内普通编辑**：目标位于 workspace 内、不是特殊持久化或执行入口的 `edit` / `write_file`；
- **静态安全工具白名单**：只读等影响范围有限的内建工具。

快速通道不等于“这些调用绝对没有风险”。它的取舍是：用户已将 workspace 交给 Agent 操作时，用受限的工具类型和路径范围换取无需 LLM 审查的速度。对于 `.git/`、`.husky/`、`package.json`、CI 配置等会影响后续执行的特殊路径，编辑不会走这条快速通道。

用户配置的 `permissions.ask` 会使快速通道失效，为本来可以自动放行的操作增加确认要求；若 Shell 类调用命中后续的确定性破坏性命令拦截规则，则仍直接阻断，不进入人工确认。

---

## 三、Transcript 构造：为 Classifier 准备安全的审查上下文

当规则无法可靠自动批准一个调用时，Classifier 必须结合用户意图与调用参数作出判断。它需要会话上下文，但完整会话中含有可能误导审查的外部内容和大量无关输出。`Transcript` 是源码中为解决这一矛盾而准备的裁剪版会话历史：它保留判断所需的信息，移除不应作为判断依据的内容。Stage 1 和 Stage 2 都使用同一份 Transcript 作为审查输入。

### 1. 构造流程总览

Transcript 从主会话最近 40 条消息和当前待审调用构造，分别进行过滤、改写和参数投影，供 Stage 1 和 Stage 2 使用。

<div id="qwen-auto-mode-transcript-construction" role="img" aria-label="近期会话与当前调用到 Transcript 的构造流水线">
<div class="construct-flow">
<div class="construct-card construct-input">
<strong>输入：最近 40 条会话消息 + 当前调用</strong>
<ul>
<li>用户原始文本</li>
<li>主 Agent 的回复</li>
<li>历史工具调用</li>
<li>工具执行结果</li>
<li>当前待审工具调用</li>
</ul>
</div>
<div class="construct-arrow" aria-hidden="true">→</div>
<div class="construct-process">
<div class="construct-action construct-remove"><strong>不写入 Transcript</strong><span>主 Agent 的回复、工具执行结果；主会话 System Prompt 也不会复制过来</span></div>
<div class="construct-action construct-keep"><strong>原样保留</strong><span>最近 40 条会话消息中的用户文本不做摘要或改写</span></div>
<div class="construct-action construct-keep"><strong>改写历史调用</strong><span>将窗口内的历史工具调用转成普通文本</span></div>
<div class="construct-action construct-limit"><strong>投影当前调用</strong><span>按工具类型提取安全相关参数；仅 edit 和 write_file 的长内容预览限制为前 300 字符</span></div>
</div>
<div class="construct-arrow" aria-hidden="true">→</div>
<div class="construct-card construct-output">
<strong>Transcript</strong>
<span>用户原始文本 + 历史调用文本 + 当前调用参数投影</span>
</div>
</div>
</div>

构造 Transcript 时，系统先从主会话中取最近 **40 条消息**：`MAX_TRANSCRIPT_MESSAGES = 40`，再对它们进行过滤和改写，最后追加当前待审调用。源码注释将这一选择解释为：在 FastModel 的上下文预算内保留足够的近期操作链，避免长时间运行的会话因历史无限增长而使 Classifier 上下文溢出。笔者认为，40 条主要是在保留足够历史信息与控制 Token 消耗之间取的平衡，同时也兼顾审批延迟；随着模型服务速度提高、调用成本降低，这一上限可以进一步增大。

**为什么按消息条数，而不是 Token 数限制历史长度？**
源码未说明这一选择的原因。笔者认为，按消息条数限制无需额外估算 Token 数，实现更简单；代价是消息长短不一，实际 Token 消耗并不固定。

### 2. 哪些内容不写入 Transcript，为什么

完整会话中的信息并非都适合作为审批依据。Transcript 不写入以下内容：

| 不写入的内容 | 不写入的原因 | 避免的问题 |
| :--- | :--- | :--- |
| **主 Agent 的回复** | 主 Agent 是被审查对象，其回复不能作为调用已获授权的依据；回复中的工具调用会单独提取并改写后保留 | 避免主 Agent 通过自我背书影响 Classifier 判断 |
| **工具执行结果** | 文件、网页和终端输出属于外部不可信内容，可能包含恶意指令或大量无关信息 | 降低间接 Prompt 注入风险，同时减少 Token 消耗与审批延迟 |
| **主会话的 System Prompt** | Classifier 使用独立的系统提示定义审查规则，不继承主 Agent 的角色和行为指令 | 保持审批规则与主 Agent 相互隔离 |

### 3. 哪些内容会写入 Transcript，如何处理

Transcript 包含窗口内的用户文本、改写后的历史工具调用和当前调用的参数投影。用户文本原样保留，作为判断用户意图的主要依据；窗口外的早期消息不进入本次 Transcript。

#### 此前工具调用如何保留

此前的工具调用不会保留为原生 Function Call，而会改写成普通的 `user` 文本：

```text
Prior action: shell({"command":"ls -la"})
```

这种改写既保留了操作历史，也避免原生 `tool_call` 在工具执行结果已被删除后失去对应回应，违反工具调用与工具结果必须成对出现的协议约束。历史调用统一转换为普通文本后，也更便于不同模型服务复用。

历史调用还受字符预算限制：单条文本保留前 4000 字符并附截断标记，总预算为 40000 字符。预算优先分配给较新的调用；较旧调用超出预算时，仅保留工具名与省略标记。这些限制针对历史调用，当前待审调用仍按工具自身的投影规则处理。

#### 当前待审工具调用保留哪些参数

每种工具通过 `toAutoClassifierInput()` 提供与安全判断相关的参数摘要：

| 工具类别 | 投影暴露内容 (`toAutoClassifierInput`) | 设计考量与安全权衡 |
| :--- | :--- | :--- |
| `shell` / `monitor` | **完整 `command` + `cwd`** | 命令行字符串与工作目录是判断操作影响范围和潜在风险的关键信息，因此需要完整保留。 |
| `edit` | **`file_path` + old/new 前 300 字符 + `lines_changed` + 截断标识** | 只提供内容开头的预览和是否截断的标记，在审查线索与 Token 成本之间取舍；第 300 个字符之后的内容不会被 Classifier 看到，因此这不是完整内容安全检查。 |
| `write_file` | **`file_path` + `byte_count` + content 前 300 字符 + 截断标识** | 同样只提供内容预览、文件大小和截断信息；长内容的后半部分不在审查上下文中。 |
| `web_fetch` | **仅目标 URL，不传递 `prompt`** | URL 用于判断外部访问边界；`prompt` 可能包含敏感上下文，因此不发送给 Classifier。 |
| `agent`（子任务） | **完整 `prompt`、`subagent_type`、`working_dir` 及 fork 相关信息** | prompt 和运行参数共同决定子 Agent 的任务与执行范围，需要完整提供给 Classifier 判断风险。 |
| MCP 第三方工具 | **工具身份、注解及受限的结构化参数投影** | 参数投影限制单个字符串、总字符数、嵌套深度和条目数量，并标记截断；也可以通过 `permissions.autoMode.mcp.forwardArguments: false` 关闭参数转发。 |

*(注：`read_file` 等安全工具在未匹配用户确认规则时可直接放行；其历史调用仍可能经参数投影后写入后续审查的 Transcript。)*

<style scoped>
#qwen-auto-mode-transcript-construction {
  --doc-text: #111827;
  --doc-muted: #1f2937;
  --doc-border: #9ca3af;
  --doc-card: #f9fafb;
  --doc-soft: #f3f4f6;
  --doc-brand: #2563eb;
  --doc-brand-soft: #dbeafe;
  --doc-green: #15803d;
  --doc-green-soft: #dcfce7;
  --doc-green-border: #86efac;
  --doc-yellow: #a16207;
  --doc-yellow-soft: #fef9c3;
  --doc-yellow-border: #fde047;
  --doc-red: #b91c1c;
  --doc-red-soft: #fee2e2;
  --doc-red-border: #fca5a5;
  --doc-shadow: 0 1px 3px rgb(0 0 0 / 0.1);
  --construct-line: var(--doc-muted);
  --construct-border: var(--doc-border);
  margin: 2rem 0;
  color: var(--doc-text);
  font-family: Inter, ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.5;
}

#qwen-auto-mode-transcript-construction * {
  box-sizing: border-box;
}

#qwen-auto-mode-transcript-construction .construct-flow {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 3rem minmax(0, 1.5fr) 3rem minmax(0, 1fr);
  gap: 0.75rem;
  align-items: stretch;
}

#qwen-auto-mode-transcript-construction .construct-card {
  padding: 1rem;
  border: 1px solid var(--construct-border);
  border-radius: 0.75rem;
  background: var(--doc-card);
  box-shadow: var(--doc-shadow);
}

#qwen-auto-mode-transcript-construction .construct-card strong {
  display: block;
  margin-bottom: 0.55rem;
  text-align: center;
}

#qwen-auto-mode-transcript-construction .construct-card ul {
  margin: 0;
  padding-left: 1.05rem;
  color: var(--doc-muted);
  font-size: 0.86rem;
}

#qwen-auto-mode-transcript-construction .construct-card li + li {
  margin-top: 0.25rem;
}

#qwen-auto-mode-transcript-construction .construct-input {
  border-color: var(--doc-brand);
  background: var(--doc-brand-soft);
}

#qwen-auto-mode-transcript-construction .construct-process {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

#qwen-auto-mode-transcript-construction .construct-action {
  padding: 0.8rem;
  border: 1px solid var(--construct-border);
  border-radius: 0.75rem;
  background: var(--doc-card);
  box-shadow: var(--doc-shadow);
}

#qwen-auto-mode-transcript-construction .construct-action strong {
  display: block;
  margin-bottom: 0.3rem;
}

#qwen-auto-mode-transcript-construction .construct-remove {
  border-color: var(--doc-red-border);
  background: var(--doc-red-soft);
}

#qwen-auto-mode-transcript-construction .construct-keep {
  border-color: var(--doc-green-border);
  background: var(--doc-green-soft);
}

#qwen-auto-mode-transcript-construction .construct-limit {
  border-color: var(--doc-yellow-border);
  background: var(--doc-yellow-soft);
}

#qwen-auto-mode-transcript-construction .construct-output {
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-color: var(--doc-green-border);
  background: var(--doc-green-soft);
  font-weight: 700;
}

#qwen-auto-mode-transcript-construction .construct-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--construct-line);
  font-size: 1.5rem;
  font-weight: 700;
}

@media (max-width: 640px) {
  #qwen-auto-mode-transcript-construction .construct-flow {
    grid-template-columns: 1fr;
  }

  #qwen-auto-mode-transcript-construction .construct-arrow {
    min-height: 2rem;
    font-size: 1.25rem;
  }

  #qwen-auto-mode-transcript-construction .construct-arrow::before {
    content: '↓';
  }

  #qwen-auto-mode-transcript-construction .construct-arrow {
    font-size: 0;
  }

  #qwen-auto-mode-transcript-construction .construct-arrow::before {
    font-size: 1.25rem;
  }
}
</style>

Transcript 通过过滤和裁剪减少不可信内容与审查成本，代价是丢失窗口外的历史及被截断的内容。

---

## 四、两阶段 Classifier：先快速判断，再进行复核

### 1. 先快速判断，再复核阻断结果

为每次调用都进行深度审查会增加延迟与 Token 成本。Stage 1 先以较小预算判断，允许则直接放行，明确阻断才进入 Stage 2 复核，以减少正常操作被误拦的情况；审查不可用则转人工确认。

两个阶段使用同一份 Transcript 和同一个 FastModel（`config.getFastModel()`），但采用不同的提示、输出预算与超时设置，具体配置如下：

<style scoped>
#qwen-auto-mode-two-stage-review {
  --doc-text: #111827;
  --doc-muted: #1f2937;
  --doc-border: #9ca3af;
  --doc-card: #f9fafb;
  --doc-soft: #f3f4f6;
  --doc-brand: #2563eb;
  --doc-brand-soft: #dbeafe;
  --doc-green: #15803d;
  --doc-green-soft: #dcfce7;
  --doc-green-border: #86efac;
  --doc-yellow: #a16207;
  --doc-yellow-soft: #fef9c3;
  --doc-yellow-border: #fde047;
  --doc-red: #b91c1c;
  --doc-red-soft: #fee2e2;
  --doc-red-border: #fca5a5;
  --doc-shadow: 0 1px 3px rgb(0 0 0 / 0.1);
  --stage-line: var(--doc-muted);
  --stage-border: var(--doc-border);
  margin: 2rem 0;
  color: var(--doc-text);
  font-family: Inter, ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.5;
}

#qwen-auto-mode-two-stage-review * {
  box-sizing: border-box;
}

#qwen-auto-mode-two-stage-review .stage-flow {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(8rem, 0.45fr) minmax(0, 1fr);
  gap: 0.85rem;
  align-items: stretch;
}

#qwen-auto-mode-two-stage-review .stage-card {
  display: flex;
  min-height: 12rem;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--stage-border);
  border-radius: 0.75rem;
  background: var(--doc-card);
  box-shadow: var(--doc-shadow);
}

#qwen-auto-mode-two-stage-review .stage-input {
  margin-bottom: 1rem;
  padding: 0.8rem 1rem;
  border: 1px solid var(--doc-brand);
  border-radius: 999px;
  background: var(--doc-brand-soft);
  font-weight: 700;
  text-align: center;
}

#qwen-auto-mode-two-stage-review .stage-input span {
  color: var(--doc-muted);
  font-size: 0.82rem;
  font-weight: 600;
}

#qwen-auto-mode-two-stage-review .stage-card strong {
  text-align: center;
}

#qwen-auto-mode-two-stage-review .stage-model {
  border-radius: 999px;
  padding: 0.2rem 0.65rem;
  background: var(--doc-soft);
  color: var(--doc-muted);
  font-size: 0.82rem;
  font-weight: 700;
  text-align: center;
}

#qwen-auto-mode-two-stage-review .stage-item {
  display: grid;
  grid-template-columns: 6.25rem minmax(0, 1fr);
  gap: 0.5rem;
  align-items: baseline;
  margin: 0;
}

#qwen-auto-mode-two-stage-review .stage-item span:first-child {
  color: var(--doc-muted);
  font-size: 0.82rem;
}

#qwen-auto-mode-two-stage-review .stage-item span:last-child {
  font-weight: 650;
}

#qwen-auto-mode-two-stage-review .stage-one {
  border-color: var(--doc-green-border);
  background: var(--doc-green-soft);
}

#qwen-auto-mode-two-stage-review .stage-two {
  border-color: var(--doc-brand);
  background: var(--doc-brand-soft);
}

#qwen-auto-mode-two-stage-review .stage-gate {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  color: var(--stage-line);
  font-weight: 700;
  text-align: center;
}

#qwen-auto-mode-two-stage-review .stage-gate-label {
  max-width: 8rem;
  border-radius: 999px;
  padding: 0.16rem 0.65rem;
  background: var(--doc-soft);
  color: var(--doc-muted);
  font-size: 0.78rem;
}

#qwen-auto-mode-two-stage-review .stage-gate-arrow {
  font-size: 1.5rem;
}

@media (max-width: 640px) {
  #qwen-auto-mode-two-stage-review .stage-flow {
    display: flex;
    flex-direction: column;
  }

  #qwen-auto-mode-two-stage-review .stage-card {
    width: 100%;
    min-height: 0;
  }

  #qwen-auto-mode-two-stage-review .stage-gate {
    min-height: 3rem;
  }

  #qwen-auto-mode-two-stage-review .stage-gate-arrow {
    display: block;
    line-height: 1;
    transform: rotate(90deg);
  }
}
</style>

<div id="qwen-auto-mode-two-stage-review" role="img" aria-label="同一个 Transcript 输入与同一个 FastModel 的两阶段审查配置">
<div class="stage-input">同一份 Transcript <span>作为 Stage 1 与 Stage 2 的审查输入</span></div>
<div class="stage-flow">
<div class="stage-card stage-one">
<strong>Stage 1：快速判断</strong>
<span class="stage-model">同一个 <code>fastModel</code></span>
<p class="stage-item"><span>分析过程</span><span>不返回</span></p><p class="stage-item"><span>输出预算</span><span>256 tokens</span></p><p class="stage-item"><span>默认超时</span><span>10 秒</span></p><p class="stage-item"><span>返回结果</span><span>是否阻断（<code>shouldBlock</code>）</span></p>
</div>
<div class="stage-gate">
<span class="stage-gate-label">Stage 1 返回 <code>shouldBlock=true</code></span>
<span class="stage-gate-arrow" aria-hidden="true">→</span>
</div>
<div class="stage-card stage-two">
<strong>Stage 2：复核</strong>
<span class="stage-model">同一个 <code>fastModel</code></span>
<p class="stage-item"><span>分析过程</span><span>返回文本分析</span></p><p class="stage-item"><span>输出预算</span><span>4096 tokens</span></p><p class="stage-item"><span>默认超时</span><span>30 秒</span></p><p class="stage-item"><span>返回结果</span><span>分析过程、阻断结论、判断理由<br><code>{thinking, shouldBlock, reason}</code></span></p>
</div>
</div>
</div>

Stage 1 的输出预算为自适应思考预留余量，Stage 2 则为复核提供更大的分析空间。Stage 2 要求模型在响应的 `thinking` 字段中写出分析过程。这属于普通文本输出；模型 API 的思考功能默认关闭，可通过 `stage2ThinkingEnabled` 开启。

### 2. 审查不可用时转人工确认

Classifier 在网络超时、API 报错、返回格式无法解析或上下文溢出等情况下，会将结果标记为 `unavailable`。调度器记录不可用计数，并将当前调用转入人工确认流程；普通非交互运行无法弹出确认时，会拒绝执行。如果连续两次无法完成审查且计数未被重置，下一条仍需送审的调用会跳过 Classifier，直接进入人工确认流程。

前两行是本次 Classifier 审查的结果；第三行是在当前调用送审前，根据此前失败计数作出的降级决定。

| 当前调用的处理条件 | 交互式会话中本次调用 | 普通非交互运行中本次调用 |
| :--- | :--- | :--- |
| Classifier 明确阻断 | 直接拒绝 | 直接拒绝 |
| Classifier 不可用 | 转人工确认 | 因无法确认而拒绝 |
| 此前失败计数已达到阈值，跳过 Classifier | 转人工确认 | 因无法确认而拒绝 |

---

## 五、失败计数与降级：避免自动审批无限重试

自动审批不能无限重试。即使每一次调用都被正确阻断，Agent 也可能不断换写法继续送审；审查服务暂时不可用时，重复请求同样只会增加等待和 Token 消耗。连续失败计数用于识别这两种“自动审批无法继续可靠工作”的情况，并在达到阈值后把下一条需要审查的调用交给用户确认。

### 1. 连续失败如何触发人工确认

源码将这组逻辑放在 `denialTracking.ts` 中。对未被前置规则处理、仍需送审的调用，系统先检查失败计数；累计阻断与不可用达到 20 次、连续阻断达到 3 次或连续不可用达到 2 次时，跳过 Classifier，直接转人工确认。累计上限优先于连续阈值判断。

<style scoped>
#qwen-auto-mode-fallback-timeline {
  --doc-text: #111827;
  --doc-muted: #1f2937;
  --doc-border: #9ca3af;
  --doc-card: #f9fafb;
  --doc-soft: #f3f4f6;
  --doc-brand: #2563eb;
  --doc-brand-soft: #dbeafe;
  --doc-green: #15803d;
  --doc-green-soft: #dcfce7;
  --doc-green-border: #86efac;
  --doc-yellow: #a16207;
  --doc-yellow-soft: #fef9c3;
  --doc-yellow-border: #fde047;
  --doc-red: #b91c1c;
  --doc-red-soft: #fee2e2;
  --doc-red-border: #fca5a5;
  --doc-shadow: 0 1px 3px rgb(0 0 0 / 0.1);
  --timeline-line: var(--doc-muted);
  --timeline-border: var(--doc-border);
  margin: 2rem 0;
  color: var(--doc-text);
  font-family: Inter, ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.5;
}

#qwen-auto-mode-fallback-timeline * {
  box-sizing: border-box;
}

#qwen-auto-mode-fallback-timeline .timeline-phase {
  display: grid;
  grid-template-columns: 7rem minmax(0, 1fr);
  gap: 1rem;
  align-items: stretch;
}

#qwen-auto-mode-fallback-timeline .timeline-label {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--timeline-border);
  border-radius: 0.75rem;
  background: var(--doc-card);
  color: var(--doc-muted);
  font-weight: 700;
  text-align: center;
}

#qwen-auto-mode-fallback-timeline .timeline-card {
  padding: 1rem 1.15rem;
  border: 1px solid var(--timeline-border);
  border-radius: 0.75rem;
  background: var(--doc-card);
  box-shadow: var(--doc-shadow);
}

#qwen-auto-mode-fallback-timeline .timeline-card strong {
  display: block;
  margin-bottom: 0.3rem;
}

#qwen-auto-mode-fallback-timeline .timeline-card span {
  color: var(--doc-muted);
  font-size: 0.9rem;
}

#qwen-auto-mode-fallback-timeline .timeline-connector {
  display: grid;
  grid-template-columns: 7rem minmax(0, 1fr);
  gap: 1rem;
  min-height: 2.75rem;
}

#qwen-auto-mode-fallback-timeline .timeline-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--timeline-line);
  font-size: 1.25rem;
  font-weight: 700;
}

#qwen-auto-mode-fallback-timeline .timeline-check {
  border-color: var(--doc-brand);
  background: var(--doc-brand-soft);
}

#qwen-auto-mode-fallback-timeline .timeline-branches {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
  margin: 1rem 0 0 8rem;
}

#qwen-auto-mode-fallback-timeline .timeline-branch {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  align-items: center;
}

#qwen-auto-mode-fallback-timeline .timeline-branch-label {
  border-radius: 999px;
  padding: 0.12rem 0.55rem;
  background: var(--doc-soft);
  color: var(--doc-muted);
  font-size: 0.78rem;
  font-weight: 700;
}

#qwen-auto-mode-fallback-timeline .timeline-result {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid var(--timeline-border);
  border-radius: 0.75rem;
  text-align: center;
  font-weight: 700;
}

#qwen-auto-mode-fallback-timeline .timeline-result--review {
  border-color: var(--doc-brand);
  background: var(--doc-brand-soft);
}

#qwen-auto-mode-fallback-timeline .timeline-result--manual {
  border-color: var(--doc-yellow-border);
  background: var(--doc-yellow-soft);
  color: var(--doc-yellow);
}

#qwen-auto-mode-fallback-timeline .timeline-reset {
  margin-top: 0.45rem;
  color: var(--doc-muted);
  font-size: 0.85rem;
  text-align: center;
}

@media (max-width: 640px) {
  #qwen-auto-mode-fallback-timeline .timeline-phase,
  #qwen-auto-mode-fallback-timeline .timeline-connector {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  #qwen-auto-mode-fallback-timeline .timeline-label {
    width: fit-content;
    margin: 0 auto;
    padding: 0.3rem 0.75rem;
  }

  #qwen-auto-mode-fallback-timeline .timeline-connector > :first-child {
    display: none;
  }

  #qwen-auto-mode-fallback-timeline .timeline-branches {
    grid-template-columns: 1fr;
    margin-left: 0;
  }
}
</style>

<div id="qwen-auto-mode-fallback-timeline" role="img" aria-label="连续失败计数跨工具调用生效的时序">
  <div class="timeline-phase">
    <div class="timeline-label">此前调用</div>
    <div class="timeline-card">
      <strong>Classifier 更新连续失败计数</strong>
      <span>明确阻断时记录 <code>consecutiveBlock</code>；审查不可用时记录 <code>consecutiveUnavailable</code></span>
    </div>
  </div>

  <div class="timeline-connector" aria-hidden="true">
    <span></span>
    <span class="timeline-arrow">↓</span>
  </div>

  <div class="timeline-phase">
    <div class="timeline-label">本次调用</div>
    <div class="timeline-card timeline-check">
      <strong>在送交 Classifier 前读取计数</strong>
      <span>此前是否累计阻断与不可用共 20 次，或连续阻断 3 次，或连续不可用 2 次？</span>
    </div>
  </div>

  <div class="timeline-branches">
    <div class="timeline-branch">
      <span class="timeline-branch-label">否</span>
      <div class="timeline-result timeline-result--review">继续两阶段 Classifier 审查</div>
    </div>
    <div class="timeline-branch">
      <span class="timeline-branch-label">是</span>
      <div class="timeline-result timeline-result--manual">跳过 Classifier，本次调用转人工确认</div>
      <span class="timeline-reset">用户批准后，两个连续计数归零</span>
    </div>
  </div>
</div>

达到阈值只会让本次原本需要 Classifier 审查的调用转人工确认，会话仍保持在 AUTO 模式，快速通道中的调用继续自动执行。

### 2. 两类连续失败为什么分开记录

源码注释说明，阻断与不可用代表不同的失败类型，因此连续次数不混合累计：阻断表示调用未获批准，不可用表示审查未能完成。分别计数用于判断哪类问题在持续，交替出现的失败则由累计上限兜底。`denialTracking.ts` 中的两类连续计数如下：

| 计数器 | 何时增加 | 达到阈值后的下一条调用 | 追踪的问题 |
| :--- | :--- | :--- | :--- |
| **连续被阻断次数**（`consecutiveBlock`） | Classifier 明确阻断或命中确定性破坏性命令拦截 | 连续 **3 次**后，下一条仍需送审的调用跳过 Classifier，直接转人工确认 | 调用反复未获批准；阈值用于防止循环，不代表允许重试被拒绝的操作。 |
| **连续不可用次数**（`consecutiveUnavailable`） | Classifier 无法完成审查；当前调用已转入人工确认流程 | 连续 **2 次**后，下一条仍需送审的调用跳过 Classifier，直接转人工确认 | 审查服务持续未能完成判断，继续请求会增加等待与成本。 |

出现阻断或不可用时，该类连续计数加一，另一类归零；放行时，两类连续计数都归零。例如，连续结果为“不可用 → 明确阻断 → 不可用 → 不可用”时：

| 审查结果 | 连续被阻断次数 | 连续不可用次数 |
| :--- | ---: | ---: |
| 初始状态 | 0 | 0 |
| 不可用 | 0 | 1 |
| 明确阻断 | 1 | 0 |
| 不可用 | 0 | 1 |
| 不可用 | 0 | 2，下一次调用转人工确认 |

因此，两种连续计数分别追踪操作被阻断与审查服务不可用，避免把不同问题混合累计。除此之外，系统保留累计阻断与不可用总数，上限为 **20 次**；即使阻断、不可用和放行交替出现，累计上限仍能阻止反复送审。

快速通道、权限规则或 Classifier 放行都会清零两个连续计数，但保留累计总数。确定性破坏性命令拦截也计入阻断次数。上表仅展示没有放行或人工批准介入时的计数变化。

### 3. 人工确认后如何恢复

- **用户批准降级确认中的调用后**（`recordFallbackApprove`）：两个连续计数归零；若已达到累计上限，累计计数也归零，后续调用恢复正常审批流程。普通 `permissions.ask` 确认不触发该重置；
- **用户拒绝或取消降级确认**：计数保持不变；
- **切换 ApprovalMode**：连续与累计计数全部归零。

---

## 六、Classifier 模型的配置建议

Qwen Code 可以单独配置 **FastModel**，Auto Mode 的两阶段审查都使用这一模型。配置时主要考虑三个维度：

- **判断能力**：选择能准确判断调用风险与用户授权范围的模型；
- **审查效率**：选择响应快、支持关闭思考功能的模型，以控制审批延迟和 Token 成本；
- **数据安全**：Classifier 会接收用户意图、工具参数和部分工作区内容，所选模型服务的数据安全保障不应低于主模型服务。

---

## 七、总结：Auto Mode 的关键设计

Auto Mode 的核心不是让 Agent 永远自动执行，而是按调用能否被可靠判断来分配决策方式：

1. **快速通道**：用受限的工具和路径范围，让边界清晰的调用无需等待 LLM；
2. **Transcript 构造**：用经过过滤、改写和截断的上下文，降低审查输入被外部内容误导的风险，同时限制 Token 成本；
3. **两阶段 Classifier**：先用低成本判断放行明确安全的调用，只为疑难调用支付深度复核成本；
4. **连续失败计数**：当自动审查连续不能收敛时，停止重复请求并将下一条送审调用交给用户。

---

## 八、术语速查

| 术语 | 定义与关系 |
| :--- | :--- |
| **主 Agent** | 主会话（session）中直接与用户对话交互的 Agent。 |
| **工具调用** | 对工具的一次执行请求，包含工具名和参数；提出请求不代表已经执行。 |
| **审批模式** | 决定工具调用如何获得执行许可的运行配置，如 Default、YOLO、Auto 等。 |
| **Auto Mode** | 结合确定性规则、模型审查与人工确认的审批模式。 |
| **Classifier** | 在 Auto 模式下审查待执行调用的模型审查器；规则已处理的调用不必经过它。 |
| **FastModel** | Qwen Code 中可单独配置、用于辅助任务的模型；Classifier 的两个阶段都使用它。 |
| **Transcript** | 从近期会话消息和当前调用构造的审查上下文，供 Classifier 判断使用。 |
| **参数投影** | 将原始工具参数转换为供 Classifier 使用的参数表示，包括字段选择、内容截取和结构整理。 |

---

## 参考与源码溯源

本文分析基于官方仓库 [QwenLM/qwen-code](https://github.com/QwenLM/qwen-code) `main` 分支（commit: [`9c320cb0c`](https://github.com/QwenLM/qwen-code/commit/9c320cb0cc328dc91b362516b630ae4a3dcdd15d)），相关核心模块的源码相对路径如下：

- 核心审批模式主控与分层漏斗：[`packages/core/src/permissions/autoMode.ts`](https://github.com/QwenLM/qwen-code/blob/9c320cb0cc328dc91b362516b630ae4a3dcdd15d/packages/core/src/permissions/autoMode.ts)
- 核心分类器编排与两阶段实现：[`packages/core/src/permissions/classifier.ts`](https://github.com/QwenLM/qwen-code/blob/9c320cb0cc328dc91b362516b630ae4a3dcdd15d/packages/core/src/permissions/classifier.ts)
- 审查上下文的过滤与投影：[`packages/core/src/permissions/classifier-transcript.ts`](https://github.com/QwenLM/qwen-code/blob/9c320cb0cc328dc91b362516b630ae4a3dcdd15d/packages/core/src/permissions/classifier-transcript.ts)
- 连续失败计数与降级逻辑：[`packages/core/src/permissions/denialTracking.ts`](https://github.com/QwenLM/qwen-code/blob/9c320cb0cc328dc91b362516b630ae4a3dcdd15d/packages/core/src/permissions/denialTracking.ts)
- 调度层的降级短路处理：[`packages/core/src/core/coreToolScheduler.ts`](https://github.com/QwenLM/qwen-code/blob/9c320cb0cc328dc91b362516b630ae4a3dcdd15d/packages/core/src/core/coreToolScheduler.ts)
