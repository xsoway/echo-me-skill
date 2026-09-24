#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the echo-me-skill package contract.

独立可执行的结构、安全与链接校验。运行：
    python3 scripts/validate_skill_package.py <skill-dir>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = (
    "## 何时使用",
    "## 输出格式选项",
    "## 如何使用",
    "## 参考文件",
    "## 常见误区",
    "## 最佳实践",
)
REQUIRED_CASES = ("basic-success.yaml", "edge-incomplete-input.yaml", "edge-scope-boundary.yaml")
SECRET = re.compile(r"(?i)(sk-[a-z0-9_-]{12,}|authorization:|api[_ -]?key\s*[:=]|bearer\s+[a-z0-9._-]{12,})")
ABSOLUTE_PATH = re.compile(r"/(?:Users|home|private|etc|var|opt)/[^\s`]+")


def fail(messages: list[str]) -> int:
    for message in messages:
        print(f"FAIL: {message}", file=sys.stderr)
    return 1


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) == 2 else ".").resolve()
    name = root.name

    required = [
        root / "SKILL.md",
        root / "prompts" / f"{name}.md",
        root / "agents/openai.yaml",
        root / "evals/eval.yaml",
        root / "scripts/validate_skill_package.py",
    ]
    required.extend(root / "evals/cases" / case for case in REQUIRED_CASES)

    problems = [f"missing {p.relative_to(root)}" for p in required if not p.is_file()]
    if problems:
        return fail(problems)

    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    metadata = (root / "agents/openai.yaml").read_text(encoding="utf-8")

    if f"name: {name}" not in skill:
        problems.append("SKILL.md frontmatter name must match directory")
    if f'key: "{name}"' not in metadata:
        problems.append("agents metadata.key must match directory")
    problems.extend(f"SKILL.md missing heading {h}" for h in REQUIRED_HEADINGS if h not in skill)

    # 扫描全部文本文件（.md/.yaml/.yml/.py/.html/.toml/.json/.txt 等），
    # 二进制文件（如图片，.gitattributes 已标记）跳过 —— 避免漏扫 Python/HTML 等源码。
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # 二进制文件，跳过
        if SECRET.search(text):
            problems.append(f"credential-like content in {path.relative_to(root)}")
        if ABSOLUTE_PATH.search(text):
            problems.append(f"absolute local path in {path.relative_to(root)}")

    if problems:
        return fail(problems)
    print(f"PASS: {name} package contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())