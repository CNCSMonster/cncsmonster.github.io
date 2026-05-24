+++
title = "pi-local-ocr 扩展的设计过程"
date = 2026-05-24
tags = ["AI Code CLI", "扩展开发", "设计笔记", "OCR"]
+++

为没有 vision 能力的模型做了一个本地 OCR 扩展，让模型通过 EasyOCR 读取图片中的文字和表格。

## 关键决策

| 决策 | 选择 | 原因 |
|------|------|------|
| Extension vs Skill | Extension | 20 token vs 500 token 上下文污染，TypeBox 参数校验，零幻觉 |
| EasyOCR vs PaddleOCR | EasyOCR | PaddleOCR 预编译二进制要求 AVX512，本机 SIGILL 崩溃 |
| 表格重建方式 | 坐标聚类 | EasyOCR 无原生表格识别，用 y 坐标分组行 + x 坐标排序列补偿 |
| 语言栈 | Python subprocess | 中文 OCR 的最强生态在 Python，Node.js 无可用方案 |

## 核心洞察

### 1. "没有现成的"本身就是价值

调研了四层才确认空白：
- skills.sh 市场 → 有 OCR skill，全是 Markdown 指令
- pi-package 生态（216 个仓库）→ 0 个 OCR 扩展
- GitHub 代码搜索 → "pi coding agent" + ocr = 0
- npm 包搜索 → 0

### 2. Extension 和 Skill 的本质差距

| 维度 | Skill（Markdown 指令） | Extension（注册工具） |
|------|----------------------|---------------------|
| 每次上下文消耗 | ~500 token | ~20 token |
| 参数校验 | 无，靠 LLM 自觉 | TypeBox schema 强制 |
| 出错概率 | 每次调用都有 | 几乎为零 |

所有有外部依赖的工具都应该用 extension。

### 3. CPU 兼容性 > 功能炫

PaddleOCR 的 PP-Structure 很牛，但 SIGILL 崩溃 — 要求 AVX512。EasyOCR 功能稍逊，但任何 x86 CPU 都能跑。

## 表格重建算法

1. y 坐标接近 → 同一行
2. 行内按 x 坐标排序 → 列
3. 股票代码被 OCR 合并时正则拆分
4. 输出 Markdown 表格

## 安装

```bash
pi install git:github.com/CNCSMonster/pi-local-ocr
bash ~/.pi/agent/git/github.com/CNCSMonster/pi-local-ocr/scripts/setup.sh
```

GitHub: [CNCSMonster/pi-local-ocr](https://github.com/CNCSMonster/pi-local-ocr)
