#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2026/09/23 22:40
# @Filename : social_parser.py
# @Author   : Alan_Hsu
"""社交媒体内容扫描器

扫描目录，把图片与文本文件分类列出，供后续读取分析（图片用 Read 工具查看）。

Usage:
    python social_parser.py --dir <screenshot_dir> --output <output_path>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
_TEXT_EXTS = {".txt", ".md", ".json", ".csv"}


def scan_directory(dir_path: str) -> dict[str, list[str]]:
    """按扩展名把目录文件分类为 images / texts / other。"""
    files: dict[str, list[str]] = {"images": [], "texts": [], "other": []}
    for p in Path(dir_path).rglob("*"):
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext in _IMAGE_EXTS:
            files["images"].append(str(p))
        elif ext in _TEXT_EXTS:
            files["texts"].append(str(p))
        else:
            files["other"].append(str(p))
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="社交媒体内容扫描器")
    parser.add_argument("--dir", required=True, help="截图/文件目录")
    parser.add_argument("--output", required=True, help="输出文件路径")
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.is_dir():
        print(f"错误：目录不存在 {args.dir}", file=sys.stderr)
        sys.exit(1)

    files = scan_directory(args.dir)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8") as f:
        f.write("# 社交媒体内容扫描结果\n\n")
        f.write(f"扫描目录：{args.dir}\n\n")
        f.write("## 文件统计\n")
        f.write(f"- 图片文件：{len(files['images'])} 个\n")
        f.write(f"- 文本文件：{len(files['texts'])} 个\n")
        f.write(f"- 其他文件：{len(files['other'])} 个\n\n")

        if files["images"]:
            f.write("## 图片列表（需用 Read 工具逐一查看）\n")
            f.writelines(f"- {img}\n" for img in sorted(files["images"]))
            f.write("\n")

        if files["texts"]:
            f.write("## 文本内容\n")
            for txt in sorted(files["texts"]):
                f.write(f"\n### {Path(txt).name}\n")
                try:
                    f.write(f"```\n{Path(txt).read_text(encoding='utf-8', errors='ignore')[:5000]}\n```\n")
                except Exception as exc:  # noqa: BLE001 - 单文件读取失败不影响整体
                    f.write(f"读取失败：{exc}\n")

    print(f"扫描完成，结果已写入 {args.output}")
    print("提示：图片截图需使用 Read 工具查看，本工具仅列出文件路径")


if __name__ == "__main__":
    main()