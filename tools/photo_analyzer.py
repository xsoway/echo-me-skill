#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2026/09/23 22:42
# @Filename : photo_analyzer.py
# @Author   : xsoway
"""照片元信息分析器

提取照片 EXIF 信息（拍摄时间、GPS 地点），按时间排序生成个人时间线与常去地点线索。

Usage:
    python photo_analyzer.py --dir <photo_dir> --output <output_path>
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from PIL import ExifTags, Image
except ImportError:  # Pillow 未安装
    Image = None  # type: ignore[assignment]
    ExifTags = None  # type: ignore[assignment]
    HAS_PIL = False
else:
    HAS_PIL = True

_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif"}


def _to_degrees(value: tuple) -> float:
    """把 (度, 分, 秒) GPS 元组转成十进制度。"""
    d, m, s = value
    return float(d) + float(m) / 60.0 + float(s) / 3600.0


def get_exif_data(image_path: str) -> dict[str, Any]:
    """提取单张图片的 EXIF 信息。"""
    if HAS_PIL is False or Image is None:
        return {"file": Path(image_path).name, "error": "Pillow 未安装，无法读取 EXIF"}

    try:
        with Image.open(image_path) as img:
            exif = img._getexif() or {}
            tag_map = {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}
            result: dict[str, Any] = {"file": Path(image_path).name}

            taken = tag_map.get("DateTimeOriginal") or tag_map.get("DateTime")
            if taken:
                try:
                    result["date_taken"] = datetime.strptime(str(taken), "%Y:%m:%d %H:%M:%S").isoformat()
                except ValueError:
                    result["date_taken"] = str(taken)

            gps = exif.get(34853)  # GPS IFD
            if gps and "GPSLatitude" in gps and "GPSLongitude" in gps:
                lat_ref = gps.get("GPSLatitudeRef", "N")
                lon_ref = gps.get("GPSLongitudeRef", "E")
                lat = _to_degrees(gps["GPSLatitude"])
                lon = _to_degrees(gps["GPSLongitude"])
                if lat_ref != "N":
                    lat = -lat
                if lon_ref != "E":
                    lon = -lon
                result["gps"] = {"lat": round(lat, 6), "lon": round(lon, 6)}

            return result
    except Exception as exc:  # noqa: BLE001 - 单张失败不影响整体
        return {"file": Path(image_path).name, "error": str(exc)}


def main() -> None:
    parser = argparse.ArgumentParser(description="照片元信息分析器")
    parser.add_argument("--dir", required=True, help="照片目录")
    parser.add_argument("--output", required=True, help="输出文件路径")
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.is_dir():
        print(f"错误：目录不存在 {args.dir}", file=sys.stderr)
        sys.exit(1)

    photos = [get_exif_data(str(p)) for p in sorted(root.rglob("*")) if p.is_file() and p.suffix.lower() in _IMAGE_EXTS]
    dated = sorted([p for p in photos if p.get("date_taken")], key=lambda x: x["date_taken"])
    undated = [p for p in photos if not p.get("date_taken")]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        f.write("# 照片时间线分析\n\n")
        f.write(f"照片总数：{len(photos)}，带日期：{len(dated)}，无日期：{len(undated)}\n\n")

        if dated:
            f.write("## 时间线（按拍摄时间排序）\n\n")
            for p in dated:
                line = f"- {p['date_taken']}  {p['file']}"
                if "gps" in p:
                    g = p["gps"]
                    line += f"  (所在地: {g['lat']}, {g['lon']})"
                f.write(line + "\n")

        gps_list = [p["gps"] for p in photos if "gps" in p]
        if gps_list:
            f.write("\n## GPS 地点（去重，作为常去地点线索）\n")
            seen: set[tuple] = set()
            for g in gps_list:
                key = (g["lat"], g["lon"])
                if key not in seen:
                    seen.add(key)
                    f.write(f"- ({g['lat']}, {g['lon']})\n")

        if undated:
            f.write(f"\n## 无日期照片（{len(undated)} 张）\n")
            for p in undated:
                f.write(f"- {p['file']}\n")

        if not HAS_PIL:
            f.write("\n⚠️ Pillow 未安装，仅列出文件。安装方法：pip install Pillow\n")

    print(f"分析完成，结果已写入 {args.output}")


if __name__ == "__main__":
    main()