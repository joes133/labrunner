#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
watermark.py - 高质量档截图水印（B1 样式）

样式：整图斜铺半透明「学号 姓名」+ 右下角实心角标

用法：
    python watermark.py --input step-01.png --text "2023123456 焦馨"
    python watermark.py --input a.png --text "..." --output b.png
    python watermark.py --input a.png --text "..." --no-tile    只加角标
    python watermark.py --input a.png --text "..." --opacity 40  调整浓度

默认行为：直接覆盖原图（加 .wm 备份）。用 --output 可另存。

依赖：pillow
"""

import argparse
import shutil
import sys
from pathlib import Path

# Windows 终端默认可能是 GBK，强制 UTF-8 输出，避免中文提示变乱码
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from PIL import Image, ImageDraw, ImageFont

# 中文字体候选（按优先级）
FONT_CANDIDATES = [
    # Windows
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
    # macOS
    "/System/Library/Fonts/PingFang.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def find_font():
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return path
    return None


def load_font(size):
    path = find_font()
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def add_tiled(img, text, font, angle, opacity, color=(90, 90, 90)):
    """整图斜铺半透明文字"""
    w, h = img.size
    # 放大画布再旋转，避免旋转后四角露空
    diag = int((w * w + h * h) ** 0.5) + 4
    layer = Image.new("RGBA", (diag, diag), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    dummy = ImageDraw.Draw(layer)
    bbox = dummy.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    gap_x = int(tw * 0.8) + 40
    gap_y = int(th * 2.5) + 40

    fill = color + (opacity,)
    y = 0
    while y < diag:
        x = 0
        while x < diag:
            d.text((x, y), text, font=font, fill=fill)
            x += tw + gap_x
        y += th + gap_y

    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)

    left = (diag - w) // 2
    top = (diag - h) // 2
    layer = layer.crop((left, top, left + w, top + h))

    base = img.convert("RGBA")
    out = Image.alpha_composite(base, layer)
    return out.convert("RGB")


def add_corner(img, text, font, margin=16):
    """右下角实心角标"""
    d = ImageDraw.Draw(img)
    w, h = img.size

    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    pad = 8
    box_w = tw + pad * 2
    box_h = th + pad * 2
    x0 = w - box_w - margin
    y0 = h - box_h - margin

    d.rectangle([x0, y0, x0 + box_w, y0 + box_h], fill=(25, 25, 25, 235))
    d.text((x0 + pad - bbox[0], y0 + pad - bbox[1]), text, font=font, fill=(255, 255, 255))
    return img


def main():
    ap = argparse.ArgumentParser(description="实验截图水印（高质量档专用）")
    ap.add_argument("--input", required=True, help="输入图片")
    ap.add_argument("--text", required=True, help="水印文字，通常是「学号 姓名」")
    ap.add_argument("--output", help="输出路径，默认覆盖原图")
    ap.add_argument("--opacity", type=int, default=55, help="斜铺透明度 0-255，默认 55")
    ap.add_argument("--angle", type=int, default=-30, help="斜铺角度，默认 -30")
    ap.add_argument("--font-size", type=int, help="字号，默认按图宽自适应")
    ap.add_argument("--no-tile", action="store_true", help="不加斜铺，只要角标")
    ap.add_argument("--no-corner", action="store_true", help="不加角标，只要斜铺")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.exists():
        print("文件不存在: {}".format(src), file=sys.stderr)
        return 1

    try:
        img = Image.open(src)
        img.load()
    except Exception as exc:
        print("打开图片失败: {}".format(exc), file=sys.stderr)
        return 1

    size = args.font_size or max(16, img.width // 42)
    font = load_font(size)
    if find_font() is None:
        print("警告: 未找到中文字体，中文可能显示为方块", file=sys.stderr)

    img = img.convert("RGB")

    if not args.no_tile:
        img = add_tiled(img, args.text, font, args.angle, args.opacity)

    if not args.no_corner:
        img = add_corner(img, args.text, font)

    if args.output:
        dst = Path(args.output)
    else:
        # 覆盖原图前留个备份，防止用户后悔
        backup = src.with_suffix(src.suffix + ".bak")
        shutil.copy2(src, backup)
        dst = src
        print("原图已备份: {}".format(backup))

    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, "PNG")
    print("已加水印: {}  ({}x{})".format(dst, img.width, img.height))
    return 0


if __name__ == "__main__":
    sys.exit(main())
