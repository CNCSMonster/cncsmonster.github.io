+++
title = "WSL2 + xrdp + XFCE Desktop: A Post-Mortem"
date = 2026-06-20T00:00:00+08:00
slug = "wsl2-xrdp-xfce-desktop-en"
tags = ["WSL2", "xrdp", "XFCE", "Remote Desktop", "Linux"]
+++

Can WSL2 serve as a full Linux desktop machine? I tried the xrdp + XFCE route, and the answer is **it doesn't work**.

> - **WSL2 was never designed for a complete desktop** — Microsoft built WSLg to run individual GUI apps, not to give you a desktop server
> - **xrdp assumes a real Linux server** — WSL2 has no real display hardware, no VT, no stable networking

Here's the full post-mortem.

---

## The Issues

### Prelude: xrdp binding address misconfiguration

Instinctively wrote `address=127.0.0.1`, but this version of xrdp controls binding via `port=`, not `address=`. Fixed by changing to `port=tcp://.:3389`.

---

### Issue 1: Black screen or session exits immediately after connecting

**Cause**: WSLg sets `WAYLAND_DISPLAY=wayland-0`. XFCE/GTK components prefer Wayland, but xrdp only provides X11.

**Fix**: Clear Wayland variables in `/etc/xrdp/startwm.sh`:

```sh
unset WAYLAND_DISPLAY
export GDK_BACKEND=x11
export QT_QPA_PLATFORM=xcb
export SDL_VIDEODRIVER=x11
```

> `/etc/xrdp/startwm.sh` is xrdp's default session startup script — called by xrdp when a user connects via RDP. Think of it as xrdp's equivalent of `.xinitrc`. On a regular Linux server it doesn't need modification; here it's used to clear the Wayland variables injected by WSLg.

---

### Issue 2: Desktop elements too small on HiDPI displays

Test environment: 2880x1800 display, Windows scaling at 200%.

**Approaches tried**:

- Lowering mstsc resolution to 1440x900 → desktop shrinks with black borders
- `GDK_SCALE=2` global scaling → XFCE crashes outright

**Final compromise**:

- `GDK_DPI_SCALE=1.5` to scale fonts only (`GDK_SCALE` changes window geometry, which XFCE can't handle)
- Panel `icon-size` changed from default 16 to 48
- Panel height set to 64

---

### Issue 3: HOME folder won't open

Error: `获取文件信息时出错 "/home/.../thinclient_drives"：传输端点未连接。` (Error getting file info: transport endpoint not connected)

**Cause**: xrdp's drive redirection creates a FUSE mount point `thinclient_drives` under the home directory. It doesn't auto-unmount when the connection drops.

**Fix**:

```bash
sudo umount -l /home/<username>/thinclient_drives
sudo rm -rf /home/<username>/thinclient_drives
```

---

## Lessons Learned

- WSLg's `WAYLAND_DISPLAY` pollutes X11 sessions — remote desktop setups must clear it manually
- `GDK_SCALE` and `GDK_DPI_SCALE` are fundamentally different: the former changes window geometry, the latter only scales fonts
- XFCE panel icon size is controlled independently by `icon-size`, separate from panel height
- xrdp's `thinclient_drives` tends to linger under WSL
