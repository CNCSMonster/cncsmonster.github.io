+++
title = "Why SSH to LAN Hosts Fails Inside WSL — And How to Fix It"
date = 2025-04-22T11:06:46+08:00
tags = ["WSL", "SSH", "Linux", "Networking"]
+++

## Reference

- https://cn.linux-console.net/?p=9494#google_vignette
- https://www.cnblogs.com/guobaiwang/articles/12610439.html

## The Problem

SSH connections to hosts on the local network fail when initiated from inside WSL2.

## The Investigation

### Try 1

Discovered that WSL2 and the Windows host are not on the same LAN — even when connected to the same Wi-Fi. WSL2 uses its own isolated internal network address, different from the Windows host's LAN address.

Research revealed that WSL2 has a separate network namespace from the host. To reach other hosts on the LAN from within WSL2, the WSL2 environment needs to share the same subnet as the Windows host.

The solution: enable mirrored network mode.

- [cnblogs — WSL2 Mirrored Network Mode Configuration](https://www.cnblogs.com/netWild/p/18503950) (solution source — note: the `localhostForwarding=true` setting in that article is actually ineffective when mirrored mode is active)
- [Microsoft Learn — WSL Networking](https://learn.microsoft.com/en-us/windows/wsl/networking) (official docs for verification)
