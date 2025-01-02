+++
title = '使用uv管理python包'
date = 2025-01-03T00:22:09+08:00
+++

# 使用uv


## Ref

- https://github.com/astral-sh/uv

## 使用uv运行python项目

```shell
# .. 首先进入项目根目录
# 初始化uv工程配置
uv init
# 加入所需依赖
# uv add <python包名>
# 一般项目如果提供requirements.txt的话,可以使用如下命令
uv add -r requirements.txt

# 运行
uv run <xx.py>
```

## 使用uv提供的python虚拟环境

设置好依赖并且运行成功后，会在本地生成.venv目录
根据开发环境选择激活.venv/bin目录下的对应activate文件即可。

比如在linux命令行中(使用zsh/bash时):
```shell
source ./.venv/bin/activate
```

在vscode中:https://developer.baidu.com/article/detail.html?id=3235457
你将能够找到uv生成的虚拟环境的选项

