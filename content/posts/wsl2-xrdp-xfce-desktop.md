+++
title = "WSL2 + xrdp + XFCE 桌面方案踩坑记录"
date = 2026-06-20T00:00:00+08:00
slug = "wsl2-xrdp-xfce-desktop"
tags = ["WSL2", "xrdp", "XFCE", "远程桌面", "Linux"]
+++

WSL2 能不能当一台带桌面的 Linux 服务器用？试了 xrdp + XFCE 这条路，结论是**走不通**。

> - **WSL2 不是为完整桌面设计的** — 微软设计 WSLg 是为了运行单个 GUI 应用，不是给你一台桌面服务器
> - **xrdp 假设真实 Linux 服务器环境** — WSL2 没有真实显示硬件、VT、固定网络

下面是完整的踩坑记录。

---

## 踩坑时间线

### 插曲：xrdp 绑定地址配错了

直觉地写了 `address=127.0.0.1`，但这个版本的 xrdp 通过 `port=` 控制绑定地址，`address=` 不生效。改成 `port=tcp://.:3389` 解决。

---

### 坑 1：连接后黑屏或会话立即退出

**原因**：WSLg 设置了 `WAYLAND_DISPLAY=wayland-0`，XFCE/GTK 组件优先尝试 Wayland，但 xrdp 只提供 X11。

**解决**：在 `/etc/xrdp/startwm.sh` 中清除 Wayland 变量：

```sh
unset WAYLAND_DISPLAY
export GDK_BACKEND=x11
export QT_QPA_PLATFORM=xcb
export SDL_VIDEODRIVER=x11
```

> `/etc/xrdp/startwm.sh` 是 xrdp 安装后自带的会话启动脚本，用户通过 RDP 连接时由 xrdp 调用，相当于 xrdp 版的 `.xinitrc`。在普通 Linux 服务器上不需要修改，这里是为了清除 WSLg 注入的 Wayland 变量。

---

### 坑 2：高分屏下桌面元素太小

测试环境：2880x1800 屏幕，Windows 缩放 200%。

**尝试过的路**：

- mstsc 分辨率降到 1440x900 → 桌面缩小，周围有黑边
- `GDK_SCALE=2` 全局缩放 → XFCE 直接崩溃

**最终妥协**：

- `GDK_DPI_SCALE=1.5` 只放大字体（`GDK_SCALE` 会改变窗口大小，XFCE 承受不住）
- 面板 `icon-size` 从默认 16 改为 48
- 面板高度调到 64

---

### 坑 3：HOME 文件夹打不开

报错：`获取文件信息时出错 "/home/.../thinclient_drives"：传输端点未连接。`

**原因**：xrdp 的驱动器重定向功能在 home 目录下创建 FUSE 挂载点 `thinclient_drives`，断开连接后没有自动卸载。

**解决**：

```bash
sudo umount -l /home/<username>/thinclient_drives
sudo rm -rf /home/<username>/thinclient_drives
```

---

## 学到的东西

- WSLg 的 `WAYLAND_DISPLAY` 会污染 X11 会话，远程桌面必须手动清除
- `GDK_SCALE` 和 `GDK_DPI_SCALE` 有本质区别：前者改变窗口大小，后者只放大字体
- XFCE 面板图标大小由 `icon-size` 单独控制，和面板高度无关
- xrdp 的 `thinclient_drives` 在 WSL 下容易残留
