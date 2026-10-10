#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detect_encoding.py - 探测文件编码并安全读取

用途：读取用户提供的未知编码文档（txt / md / csv / 代码）时，
      先探测再解码，避免硬猜导致乱码。

用法：
    python detect_encoding.py <path>              # 只报告编码
    python detect_encoding.py <path> --read       # 探测并打印内容
    python detect_encoding.py <path> --json       # 输出 JSON 结果
    python detect_encoding.py <path> --write-out <dst>   # 转成 UTF-8 另存

探测顺序：BOM -> chardet(若可用) -> UTF-8 严格校验 -> GBK 回退
"""

import argparse
import json
import sys
from pathlib import Path

# Windows 终端默认可能是 GBK，强制 UTF-8 输出，避免中文提示变乱码
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# BOM 表：命中即确定编码，优先级最高
BOMS = [
    (b"\xef\xbb\xbf", "utf-8-sig"),
    (b"\xff\xfe\x00\x00", "utf-32-le"),
    (b"\x00\x00\xfe\xff", "utf-32-be"),
    (b"\xff\xfe", "utf-16-le"),
    (b"\xfe\xff", "utf-16-be"),
]

# 中文环境的常见回退编码，按可能性排序
FALLBACKS = ["utf-8", "gbk", "gb18030", "big5", "latin-1"]


def detect(path):
    """返回 (encoding, confidence, method)"""
    raw = Path(path).read_bytes()

    if not raw:
        return "utf-8", 1.0, "empty"

    # 1. BOM
    for bom, enc in BOMS:
        if raw.startswith(bom):
            return enc, 1.0, "bom"

    # 2. chardet（若安装）
    try:
        import chardet

        result = chardet.detect(raw)
        if result and result.get("encoding"):
            enc = result["encoding"]
            conf = result.get("confidence") or 0.0
            if conf >= 0.6:
                return enc, round(conf, 3), "chardet"
    except ImportError:
        pass

    # 3. 逐个尝试解码，第一个成功的就是它
    for enc in FALLBACKS:
        try:
            raw.decode(enc)
            # 严格模式下能解开，基本可以确定
            return enc, 0.8, "try-decode"
        except (UnicodeDecodeError, LookupError):
            continue

    return "utf-8", 0.0, "fallback-default"


def safe_read(path):
    """安全读取，返回 (text, encoding, confidence, method)"""
    enc, conf, method = detect(path)
    raw = Path(path).read_bytes()
    try:
        text = raw.decode(enc)
    except UnicodeDecodeError:
        # 兜底：有问题的字节替换掉，总比崩溃好
        text = raw.decode(enc, errors="replace")
        conf = min(conf, 0.3)
    return text, enc, conf, method


def main():
    ap = argparse.ArgumentParser(
        description="探测文件编码并安全读取（防乱码第一步）"
    )
    ap.add_argument("path", help="目标文件路径")
    ap.add_argument("--read", action="store_true", help="探测后打印文件内容")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    ap.add_argument("--write-out", metavar="DST", help="将内容转为 UTF-8 另存")
    args = ap.parse_args()

    src = Path(args.path)
    if not src.exists():
        print("文件不存在: {}".format(src), file=sys.stderr)
        return 1

    text, enc, conf, method = safe_read(src)

    if args.json:
        print(
            json.dumps(
                {
                    "path": str(src),
                    "encoding": enc,
                    "confidence": conf,
                    "method": method,
                    "chars": len(text),
                    "has_replacement_char": "\ufffd" in text,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print("文件: {}".format(src))
    print("编码: {}  (置信度 {}, 方法 {})".format(enc, conf, method))
    print("字符数: {}".format(len(text)))
    if "\ufffd" in text:
        print("警告: 检测到 U+FFFD 替换字符，解码可能已损坏", file=sys.stderr)

    if args.write_out:
        dst = Path(args.write_out)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        print("已转存为 UTF-8: {}".format(dst))

    if args.read:
        print("-" * 40)
        print(text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
