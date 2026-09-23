#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""照片 EXIF 分析器单测。

覆盖：GPS (度,分,秒) 坐标换算主路径、Pillow 缺失时 get_exif_data 的降级返回。
"""
from __future__ import annotations

import math

from tools import photo_analyzer


def test_to_degrees_normal():
    """GPS (度,分,秒) 元组 → 十进制度。"""
    result = photo_analyzer._to_degrees((116, 23, 30))
    assert math.isclose(result, 116.3916666666, rel_tol=1e-6)
    assert photo_analyzer._to_degrees((0, 0, 0)) == 0.0


def test_to_degrees_negative_north_south_not_handled_here():
    """换算只做纯数值计算，方位（南北/东西取负）由调用方处理。"""
    assert photo_analyzer._to_degrees((30, 0, 0)) == 30.0


def test_get_exif_data_without_pillow_degrades(tmp_path):
    """降级：Pillow 不可用时返回 error 标记，不抛出 Remote PIL 异常。"""
    # 构造一个内容非法的假图片文件，验证 get_exif_data 不会崩溃
    fake = tmp_path / "a.jpg"
    fake.write_bytes(b"not a real image")
    if photo_analyzer.Image is None:
        # Pillow 未安装分支
        result = photo_analyzer.get_exif_data(str(fake))
        assert result["file"] == "a.jpg"
        assert "error" in result
    else:
        # Pillow 已安装：非图片文件应返回 error 而非抛异常
        result = photo_analyzer.get_exif_data(str(fake))
        assert result["file"] == "a.jpg"
        assert "error" in result