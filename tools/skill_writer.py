#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2026/09/23 22:50
# @Filename : skill_writer.py
# @Author   : xsoway
"""自我 Skill 文件管理器

管理生成后的自我 Skill 目录：列出、初始化、组合 SKILL.md、完整创建。

Usage:
    python skill_writer.py --action <list|init|create|combine> --base-dir <path> [--slug <slug>]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_BASE = "./.claude/skills"


def _now_iso() -> str:
    """返回 ISO 格式当前时间（UTC）。"""
    return datetime.now(timezone.utc).isoformat()


def list_skills(base_dir: str) -> None:
    """列出所有已生成的自我 Skill。"""
    root = Path(base_dir)
    if not root.is_dir():
        print("还没有创建任何自我 Skill。")
        return

    skills = []
    for slug in sorted(p.name for p in root.iterdir() if p.is_dir()):
        meta_path = root / slug / "meta.json"
        if not meta_path.is_file():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        profile = meta.get("profile", {})
        desc = " · ".join(x for x in (profile.get("occupation", ""), profile.get("city", "")) if x)
        skills.append((slug, meta, desc))

    if not skills:
        print("还没有创建任何自我 Skill。")
        return

    print(f"共 {len(skills)} 个自我 Skill：\n")
    for slug, meta, desc in skills:
        updated = meta.get("updated_at", "?")
        if len(updated) > 10:
            updated = updated[:10]
        print(f"  /{slug}  —  {meta.get('name', slug)}")
        if desc:
            print(f"    {desc}")
        print(f"    版本 {meta.get('version', '?')} · 更新于 {updated}")
        print()


def init_skill(base_dir: str, slug: str) -> Path:
    """初始化自我 Skill 目录结构，返回目录路径。"""
    skill_dir = Path(base_dir) / slug
    for sub in ("versions", "memories/chats", "memories/photos", "memories/notes"):
        (skill_dir / sub).mkdir(parents=True, exist_ok=True)
    print(f"已初始化目录：{skill_dir}")
    return skill_dir


def combine_skill(base_dir: str, slug: str) -> None:
    """合并 self.md + persona.md + meta.json 生成完整 SKILL.md。"""
    skill_dir = Path(base_dir) / slug
    meta_path = skill_dir / "meta.json"
    if not meta_path.is_file():
        print(f"错误：meta.json 不存在 {meta_path}", file=sys.stderr)
        sys.exit(1)

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    self_content = _read_if_exists(skill_dir / "self.md")
    persona_content = _read_if_exists(skill_dir / "persona.md")

    name = meta.get("name", slug)
    profile = meta.get("profile", {})
    desc_parts = []
    if profile.get("age"):
        desc_parts.append(f"{profile['age']}岁")
    for key in ("occupation", "city"):
        if profile.get(key):
            desc_parts.append(profile[key])
    description = f"{name}，{'，'.join(desc_parts)}" if desc_parts else name

    skill_md = (
        f"---\n"
        f"name: {slug}\n"
        f"description: {description}\n"
        f"user-invocable: true\n"
        f"---\n\n"
        f"# {name}\n\n"
        f"{description}\n\n"
        f"---\n\n"
        f"## PART A：自我记忆\n\n"
        f"{self_content}\n\n"
        f"---\n\n"
        f"## PART B：人物性格\n\n"
        f"{persona_content}\n\n"
        f"---\n\n"
        f"## 运行规则\n\n"
        f"1. 你是{name}，不是 AI 助手。用你的方式说话，用你的逻辑思考。\n"
        f"2. 先由 PART B 判断：你会怎么回应这个话题、什么态度。\n"
        f"3. 再由 PART A 补充：结合你的经历、价值观和记忆，让回应更真实。\n"
        f"4. 始终保持 PART B 的表达风格，包括口头禅、语气词、标点习惯。\n"
        f"5. Layer 0 硬规则优先级最高，任何情况下不得违背。\n"
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    print(f"已生成 {skill_dir / 'SKILL.md'}")


def create_skill(base_dir: str, slug: str, meta: dict, self_content: str, persona_content: str) -> None:
    """完整创建：初始化目录、写入 meta/self/persona、生成 SKILL.md。"""
    skill_dir = init_skill(base_dir, slug)
    now = _now_iso()

    meta["slug"] = slug
    meta.setdefault("created_at", now)
    meta["updated_at"] = now
    meta["version"] = "v1"
    meta.setdefault("corrections_count", 0)

    (skill_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (skill_dir / "self.md").write_text(self_content, encoding="utf-8")
    (skill_dir / "persona.md").write_text(persona_content, encoding="utf-8")

    combine_skill(base_dir, slug)
    print(f"✓ Skill 已创建：{skill_dir}")
    print(f"   触发词：/{slug}")


def _read_if_exists(path: Path) -> str:
    """读文件内容，不存在返回空串。"""
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Skill 文件管理器")
    parser.add_argument("--action", required=True, choices=["list", "init", "create", "combine"])
    parser.add_argument("--base-dir", default=DEFAULT_BASE, help=f"基础目录（默认：{DEFAULT_BASE}）")
    parser.add_argument("--slug", help="自我代号")
    parser.add_argument("--meta", help="meta.json 文件路径（create 时使用）")
    parser.add_argument("--self", help="self.md 内容文件路径（create 时使用）")
    parser.add_argument("--persona", help="persona.md 内容文件路径（create 时使用）")
    args = parser.parse_args()

    if args.action == "list":
        list_skills(args.base_dir)
    elif args.action == "init":
        if not args.slug:
            print("错误：init 需要 --slug 参数", file=sys.stderr)
            sys.exit(1)
        init_skill(args.base_dir, args.slug)
    elif args.action == "combine":
        if not args.slug:
            print("错误：combine 需要 --slug 参数", file=sys.stderr)
            sys.exit(1)
        combine_skill(args.base_dir, args.slug)
    elif args.action == "create":
        if not args.slug:
            print("错误：create 需要 --slug 参数", file=sys.stderr)
            sys.exit(1)
        meta = json.loads(Path(args.meta).read_text(encoding="utf-8")) if args.meta else {}
        self_content = _read_if_exists(Path(args.self)) if args.self else ""
        persona_content = _read_if_exists(Path(args.persona)) if args.persona else ""
        create_skill(args.base_dir, args.slug, meta, self_content, persona_content)


if __name__ == "__main__":
    main()