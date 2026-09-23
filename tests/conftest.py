#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pytest 公共夹具：把仓库根加入 sys.path，使 tools 包可导入。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))