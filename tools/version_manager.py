#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2026/09/23 22:52
# @Filename : version_manager.py
# @Author   : Alan_Hsu
"""版本存档与回滚管理器

对自我 Skill 做版本备份、回滚与列表查询。每次更新前自动存档，支持回滚到历史版本。

Usage:
    python version_manager.py --action <backup|rollback|list> --slug <slug> --base-dir <path> [--version <v>]
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_BASE = "./.claude/skills"
_CORE_FILES = ("self.md", "persona.md", "SKILL.md", "meta.json")


def _unique_backup_name(skill_dir: Path, version: str) -> str:
    """生成不冲突的备份目录名：{version}_{timestamp}，同秒冲突时追加序号。"""
    versions_dir = skill_dir / "versions"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{version}_{stamp}"
    candidate = base
    suffix = 1
    while (versions_dir / candidate).exists():
        suffix += 1
        candidate = f"{base}_{suffix}"
    return candidate


def _meta_version(skill_dir: Path) -> str:
    """读取当前 meta.json 的 version，缺省 v0。"""
    meta_path = skill_dir / "meta.json"
    if not meta_path.is_file():
        return "v0"
    return json.loads(meta_path.read_text(encoding="utf-8")).get("version", "v0")


def backup(base_dir: str, slug: str) -> str:
    """备份当前版本到 versions/，返回备份目录名。"""
    skill_dir = Path(base_dir) / slug
    if not (skill_dir / "meta.json").is_file():
        print("错误：meta.json 不存在", file=sys.stderr)
        sys.exit(1)

    version = _meta_version(skill_dir)
    backup_name = _unique_backup_name(skill_dir, version)
    backup_dir = skill_dir / "versions" / backup_name
    backup_dir.mkdir(parents=True, exist_ok=True)

    for fname in _CORE_FILES:
        src = skill_dir / fname
        if src.is_file():
            shutil.copy2(src, backup_dir / fname)

    print(f"已备份版本 {backup_name} 到 {backup_dir}")
    return backup_name


def _find_version_dir(skill_dir: Path, version: str) -> Path | None:
    """在 versions/ 下找到匹配版本目录（前缀匹配）。"""
    versions_dir = skill_dir / "versions"
    if not versions_dir.is_dir():
        return None
    for vname in sorted(versions_dir.iterdir()):
        if vname.name.startswith(version) or vname.name == version:
            return vname
    return None


def rollback(base_dir: str, slug: str, version: str) -> None:
    """回滚到指定版本（回滚前自动备份当前版本）。"""
    skill_dir = Path(base_dir) / slug
    target = _find_version_dir(skill_dir, version)
    if target is None or not target.is_dir():
        print(f"错误：找不到版本 {version}", file=sys.stderr)
        list_versions(base_dir, slug)
        sys.exit(1)

    backup(base_dir, slug)

    for fname in _CORE_FILES:
        src = target / fname
        dst = skill_dir / fname
        if src.is_file():
            shutil.copy2(src, dst)

    print(f"已回滚到版本 {target.name}")


def list_versions(base_dir: str, slug: str) -> None:
    """列出所有历史版本。"""
    versions_dir = Path(base_dir) / slug / "versions"
    if not versions_dir.is_dir():
        print("没有历史版本。")
        return

    versions = sorted(p.name for p in versions_dir.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not versions:
        print("没有历史版本。")
        return

    print(f"历史版本（共 {len(versions)} 个）：\n")
    for v in reversed(versions):
        print(f"  {v}")


def main() -> None:
    parser = argparse.ArgumentParser(description="版本管理器")
    parser.add_argument("--action", required=True, choices=["backup", "rollback", "list"])
    parser.add_argument("--slug", required=True, help="自我代号")
    parser.add_argument("--base-dir", default=DEFAULT_BASE, help=f"基础目录（默认：{DEFAULT_BASE}）")
    parser.add_argument("--version", help="回滚目标版本")
    args = parser.parse_args()

    if args.action == "backup":
        backup(args.base_dir, args.slug)
    elif args.action == "rollback":
        if not args.version:
            print("错误：rollback 需要 --version 参数", file=sys.stderr)
            sys.exit(1)
        rollback(args.base_dir, args.slug, args.version)
    elif args.action == "list":
        list_versions(args.base_dir, args.slug)


if __name__ == "__main__":
    main()