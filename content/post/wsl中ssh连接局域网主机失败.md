+++
title = 'Wsl 中 ssh 连接局域网主机失败'
date = 2025-04-22T11:06:46+08:00
+++

# wsl 中通过 ssh 连接局域网中其他主机失败解决方案

## 参考资料

- [https://cn.linux-console.net/?p=9494#google_vignette](https://cn.linux-console.net/?p=9494#google_vignette)
- [https://www.cnblogs.com/guobaiwang/articles/12610439.html](https://www.cnblogs.com/guobaiwang/articles/12610439.html)

## 问题描述

在 wsl2 中使用 ssh 连接局域网中的主机时,提示连接失败

## 尝试解决

### try 1

这次尝试,发现是不在同一个局域网中,即使连接的是同一个 WIFI,
然后发现是 wsl2 中的局域网地址和 windows 中直接的局域网地址不一样
查资料发现是 wsl2 中使用的是 windows 内部的一个独立的地址
于是为了能够在 wsl2 中连接同一个局域网中的其他主机，需要让 wsl2 环境中的局域网地址和外部一样
最终通过配置镜像网络模式解决

- [https://www.cnblogs.com/netWild/p/18503950](https://www.cnblogs.com/netWild/p/18503950) (解决方案来源，需要注意的是它的方案中 localhostForwarding=true 这条属性实际上在 镜像网络模式启动 的时候 是无效的 )
- [https://learn.microsoft.com/zh-cn/windows/wsl/networking](https://learn.microsoft.com/zh-cn/windows/wsl/networking) (官方文档,可以验证上面的博客)
