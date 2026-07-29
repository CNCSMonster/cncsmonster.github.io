+++
title = "Qwen Code Auto Mode Classifier：两阶段 LLM 审批机制解析"
date = 2026-07-29T00:00:00+08:00
slug = "qwen-code-auto-mode-classifier"
[taxonomies]
    tags = ["Qwen Code", "AI Agent", "LLM", "安全", "Coding Assistant"]
+++

> 本文基于 Qwen Code `0.20.1-preview.7215` 版本的编译源码分析。preview 版本的机制可能随版本变化。

Qwen Code 提供五种审批模式：`plan`（计划）、`default`（默认确认）、`auto-edit`（自动编辑）、`auto`（自动审批）、`yolo`（全部自动）。在这个版本中，**新用户安装后默认就是 auto 模式**——工具调用不需要逐个确认，而是通过多层过滤自动判断每个操作是否安全。我平时使用也推荐 auto 模式，它在效率和安全之间取得了很好的平衡。本文拆解这个机制的工作原理和配置方式。

## 整体架构

Auto mode 的自动审批机制由四个部分组成：

1. **规则层**：确定性规则（工具默认权限、用户自定义规则、白名单、正则拦截），快速过滤掉明确安全或明确危险的操作
2. **LLM 判断层**：两阶段 Classifier，处理规则覆盖不了的模糊地带
3. **Fail-closed**：classifier 出错时默认阻止——宁可错杀不放过
4. **安全网**：Denial Tracking，检测 LLM 和 classifier 的死循环，必要时降级为人工确认

一个工具调用的完整生命周期：

```
LLM 返回 [A, B, C]
  → 每个独立走审批流程：
    ①-⑤ 规则层 → ⑥ LLM 判断层
    → A 放行 → 执行 → 返回结果
    → B 阻止 → 跳过
    → C 放行 → 执行 → 返回结果
  → 所有结果一起回传 LLM
  → LLM 看到完整画面后决定下一步
```

## 规则层：①-⑤

Qwen Code 在执行工具调用（读文件、跑命令、改代码等）之前，会依次经过以下检查：

```
工具调用
  → ① 工具自身默认权限（比如 read_file 默认安全，shell 命令默认需要审批）
  → ② PermissionManager（用户自定义规则引擎）
  → ③ acceptEdits fast-path（如果当前是 acceptEdits 模式，工作区内编辑直接放行）
  → ④ 安全工具白名单（read_file、grep、glob 等只读工具直接放行）
  → ⑤ Guard（正则拦截危险命令模式，如 git clean、rm -rf 等，不经过 LLM）
  → ⑥ LLM Classifier（两阶段 LLM 判断，见下节）
```

② 是用户可配置的规则引擎，返回四种结果：

- `allow` → 直接放行（跳过 ③-⑥）
- `deny` → 直接阻止
- `ask` → 弹出确认框，等用户手动决定
- `default`（无规则匹配）→ 继续 ③-⑥

## 两阶段 Classifier

前五步都是确定性规则——快、免费，但覆盖不了所有情况。剩下的工具调用交给 LLM 判断。Classifier 收到的是工具名称、参数和当前对话上下文，分两步走：

### Stage 1：快速判断

- 模型：fastModel（未配置则 fallback 到主模型）
- 输出：仅 `{shouldBlock: boolean}`
- 超时：10 秒
- 行为：说 allow → 立即放行；说 block → 进入 Stage 2

### Stage 2：复核

- 模型：同 Stage 1
- 输出：`{thinking, shouldBlock, reason}`
- 超时：30 秒
- 行为：说 allow → 放行；说 block → 阻止

Stage 2 输出中的 `thinking` 是模型写的一段判断依据文本（比如"用户只是读取文件，安全"），帮助开发者理解 classifier 为什么做了这个决定。

### Fail-closed：宁可错杀

任何非主动中断的失败（API 错误、超时、响应格式不对）都返回 `shouldBlock: true`。这意味着 **classifier 挂掉 = 所有需要审批的工具都被 block**。这不是 bug，是安全设计。

### 模型优先级

```javascript
override → config.getFastModel() → config.getModel() → DEFAULT_QWEN_MODEL
```

Classifier 使用 fastModel。不配置时 fallback 到主模型，但主模型通常更慢——Stage 1 每次判断大约多花几百毫秒到几秒不等，积少成多。

## Denial Tracking：防死循环

如果 classifier 持续 block（LLM 卡在死胡同），系统不会无限循环：

| 计数器 | 阈值 | 效果 |
|--------|------|------|
| 连续 block | 3 次 | 下一个工具调用跳过 classifier，直接弹人工确认 |
| 连续 unavailable | 2 次 | 同上 |
| 总计 denial | 20 次 | 触发总额上限 |

以上阈值为硬编码，不可配置。切换审批模式时所有计数器重置。

几个关键点：

- **按工具调用累计**，不是按批次——一批有 2 个 block 就加 2
- **降级发生在 classifier 之前**——连续 3 次后第 4 次不再浪费 LLM 调用，直接问人
- **用户批准后计数器归零**，恢复自动模式；拒绝则不重置，下一个继续人工确认
- **跨轮次累计**——LLM 每轮看到被拒结果后换个方式再试，连续 3 次被拒就降级

## 配置建议

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

**关键配置**：`fastModel` 是 classifier 的核心依赖。不配置时 fallback 到主模型，但主模型通常更慢——每个需要 classifier 判断的工具调用都会多等一段时间。

选型建议：选一个**快的**模型。classifier 只需要输出一个布尔值或一段简短文本，不需要深度推理。不思考的模型（如 `qwen3-coder-plus`）天然适合；有思考能力的模型（如 `deepseek-v4-flash`）也可以——classifier 两阶段都默认不开 API 思考模式，模型不会在内部做额外推理，一样很快。如果本地资源充足，配一个本地小模型当 fastModel 也行——零 API 成本，响应还快。

唯一不建议的：某个模型**强制开启思考**（无法通过参数关闭），用在 fastModel 上每次判断都会多花思考的时间和 token。另外，classifier 能看到对话上下文和工具参数，fastModel 的服务提供商安全性应不低于主模型。

`stage2Enabled` 控制 Stage 2 是否让模型走 API 深度推理模式（更慢、更多 token）。默认 `false` 即可——Stage 2 输出中的 `thinking` 字段不受影响，它只是模型写的一段普通文本解释。

## 总结

Qwen Code 的 auto mode 不是简单的"全部自动执行"，而是一个精心设计的安全阀门：规则层挡在前面，LLM classifier 做模糊地带的判断，fail-closed 保证出错时不会放行，denial tracking 防止死循环。代价是每个需要判断的工具调用都要多花一次 LLM 调用的时间和 token。
