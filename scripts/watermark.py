#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
watermark.py - 高质量档截图水印（全图斜铺）

样式：浅灰半透明文字沿对角线方向整图平铺铺满。
      内容为「姓名 + 学号」直接拼接，中间无空格（如 张三12345678）。
      不加任何角标 / 边框 / 实心底图。

用法：
    python watermark.py --input step-01.png --text "张三12345678"
    python watermark.py --input a.png --text "张三12345678" --output b.png
    python watermark.py --input a.png --text "张三12345678" --opacity 40
    python watermark.py --input a.png --text "张三12345678" --gap 1.5

默认行为：直接覆盖原图（自动留 .bak 备份）。用 --output 可另存。

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


def add_tiled(img, text, font, angle, opacity, gap_scale=1.0, color=(120, 120, 120)):
    """全图斜铺：浅灰半透明文字沿对角线铺满整张图"""
    w, h = img.size
    # 放大画布再旋转，避免旋转后四角露空
    diag = int((w * w + h * h) ** 0.5) + 4
    layer = Image.new("RGBA", (diag, diag), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    gap_x = int((tw * 0.9 + 32) * gap_scale)
    gap_y = int((th * 2.6 + 32) * gap_scale)

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


def main():
    ap = argparse.ArgumentParser(description="实验截图水印（高质量档专用，全图斜铺）")
    ap.add_argument("--input", required=True, help="输入图片")
    ap.add_argument("--text", required=True, help='水印文字，格式「姓名+学号」直接拼接，如 "张三12345678"')
    ap.add_argument("--output", help="输出路径，默认覆盖原图")
    ap.add_argument("--opacity", type=int, default=55, help="透明度 0-255，越大越明显，默认 55")
    ap.add_argument("--angle", type=int, default=-30, help="倾斜角度，默认 -30")
    ap.add_argument("--gap", type=float, default=1.0, help="平铺疏密倍率，>1 更疏，默认 1.0")
    ap.add_argument("--font-size", type=int, help="字号，默认按图宽自适应")
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
    img = add_tiled(img, args.text, font, args.angle, args.opacity, args.gap)

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
