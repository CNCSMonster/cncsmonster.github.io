+++
title = '使用mise替换fgm'
date = 2024-12-13T21:15:54+08:00
+++

mise能够完全覆盖fgm的功能和使用场景，而且不仅仅能够用来管理Golang工具链，还能够用来管理其他语言的工具链，比如nodejs、neovim、java等等。
甚至我们还能够用mise来替换direnv，实现管理进入退出目录时的环境变量加载和卸载。

下面将从三方面带你感受笔者使用mise的体验:

## 一. 下载 mise

方式1: 通过包安装管理器安装mise

```sh
# 需要先安装cargo-binstall和rust工具链
cargo binstall mise
```

方式2: 从仓库预编译版本下载资源列表中下载, 解压缩后把mise可执行文件放到可执行文件目录即可
[release链接](https://github.com/jdx/mise/releases)

## 二. 使用mise管理go版本

### 0. 初始化mise

在自己的shell配置文件中加入如下命令，其中`$SH`替换成自己的shell的名称，比如`bash`、`zsh`等等

```sh
# 初始化mise
mise activate $SH
```

### 1. 管理局部目录中的go版本

```sh
# 切换go工具链到指定版本
mise use go@1.23.1
```

第一次在某个目录使用mise时，mise会报错，提示需要先信任当前目录采用的mise配置，此时可以通过`mise trust`命令来信任当前目录的mise配置。
之后，再次使用`mise use go@1.23.1`命令，mise会自动下载并安装go1.23.1版本，并且将当前目录的go工具链切换到go1.23.1版本。同时，mise会自动在当前目录创建一个mise.toml文件，用来记录当前目录的mise配置信息。

如果当前目录或者父目录中已经存在被信任的mise配置文件mise.toml，那么mise会使用该配置文件工作，使用`mise use go@1.23.1`之类的命令时，mise会把新配置更新到该配置文件中。

mise使用全局配置文件，一般在`$XDG_CONFIG_HOME/mise/config.toml`中，可以通过`mise config`命令查看和修改全局配置文件。
使用`mise`时，可以通过`-g`选项来指定是否使用全局配置文件，此外，如果在本目录以及父目录中找不到mise配置文件，mise也会自动使用全局配置文件。

## 三. 使用mise管理进出目录时的环境变量加载和卸载

```sh
# 使用mise设置环境变量RUSTUP_BACKTRACE=1
mise env set RUSTUP_BACKTRACE=1
```
该命令执行成功后，每次进入该目录时，mise会自动加载RUSTUP_BACKTRACE=1环境变量，退出该目录时，mise会自动卸载RUSTUP_BACKTRACE=1环境变量，使用该环境变量原本的值(如果原本该环境变量已经存在)或者删除该环境变量。

需要注意的是，使用该命令时，mise会先进行配置文件检查，如果是初次使用的区域，同样需要先执行`mise trust`命令。