+++
title = '使用fgm管理Go版本'
date = 2024-09-21T23:35:50+08:00
+++

想自由的搜索当前go发布的版本以及下载各种版本到本地以及自由切换，你可以尝试使用fgm

## 下载 fgm

首先配置Rust工具链，然后可以通过cargo 下载它 `cargo install fgm`

为了快速获取预编译版本,你也可以使用`cargo-binstall`: `cargo binstall fgm`

## 快速体验
然后:
1. 初始化fnm使用需要的环境变量`eval $(fgm init)`
2. (Optional) 加载fnm shell补全配置, `eval $(fgm completions --shell <shell>)`, 这里的<shell>可以是zsh、bash等等
3. 查询当前系统-架构下可获取的预编译的go版本,`fgm list-remote`
4. 下载一个版本:`fgm install 1.23.1`,(这里的1.23.1可以替换为你想下载的第三步中查询到的版本号)
5. 列举已经被下载到本地的版本:`fgm ls`
6. 启用指定版本`fgm use 1.23.1`, 如果启用的版本在本地不存在,则会尝试下载
7. 查看当前已经下载到本地的go的列表`fgm list`, 可以看到其中一项为`1.23.1 (current)`，表示版本1.23.1不仅已经被下载到本地，并且被设置为当前启用版本
8. 输入`go version`, 能够查看到输入的go版本为`1.23.1`

Note: 第一次使用`fgm list-remote`的时候fgm 会联网搜索当前最新的golang官网的可下载版本列表, 可能会比较慢, 但是执行成功一次后会把搜索到的信息记录到本地,然后之后默认会使用本地记录的版本列表. 如果需要刷新列表,可以调用`fgm update`命令,或者是使用`-u`参数

## 高级用法

1. 使用`fgm config`可以查看fgm使用的各种配置文件路径,配置项内容
2. 你可以通过修改配置文件来设置fgm下载go工具链用的地址等等
3. 值得一提,fgm遵守XDG目录规范
