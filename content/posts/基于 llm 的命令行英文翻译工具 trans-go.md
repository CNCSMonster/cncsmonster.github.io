+++
title = '基于 LLM 的命令行英文翻译工具 Trans-Go'
date = 2024-12-14T23:27:01+08:00
tags = ['Go', 'LLM', '翻译', '命令行工具', '开源项目']
+++

项目仓库：[cncsmonster/trans-go](https://github.com/cncsmonster/trans-go)

## 项目简介

`trans-go` 是一个基于 LLM (Large Language Model) 的命令行英文翻译工具，帮助你快速翻译英文内容，提升阅读效率。

## 安装方式

**前提条件**: 已安装 Go 编译器

```shell
git clone https://github.com/cncsmonster/trans-go
cd trans-go
./install.sh
```

## 配置方式

该工具利用 OpenAI API 风格的 LLM 服务工作，需要配置三个环境变量：

- `OPENAI_API_KEY`: 服务密钥
- `OPENAI_BASE_URL`: API 基础 URL (可选，默认使用 OpenAI 官方地址)
- `OPENAI_MODEL`: 使用的模型名称 (可选)

### 配置示例

```shell
# Bash/Zsh
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"

# 或者添加到 ~/.bashrc / ~/.zshrc
echo 'export OPENAI_API_KEY="your-api-key"' >> ~/.bashrc
```

## 使用方法

```shell
# 翻译单个单词
trans hello

# 翻译句子
trans "Hello, world!"

# 从标准输入读取
echo "Hello, world!" | trans

# 翻译文件内容
trans -f input.txt
```

## 功能特性

- ✅ 支持单词、句子、段落翻译
- ✅ 支持管道输入
- ✅ 支持文件输入
- ✅ 兼容 OpenAI API 格式的 LLM 服务
- ✅ 简洁的命令行界面

## 开发计划

- [ ] 支持更多翻译引擎
- [ ] 添加翻译历史记录
- [ ] 支持批量翻译
- [ ] 添加 TTS 语音朗读

## License

MIT License
