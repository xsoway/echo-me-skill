#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2026/09/23 22:35
# @Filename : wechat_parser.py
# @Author   : Alan_Hsu
"""微信聊天记录解析器

解析主流微信导出工具的聊天记录，提取「目标对象」的说话特征用于构建 Self Memory / Persona。

支持格式：
    - WeChatMsg 导出（txt）
    - 留痕导出（json）
    - 手动复制粘贴（纯文本）

Usage:
    python wechat_parser.py --file <path> --target <name> --output <output_path> [--format auto]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 语气词与标点统计用正则
_MSG_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.+)$")
_PARTICLE_RE = re.compile(r"[哈嗯哦噢嘿唉呜啊呀吧嘛呢吗么]")
_EMOJI_RE = re.compile(
    r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
    r"\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
    r"\U00002702-\U000027B0\U0000FE00-\U0000FE0F"
    r"\U0001F900-\U0001F9FF]+",
    re.UNICODE,
)


def detect_format(file_path: str) -> str:
    """根据扩展名与内容预判文件格式。"""
    ext = Path(file_path).suffix.lower()
    if ext == ".json":
        return "liuhen"
    if ext == ".txt":
        head = Path(file_path).read_text(encoding="utf-8", errors="ignore")[:2000]
        if _MSG_PATTERN.search(head):
            return "wechatmsg_txt"
        return "plaintext"
    return "plaintext"


def _as_messages(data) -> list[dict]:
    """从留痕 JSON 解析出消息列表（兼容数组或对象内含 messages 的两种结构）。"""
    if isinstance(data, list):
        return data
    return data.get("messages") or data.get("data") or []


def parse_wechatmsg_txt(file_path: str, target_name: str) -> dict:
    """解析 WeChatMsg 导出的 txt（时间戳+发送者+内容 多行结构）。"""
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
    return analyze_messages(messages, target_name)


def parse_liuhen_json(file_path: str, target_name: str) -> dict:
    """解析留痕导出的 JSON。"""
    data = json.loads(Path(file_path).read_text(encoding="utf-8"))
    messages = []
    for msg in _as_messages(data):
        messages.append(
            {
                "timestamp": msg.get("time") or msg.get("timestamp") or "",
                "sender": msg.get("sender") or msg.get("nickname") or msg.get("from") or "",
                "content": msg.get("content") or msg.get("message") or msg.get("text") or "",
            }
        )
    return analyze_messages(messages, target_name)


def parse_plaintext(file_path: str, target_name: str) -> dict:
    """纯文本粘贴，无法结构化解析，原样返回，标注需人工辅助。"""
    content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    return {
        "raw_text": content,
        "target_name": target_name,
        "format": "plaintext",
        "message_count": 0,
        "target_messages": 0,
        "other_messages": 0,
        "analysis": {"note": "纯文本格式，需人工辅助分析"},
        "sample_messages": [],
    }


def _count_freq(items: list[str], limit: int = 10) -> list[tuple[str, int]]:
    """统计词频并取前 N 个。"""
    freq: dict[str, int] = {}
    for item in items:
        freq[item] = freq.get(item, 0) + 1
    return sorted(freq.items(), key=lambda x: -x[1])[:limit]


def analyze_messages(messages: list[dict], target_name: str) -> dict:
    """从消息列表提取目标对象的说话特征（口头禅/emoji/长度/标点）。"""
    target_msgs = [m for m in messages if target_name in m.get("sender", "")]
    other_msgs = [m for m in messages if target_name not in m.get("sender", "")]

    all_text = " ".join(m["content"] for m in target_msgs if m.get("content"))
    top_particles = _count_freq(_PARTICLE_RE.findall(all_text))
    top_emojis = _count_freq(_EMOJI_RE.findall(all_text))

    lengths = [len(m["content"]) for m in target_msgs if m.get("content")]
    avg_length = sum(lengths) / len(lengths) if lengths else 0.0

    punct = {
        "句号": all_text.count("。"),
        "感叹号": all_text.count("！") + all_text.count("!"),
        "问号": all_text.count("？") + all_text.count("?"),
        "省略号": all_text.count("...") + all_text.count("…"),
        "波浪号": all_text.count("～") + all_text.count("~"),
    }

    return {
        "target_name": target_name,
        "total_messages": len(messages),
        "target_messages": len(target_msgs),
        "other_messages": len(other_msgs),
        "analysis": {
            "top_particles": top_particles,
            "top_emojis": top_emojis,
            "avg_message_length": round(avg_length, 1),
            "punctuation_habits": punct,
            "message_style": "short_burst" if avg_length < 20 else "long_form",
        },
        "sample_messages": [m["content"] for m in target_msgs[:50] if m.get("content")],
    }


def _write_report(out: Path, result: dict, fmt: str, source: str) -> None:
    """把分析结果写成 Markdown 报告。"""
    lines = [f"# 微信聊天记录分析 — {result.get('target_name', '')}", ""]
    lines += [f"来源文件：{source}", f"检测格式：{fmt}"]
    lines += [f"总消息数：{result.get('total_messages', 'N/A')}", ""]
    lines += [f"目标消息数：{result.get('target_messages', 'N/A')}", ""]

    analysis = result.get("analysis", {})
    if analysis.get("top_particles"):
        lines.append("## 高频语气词")
        lines += [f"- {w}: {c}次" for w, c in analysis["top_particles"]]
        lines.append("")
    if analysis.get("top_emojis"):
        lines.append("## 高频 Emoji")
        lines += [f"- {e}: {c}次" for e, c in analysis["top_emojis"]]
        lines.append("")
    if analysis.get("punctuation_habits"):
        lines.append("## 标点习惯")
        lines += [f"- {k}: {v}次" for k, v in analysis["punctuation_habits"].items()]
        lines.append("")
    lines.append("## 消息风格")
    lines.append(f"- 平均消息长度：{analysis.get('avg_message_length', 'N/A')} 字")
    style = "短句连发型" if analysis.get("message_style") == "short_burst" else "长段落型"
    lines.append(f"- 风格：{style}")
    lines.append("")
    if result.get("sample_messages"):
        lines.append("## 消息样本（前50条）")
        lines += [f"{i}. {msg}" for i, msg in enumerate(result["sample_messages"], 1)]

    out.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="微信聊天记录解析器")
    parser.add_argument("--file", required=True, help="输入文件路径")
    parser.add_argument("--target", required=True, help="目标对象的名字/昵称（如：我）")
    parser.add_argument("--output", required=True, help="输出文件路径")
    parser.add_argument(
        "--format",
        default="auto",
        choices=["auto", "wechatmsg_txt", "liuhen", "plaintext"],
        help="文件格式",
    )
    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"错误：文件不存在 {args.file}", file=sys.stderr)
        sys.exit(1)

    fmt = detect_format(args.file) if args.format == "auto" else args.format
    if args.format == "auto":
        print(f"自动检测格式：{fmt}")

    parsers = {
        "wechatmsg_txt": parse_wechatmsg_txt,
        "liuhen": parse_liuhen_json,
        "plaintext": parse_plaintext,
    }
    result = parsers.get(fmt, parse_plaintext)(args.file, args.target)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    _write_report(out, result, fmt, args.file)
    print(f"分析完成，结果已写入 {args.output}")


if __name__ == "__main__":
    main()