+++
title = 'Trans-Go - 命令行英文翻译工具（已归档）'
date = 2024-12-14T23:27:01+08:00
tags = ['Go', 'LLM', '翻译', '命令行工具', '开源项目']
weight = 2
+++

> ⚠️ **注意：这个项目已归档**
>
> Trans-Go 是一个实验性项目，目前不再维护。

---

# Trans-Go

**基于 LLM 的命令行英文翻译工具。**

## 设计意图

在阅读英文文档和技术资料时，经常需要快速翻译单词或短句。

Trans-Go 提供一个简单的命令行工具，让你**在终端中直接翻译英文内容**，无需切换窗口。

## 核心方案

利用 OpenAI API 风格的 LLM 服务进行翻译：

- **支持单词、句子、段落翻译**
- **支持管道输入** - `echo "hello" | trans`
- **支持文件输入** - `trans -f input.txt`
- **兼容 OpenAI API 格式** - 可使用各种 LLM 服务

## 快速体验

```bash
# 克隆项目
git clone https://github.com/cncsmonster/trans-go
cd trans-go

# 安装
./install.sh

# 配置环境变量
export OPENAI_API_KEY="your-api-key"

# 使用
trans hello
trans "Hello, world!"
echo "Hello" | trans
```

## 项目链接

- **GitHub**: [cncsmonster/trans-go](https://github.com/cncsmonster/trans-go)

---

**这是一个实验性项目，供学习参考。**
