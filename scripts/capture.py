#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
capture.py - 实验过程真实截图

能力分级：
    L2  本机 GUI / 虚拟机窗口可控 -> 可定位窗口、置前、按窗口区域精确截取
    L1  只能截全屏                -> 用 --bbox 手动裁切
    L0  云端 / 无头环境           -> 本脚本不可用，改用「请截图清单」

用法：
    python capture.py --list                      列出当前可见窗口
    python capture.py --title Bochs --out s.png   按窗口标题截取
    python capture.py --full --out s.png          截取全屏
    python capture.py --bbox 100,200,1200,800 --out s.png   指定区域

依赖：
    pillow          必需
    pywin32         仅 Windows 下定位窗口需要（缺失时自动降级为全屏）

注意：
    1. 截图前会尝试把目标窗口置前；若失败会提示你手动点一下窗口
    2. 高缩放屏（125% / 150%）必须设置 DPI awareness，本脚本已处理
    3. 截图期间请勿移动鼠标或切换窗口，否则截到的不是目标画面
"""

import argparse
import sys
import time
from pathlib import Path

# Windows 终端默认可能是 GBK，强制 UTF-8 输出，避免中文提示变乱码
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

IS_WIN = sys.platform == "win32"


def set_dpi_awareness():
    """Windows 高缩放屏必须设置，否则截图会被缩小/偏移。"""
    if not IS_WIN:
        return False
    try:
        import ctypes

        # 2 = PROCESS_PER_MONITOR_DPI_AWARE
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return True
    except Exception:
        try:
            import ctypes

            ctypes.windll.user32.SetProcessDPIAware()
            return True
        except Exception:
            return False


def list_windows():
    """列出可见窗口，返回 [(hwnd, title), ...]"""
    if not IS_WIN:
        print("列出窗口仅支持 Windows", file=sys.stderr)
        return []
    try:
        import win32gui
    except ImportError:
        print("缺少 pywin32，无法列出窗口：pip install pywin32", file=sys.stderr)
        return []

    result = []

    def _cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title.strip():
                result.append((hwnd, title))

    win32gui.EnumWindows(_cb, None)
    return result


def find_window(title_sub):
    """按标题子串匹配窗口，返回 hwnd 或 None"""
    for hwnd, title in list_windows():
        if title_sub.lower() in title.lower():
            return hwnd
    return None


def activate_window(hwnd):
    """把窗口置前。成功返回 True。"""
    if not IS_WIN:
        return False
    try:
        import win32con
        import win32gui

        # 最小化的先还原
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.3)
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            # 系统前台锁定时会失败，用 Alt 键技巧绕过
            import win32api
            import win32com.client  # noqa: F401

            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            try:
                win32gui.SetForegroundWindow(hwnd)
            finally:
                win32api.keybd_event(
                    win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0
                )
        time.sleep(0.4)
        return win32gui.GetForegroundWindow() == hwnd
    except Exception as exc:
        print("窗口置前失败: {}".format(exc), file=sys.stderr)
        return False


def grab(bbox=None, all_screens=True):
    """截图，返回 PIL.Image"""
    from PIL import ImageGrab

    return ImageGrab.grab(bbox=bbox, all_screens=all_screens)


def window_bbox(hwnd):
    """窗口矩形 (left, top, right, bottom)"""
    import win32gui

    return win32gui.GetWindowRect(hwnd)


def parse_bbox(text):
    """解析 'x,y,w,h' 或 'l,t,r,b' 风格的字符串"""
    parts = [int(p.strip()) for p in text.replace(" ", "").split(",")]
    if len(parts) != 4:
        raise ValueError("--bbox 需要 4 个数字：left,top,right,bottom")
    return tuple(parts)


def main():
    ap = argparse.ArgumentParser(description="实验过程真实截图")
    ap.add_argument("--list", action="store_true", help="列出当前可见窗口标题")
    ap.add_argument("--title", help="按窗口标题子串定位并截取该窗口")
    ap.add_argument("--bbox", help="手动指定区域 left,top,right,bottom")
    ap.add_argument("--full", action="store_true", help="截取全屏")
    ap.add_argument("--out", help="输出 PNG 路径")
    ap.add_argument("--delay", type=float, default=1.0, help="截图前等待秒数")
    args = ap.parse_args()

    if args.list:
        wins = list_windows()
        if not wins:
            print("没有找到可见窗口")
            return 0
        for hwnd, title in wins:
            print("{:>10}  {}".format(hwnd, title))
        return 0

    if not args.out:
        print("需要 --out 指定输出路径", file=sys.stderr)
        return 1

    try:
        from PIL import ImageGrab  # noqa: F401
    except ImportError:
        print("缺少 pillow，请安装：pip install pillow", file=sys.stderr)
        return 1

    set_dpi_awareness()

    bbox = None
    if args.bbox:
        bbox = parse_bbox(args.bbox)
    elif args.title:
        hwnd = find_window(args.title)
        if hwnd is None:
            print(
                "未找到标题包含 '{}' 的窗口，可用 --list 查看".format(args.title),
                file=sys.stderr,
            )
            return 1
        if not activate_window(hwnd):
            print(
                "提示：窗口置前失败，请手动点一下 '{}' 窗口".format(args.title),
                file=sys.stderr,
            )
        bbox = window_bbox(hwnd)

    print("准备截图，{} 秒后开始...".format(args.delay))
    print("提示：请勿移动鼠标或切换窗口")
    time.sleep(args.delay)

    img = grab(bbox=bbox)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG")

    print("已保存: {}  ({}x{})".format(out, img.width, img.height))
    if bbox:
        print("区域: {}".format(bbox))
    return 0


if __name__ == "__main__":
    sys.exit(main())
