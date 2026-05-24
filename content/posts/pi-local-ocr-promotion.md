+++
title = "你的 AI 编程助手看不到图？这个扩展让它能读文字"
date = 2026-05-24
[taxonomies]
tags = ["AI Code CLI", "扩展", "OCR"]
+++


> 如果你的 Pi 模型不支持 vision，试试 `pi-local-ocr` — 两条命令，让模型能读取图片中的文字和表格。完全本地运行，零 API 费用。

## 一句话

把截图中的文字/表格转成 Markdown，让无 vision 模型的 agent 能继续分析。不替代 vision 模型，只做一件事：**读出图上的字**。

## 能做什么

| ✅ | ❌ |
|----|----|
| 截图文字提取（中文 + 英文） | 描述照片里有什么物体 |
| 表格截图 → Markdown 表格 | 理解图表趋势 |
| 报错弹窗 → 文本 | 复杂跨行跨列表格 |

## 安装

```bash
pi install git:github.com/CNCSMonster/pi-local-ocr
bash ~/.pi/agent/git/github.com/CNCSMonster/pi-local-ocr/scripts/setup.sh
```

## 使用

安装后把图片路径丢给 agent：

```text
请读取 /tmp/screenshot.png 里的表格
```

模型会自动调用 `ocr_image(path, mode, lang)`，支持 `auto` / `text` / `table` 三种模式。

## 实测

证券持仓截图（6 行 × 3 列），2.3 秒 CPU 跑完，全部字段正确。

## 为什么是本地

**方便，零配置。** 不用找 OCR API、不用注册、不用管 key —— 装上就能用。

如果你搭配本地模型使用，还能做到完全隐私：截图里的内部系统、报错日志、账户信息全程不出本机。

GitHub: [CNCSMonster/pi-local-ocr](https://github.com/CNCSMonster/pi-local-ocr)
