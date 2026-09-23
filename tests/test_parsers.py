#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""解析器单测：微信 / QQ / 社交内容扫描。

覆盖主路径（正常解析）、边界（空内容、无目标消息、内容跨行）。
"""
from __future__ import annotations

from tools import qq_parser, social_parser, wechat_parser


class TestWechatParser:
    def test_wechatmsg_txt_normal(self, tmp_path):
        """主路径：WeChatMsg txt 多行消息结构。"""
        f = tmp_path / "chat.txt"
        f.write_text(
            "2024-01-15 20:30:45 我\n今天好累啊\n\n2024-01-15 20:31:02 张三\n怎么了？\n",
            encoding="utf-8",
        )
        result = wechat_parser.parse_wechatmsg_txt(str(f), "我")
        assert result["total_messages"] == 2
        assert result["target_messages"] == 1
        assert result["target_name"] == "我"
        # 目标对象的内容被正确捕捉
        assert result["sample_messages"] == ["今天好累啊"]

    def test_wechatmsg_txt_merges_multiline_content(self, tmp_path):
        """边界：一条消息内容跨多行时正确合并。"""
        f = tmp_path / "chat.txt"
        f.write_text("2024-01-15 20:30:45 我\n第一行\n第二行\n", encoding="utf-8")
        result = wechat_parser.parse_wechatmsg_txt(str(f), "我")
        assert result["sample_messages"] == ["第一行\n第二行"]
        assert result["total_messages"] == 1

    def test_plaintext_returns_raw_with_note(self, tmp_path):
        """纯文本：无法结构化解析，返回原文并标注需人工辅助。"""
        f = tmp_path / "paste.txt"
        f.write_text("随便贴的一段话", encoding="utf-8")
        result = wechat_parser.parse_plaintext(str(f), "我")
        assert result["format"] == "plaintext"
        assert result["message_count"] == 0
        assert "人工" in result["analysis"]["note"]

    def test_detect_format_unknown_ext_falls_back_plaintext(self, tmp_path):
        """异常/边界：未知扩展名回退纯文本。"""
        f = tmp_path / "notes.log"
        f.write_text("没有时间戳的内容", encoding="utf-8")
        assert wechat_parser.detect_format(str(f)) == "plaintext"

    def test_analyze_punctuation_and_style(self):
        """语气词与标点统计、风格判断。"""
        messages = [
            {"sender": "我", "content": "嗯嗯！好的吧？"},
            {"sender": "我", "content": "哈哈，可以。"},
            {"sender": "我", "content": "好啊，短句。"},
        ]
        result = wechat_parser.analyze_messages(messages, "我")
        assert result["target_messages"] == 3
        assert result["analysis"]["message_style"] == "short_burst"
        particles = dict(result["analysis"]["top_particles"])
        assert any("嗯" in k for k in particles)
        assert result["analysis"]["punctuation_habits"]["感叹号"] >= 1


class TestQqParser:
    def test_qq_txt_normal(self, tmp_path):
        """主路径：QQ txt 结构。"""
        f = tmp_path / "qq.txt"
        f.write_text("2024-02-01 10:00:00 我\n早哦\n2024-02-01 10:00:10 同学\n早\n", encoding="utf-8")
        result = qq_parser.parse_qq_txt(str(f), "我")
        assert result["total_messages"] == 2
        assert result["sample_messages"] == ["早哦"]

    def test_qq_txt_empty_target_has_no_samples(self, tmp_path):
        """边界：目标对象无任何消息时样本为空。"""
        f = tmp_path / "qq.txt"
        f.write_text("2024-02-01 10:00:00 别人\n内容\n", encoding="utf-8")
        result = qq_parser.parse_qq_txt(str(f), "我")
        assert result["target_messages"] == 0
        assert result["sample_messages"] == []


class TestSocialParser:
    def test_scan_classifies_by_extension(self, tmp_path):
        """主路径：图片/文本/其他三类分类。"""
        (tmp_path / "shot.png").write_bytes(b"\x89PNG\r\n")
        (tmp_path / "notes.txt").write_text("hi", encoding="utf-8")
        (tmp_path / "data.bin").write_bytes(b"\x00")
        files = social_parser.scan_directory(str(tmp_path))
        assert len(files["images"]) == 1
        assert len(files["texts"]) == 1
        assert len(files["other"]) == 1

    def test_scan_empty_dir(self, tmp_path):
        """边界：空目录三类均为空。"""
        files = social_parser.scan_directory(str(tmp_path))
        assert files == {"images": [], "texts": [], "other": []}