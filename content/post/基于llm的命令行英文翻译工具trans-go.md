+++
title = '基于llm的命令行英文翻译工具trans-go'
date = 2024-12-14T23:27:01+08:00
+++

# 基于llm的命令行英文翻译工具trans-go

仓库地址: https://github.com/cncsmonster/trans-go

## 安装方式

前提条件: 安装了go编译器

```shell
git clone https://github/cncsmonster/trans-go
./install.sh
```

## 配置方式

该工具利用openai api风格的llm服务工作，需要配置三个环境变量:
- OPENAI_API_KEY: 服务密钥
- OPENAI_API_BASE_URL: 服务地址
- MODEL: 使用的模型名称

笔者测试了国内的若干中文模型的服务，综合性价比和效果等因素发现使用deepseek家的服务已经比较实用了，可以使用如下配置:

```toml
OPENAI_API_KEY="你的deepseek家的api key"
OPENAI_API_BASE_URL="https://api.deepseek.com/v1/"
MODEL="deepseek-chat"
```

也可以使用本机部署的ollama提供的openai兼容接口，开源模型的话`qwen2.5:14b`已经能够基本满足需要

## 使用方式

基础用法: 读取第一个命令行参数以外的参数, 作为要翻译的英文文本，逐个翻译
```shell
# 如下命令会依次翻译hello world 和 good morning
trans "hello world" "good morning"
```

翻译多行文件: 可以直接输入`trans`，然后粘贴文本，按`ctrl+d`然后按下enter键输入`EOF`来结束输入

> 直接使用`trans`会读取标准输入直到遇到EOF，然后翻译标准输入中的内容

翻译文件: `cat $FILE | trans`，$FILE替换成要翻译的文件路径


翻译help文档: 直接使用`trans`会翻译标准输入中的内容，可以结合管道用于翻译cli工具的help文档为英文，可以使用如下命令
```shell
go help | trans
```


