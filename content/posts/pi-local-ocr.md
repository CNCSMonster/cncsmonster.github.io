+++
title = "Pi 模型看不到图？用 pi-local-ocr 给它一双“读文字的眼睛”"
date = 2026-05-24T22:00:00+08:00
slug = "pi-local-ocr"
tags = ["Pi", "OCR", "AI Coding Agent", "Vision", "EasyOCR", "本地工具"]
+++

如果你在 Pi 里使用的模型不支持 vision，但又经常需要让 agent 读取截图、报错弹窗、表格截图或扫描件文字，`pi-local-ocr` 就是为这个场景准备的本地 OCR 扩展。

## 一句话定位

`pi-local-ocr` 是一个 **面向无 vision 模型的 Pi 本地图片 OCR 扩展**：它用 EasyOCR 读取图片/截图里的中英文文字，并把规整表格重建成 Markdown，让模型即使“看不到图”，也能继续理解图里的文本内容。

它的目标不是替代 vision 模型，而是解决一个更具体的问题：

```
你有一张截图 → 当前模型不支持图片 → pi-local-ocr 把图中文字转成文本/表格 → LLM 继续分析
```

## 适合谁用？

特别适合这些 Pi 用户：

- 你在 Pi 里使用的是不支持图片输入的模型。
- 你常把报错截图、终端截图、表格截图、证券/后台系统截图发给 agent。
- 你不想为了“读图上的字”切到更贵或更慢的 vision 模型。
- 你不想把包含隐私、账号、内部系统信息的截图上传到云 OCR。
- 你主要需要的是“读出图片里的文字”，而不是“理解照片里有什么”。

如果你的需求是“这张照片里有什么物体”，那需要真正的 vision 模型；如果你的需求是“这张截图上的字是什么”，这就是 `pi-local-ocr` 的场景。

## 核心特点

### 1. 完全本地，零 API 成本

OCR 在本机运行，不依赖云 API，不需要 OCR key，也不会把截图上传到第三方服务。

这对以下内容尤其重要：

- 公司内部系统截图
- 报错日志截图
- 证券/交易软件截图
- 个人隐私信息截图
- 本地开发环境截图

### 2. 专注图片/截图，而不是通用文档解析

`pi-local-ocr` 不想做全格式文档解析器。它专注这件事：

```
图片/截图 → 文字/表格 → Markdown → LLM 推理
```

如果你要解析 PDF、Office、CSV 等多格式文档，可以优先看 `pi-docparser`；如果你要用 Mistral OCR 把 PDF 转 Markdown，可以看 `mistral-ocr-pi`。`pi-local-ocr` 的优势在于：**本地图片 OCR，尤其是中文截图和表格截图。**

### 3. 对中文截图友好

支持：

```
ch
en
ch_en
```

实际测试场景包括中文证券软件截图、中文表格、中文错误信息等。对中文用户来说，这比只面向英文文档的 OCR 工具更贴近日常使用。

### 4. 表格截图可以转 Markdown 表格

它不仅返回散乱文字，还会根据 OCR 坐标做简单表格重建：

1. EasyOCR 返回文字块和坐标。
2. y 坐标接近的文字聚成同一行。
3. 行内按 x 坐标排序成列。
4. 输出 Markdown 表格。

这对规整截图特别有用：

- 股票/证券持仓截图
- Excel 表格截图
- 后台列表页截图
- 终端表格输出截图
- 数据看板里的表格区域

### 5. Extension 形式，模型调用更稳定

它不是一个 Markdown skill，而是 Pi extension，注册了真正的工具：

```
ocr_image(path, mode, lang)
```

相比让 LLM 自己拼 bash 命令，extension 的好处是：

- 参数有类型校验。
- 模型只需要传图片路径。
- 不需要每次在上下文里塞一大段操作说明。
- 出错面更小。

## 实测效果

证券软件持仓截图（6 行 × 3 列）：

```
| 7.48%  | 000651 | 格力电器 | 深A |
| 38.06% | 002245 | 蔚蓝锂芯 | 深A |
| 12.75% | 600011 | 华能国际 | 沪A |
| 9.97%  | 600406 | 国电南瑞 | 沪A |
| 16.34% | 600522 | 中天科技 | 沪A |
| 7.56%  | 600577 | 精达股份 | 沪A |
```

全部字段正确，CPU 上约 2.3 秒完成。

## 安装

```bash
# 1. 安装 Pi 扩展
pi install git:github.com/CNCSMonster/pi-local-ocr

# 2. 安装 OCR 后端（自动创建 venv，下载 EasyOCR + PyTorch，约 2GB）
bash ~/.pi/agent/git/github.com/CNCSMonster/pi-local-ocr/scripts/setup.sh

# 3. 重启 Pi
```

## 使用方式

安装后，模型会获得 `ocr_image` 工具。你只需要给它图片路径：

```
请读取 /tmp/screenshot.png 里的表格。
```

模型会调用：

```
ocr_image(path="/tmp/screenshot.png", mode="auto", lang="ch_en")
```

参数：

| 参数 | 说明 |
|---|---|
| `path` | 图片路径，支持 png/jpg/jpeg/bmp/webp/tiff |
| `mode` | `auto` / `text` / `table` |
| `lang` | `ch` / `en` / `ch_en` |

## 能做什么 / 不能做什么

| ✅ 能 | ❌ 不能 |
|---|---|
| 读取截图中的文字 | 描述照片里的物体 |
| 表格截图转 Markdown 表格 | 理解图表趋势 |
| 报错弹窗转文本 | 识别人脸/物体/颜色 |
| 终端截图转日志文本 | 处理复杂跨行跨列表格 |
| 中文/英文 OCR | 替代真正的 vision 模型 |

本质上，它是给 Pi 里的无 vision 模型补一双“只读文字的眼睛”。

## 链接

- GitHub: https://github.com/CNCSMonster/pi-local-ocr
- 完全本地运行，零 API 费用
- 支持中英文和简单表格重建
