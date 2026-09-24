#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""manager 单测：skill_writer 与 version_manager。

覆盖主路径（create/combine、backup/rollback/list）、边界（不存在版本）。
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import skill_writer, version_manager


def _make_skill(base_dir: Path, slug: str = "demo") -> Path:
    """辅助：创建一个完整 Skill，返回其目录。"""
    meta = {"name": "演示者", "profile": {"age": 30, "occupation": "工程师", "city": "杭州"}}
    skill_writer.create_skill(str(base_dir), slug, meta, "自我记忆内容", "人物性格内容")
    return base_dir / slug


class TestSkillWriter:
    def test_create_initializes_files(self, tmp_path):
        """主路径：create 生成 meta/self/persona/SKILL.md。"""
        skill_dir = _make_skill(tmp_path)
        for fname in ("meta.json", "self.md", "persona.md", "SKILL.md"):
            assert (skill_dir / fname).is_file(), f"missing {fname}"
        for sub in ("versions", "memories/chats", "memories/photos", "memories/notes"):
            assert (skill_dir / sub).is_dir(), f"missing {sub}"

    def test_combine_generates_skill_md_with_parts(self, tmp_path):
        """主路径：SKILL.md 内容含 A/B 两部分与 frontmatter。"""
        _make_skill(tmp_path)
        content = (tmp_path / "demo" / "SKILL.md").read_text(encoding="utf-8")
        assert "name: demo" in content
        assert "PART A：自我记忆" in content
        assert "PART B：人物性格" in content
        assert "自我记忆内容" in content

    def test_create_sets_metadata_fields(self, tmp_path):
        """主路径：meta.json 含 slug/version/timestamps。"""
        skill_dir = _make_skill(tmp_path)
        meta = json.loads((skill_dir / "meta.json").read_text(encoding="utf-8"))
        assert meta["slug"] == "demo"
        assert meta["version"] == "v1"
        assert meta.get("created_at") and meta.get("updated_at")

    def test_list_empty_base(self, tmp_path, capsys):
        """边界：空基础目录提示未创建。"""
        skill_writer.list_skills(str(tmp_path))
        out = capsys.readouterr().out
        assert "还没有创建" in out


class TestVersionManager:
    def test_backup_creates_version_dir(self, tmp_path):
        """主路径：backup 生成 versions/{v}_{timestamp}/ 并复制核心文件。"""
        skill_dir = _make_skill(tmp_path)
        version_manager.backup(str(tmp_path), "demo")
        entries = list((skill_dir / "versions").iterdir())
        assert len(entries) == 1
        backup_dir = entries[0]
        for fname in ("self.md", "persona.md", "SKILL.md", "meta.json"):
            assert (backup_dir / fname).is_file(), f"missing {fname}"

    def test_rollback_restores_files_and_backs_up_first(self, tmp_path):
        """主路径：rollback 先备份当前状态再恢复目标版本。"""
        skill_dir = _make_skill(tmp_path)
        version_manager.backup(str(tmp_path), "demo")
        entries = sorted(p.name for p in (skill_dir / "versions").iterdir())
        # 修改当前 self.md，再回滚
        (skill_dir / "self.md").write_text("修改后内容", encoding="utf-8")
        version_manager.rollback(str(tmp_path), "demo", entries[0])
        # 恢复了原始内容
        assert (skill_dir / "self.md").read_text(encoding="utf-8") == "自我记忆内容"
        # rollback 前又做了一次备份
        assert len(list((skill_dir / "versions").iterdir())) == 2

    def test_rollback_unknown_version_lists_and_exits(self, tmp_path):
        """异常：回滚到不存在版本打印错误并退出非零。"""
        _make_skill(tmp_path)
        with pytest.raises(SystemExit) as exc:
            version_manager.rollback(str(tmp_path), "demo", "v999")
        assert exc.value.code == 1

    def test_rollback_exact_version_prefix_not_ambiguous(self, tmp_path):
        """回归：回滚到 v1 不得误选中 v10_... 备份（前缀精确匹配）。

        备份目录名为 {version}_{timestamp}；v10_... 在字典序上排在 v1_... 之前，
        若用 startswith("v1") 匹配会误恢复 v10 快照。必须按 "_" 前的版本段精确匹配。
        """
        skill_dir = _make_skill(tmp_path)
        versions = skill_dir / "versions"
        versions.mkdir(exist_ok=True)
        # 构造 v1 与 v10 两个快照，v10 用更早时间戳以排在 v1 之前（字典序）
        (versions / "v10_19990101_000000").mkdir()
        (versions / "v10_19990101_000000" / "self.md").write_text("V10 内容", encoding="utf-8")
        (versions / "v1_20260102_000000").mkdir()
        (versions / "v1_20260102_000000" / "self.md").write_text("V1 内容", encoding="utf-8")
        # 修改当前 self.md，再回滚到 v1
        (skill_dir / "self.md").write_text("当前内容", encoding="utf-8")
        version_manager.rollback(str(tmp_path), "demo", "v1")
        # 应恢复 v1 快照而非 v10
        assert (skill_dir / "self.md").read_text(encoding="utf-8") == "V1 内容"

    def test_list_versions_no_history(self, tmp_path, capsys):
        """边界：无历史版本时提示为空。"""
        _make_skill(tmp_path)
        version_manager.list_versions(str(tmp_path), "demo")
        assert "没有历史版本" in capsys.readouterr().out