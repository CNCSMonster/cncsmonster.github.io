+++
title = 'WSL 中 SSH 连接局域网主机失败'
date = 2025-04-22T11:06:46+08:00
tags = ['WSL', 'SSH', 'Linux', '网络']
+++

## 参考资源

- [Linux 控制台 - WSL2 网络配置](https://cn.linux-console.net/?p=9494#google_vignette)
- [博客园 - WSL2 网络问题](https://www.cnblogs.com/guobaiwang/articles/12610439.html)

## 问题描述

在 WSL2 中使用 SSH 连接局域网中的主机时，提示连接失败

## 尝试解决

### Try 1

这次尝试，发现是不在同一个局域网中，即使连接的是同一个 WIFI。
然后发现是 WSL2 中的局域网地址和 Windows 中直接的局域网地址不一样。
查资料发现是 WSL2 中使用的是 Windows 内部的一个独立的地址。
于是为了能够在 WSL2 中连接同一个局域网中的其他主机，需要让 WSL2 环境中的局域网地址和外部一样。
最终通过配置镜像网络模式解决。

- [博客园 - WSL2 镜像网络模式配置](https://www.cnblogs.com/netWild/p/18503950)（解决方案来源，需要注意的是它的方案中 localhostForwarding=true 这条属性实际上在镜像网络模式启动的时候是无效的）
- [Microsoft Learn - WSL 网络配置](https://learn.microsoft.com/zh-cn/windows/wsl/networking)（官方文档，可以验证上面的博客）
