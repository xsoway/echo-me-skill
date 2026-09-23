#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2026/09/23 22:38
# @Filename : qq_parser.py
# @Author   : Alan_Hsu
"""QQ 聊天记录解析器

支持 QQ 消息管理器导出的 txt 与 mht 格式，提取目标对象的说话特征。

Usage:
    python qq_parser.py --file <path> --target <name> --output <output_path>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# QQ 消息头模式：2024-01-15 20:30:45 发送者(QQ号?) 或 2024-01-15 20:30:45 发送者
_MSG_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.+?)(?:\(\d+\))?\s*$")


def parse_qq_txt(file_path: str, target_name: str) -> dict:
    """解析 QQ 导出的 txt 聊天记录。"""
    messages: list[dict] = []
    current: dict | None = None

    for raw in Path(file_path).read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.rstrip("\n")
        m = _MSG_PATTERN.match(line)
        if m:
            if current:
                messages.append(current)
            timestamp, sender = m.groups()
            current = {"timestamp": timestamp, "sender": sender.strip(), "content": ""}
        elif current and line.strip():
            current["content"] += ("\n" if current["content"] else "") + line

    if current:
        messages.append(current)

    return _summarize(messages, target_name, "qq_txt")


def parse_qq_mht(file_path: str, target_name: str) -> dict:
    """解析 QQ 导出的 mht（HTML 内容，粗略提取可见文本）。"""
    import html as html_mod

    raw = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    # 去标签，保留可见文本
    text = re.sub(r"<[^>]+>", "\n", raw)
    text = html_mod.unescape(text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return {
        "target_name": target_name,
        "total_messages": 0,
        "target_messages": 0,
        "other_messages": 0,
        "format": "qq_mht",
        "raw_text": "\n".join(lines),
        "analysis": {"note": "mht 格式为 HTML，已提取可见文本，需人工辅助分析"},
        "sample_messages": lines[:50],
    }


def _summarize(messages: list[dict], target_name: str, fmt: str) -> dict:
    """汇总消息统计。"""
    target_msgs = [m for m in messages if target_name in m.get("sender", "")]
    lengths = [len(m["content"]) for m in target_msgs if m.get("content")]
    avg_length = sum(lengths) / len(lengths) if lengths else 0.0

    return {
        "target_name": target_name,
        "total_messages": len(messages),
        "target_messages": len(target_msgs),
        "other_messages": len(messages) - len(target_msgs),
        "format": fmt,
        "analysis": {
            "avg_message_length": round(avg_length, 1),
            "message_style": "short_burst" if avg_length < 20 else "long_form",
        },
        "sample_messages": [m["content"] for m in target_msgs[:50] if m.get("content")],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="QQ 聊天记录解析器")
    parser.add_argument("--file", required=True, help="输入文件路径")
    parser.add_argument("--target", required=True, help="目标对象的名字/昵称（如：我）")
    parser.add_argument("--output", required=True, help="输出文件路径")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"错误：文件不存在 {args.file}", file=sys.stderr)
        sys.exit(1)

    fmt = path.suffix.lower()
    if fmt == ".txt":
        result = parse_qq_txt(args.file, args.target)
    elif fmt in (".mht", ".mhtml"):
        result = parse_qq_mht(args.file, args.target)
    else:
        result = parse_qq_txt(args.file, args.target)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        f.write(f"# QQ 聊天记录分析 — {args.target}\n\n")
        f.write(f"来源文件：{args.file}\n")
        f.write(f"总消息数：{result.get('total_messages', 'N/A')}\n")
        f.write(f"目标消息数：{result.get('target_messages', 'N/A')}\n\n")
        analysis = result.get("analysis", {})
        if analysis.get("avg_message_length") is not None:
            f.write(f"平均消息长度：{analysis['avg_message_length']} 字\n")
            style = "短句连发型" if analysis.get("message_style") == "short_burst" else "长段落型"
            f.write(f"风格：{style}\n\n")
        if result.get("sample_messages"):
            f.write("## 消息样本（前50条）\n")
            for i, msg in enumerate(result["sample_messages"], 1):
                f.write(f"{i}. {msg}\n")

    print(f"分析完成，结果已写入 {args.output}")


if __name__ == "__main__":
    main()