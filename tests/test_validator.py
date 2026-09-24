#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""validate_skill_package.py 回归测试。

重点验证发布守卫的真实契约：
- 结构齐全的包 → PASS
- 任一文本文件（含 .py/.html 等非 md/yaml）含密钥或绝对路径 → FAIL
"""
from __future__ import annotations

import contextlib
import io
import runpy
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
CASES = ("basic-success.yaml", "edge-incomplete-input.yaml", "edge-scope-boundary.yaml")
def _make_valid_package(root: Path, name: str | None = None) -> Path:
    """搭建一个结构合法、可被 validator 判 PASS 的最小 Skill 包。

    validator 用目录名作为 skill 名（name = root.name），因此 name 参数缺省时
    取自目录名，确保 prompts/{name}.md 与 frontmatter 一致。
    """
    name = name or root.name
    (root / "prompts").mkdir(parents=True)
    (root / "agents").mkdir()
    (root / "evals" / "cases").mkdir(parents=True)
    (root / "scripts").mkdir()
    headings = "\n\n".join(h + "\n占位" for h in REQUIRED_HEADINGS)
    (root / "SKILL.md").write_text(f"---\nname: {name}\n---\n\n{headings}\n", encoding="utf-8")
    (root / "prompts" / f"{name}.md").write_text("intake / analyze / write", encoding="utf-8")
    (root / "agents" / "openai.yaml").write_text(f'key: "{name}"\n', encoding="utf-8")
    (root / "evals" / "eval.yaml").write_text("environment:\n  type: none\n", encoding="utf-8")
    for case in CASES:
        (root / "evals" / "cases" / case).write_text("name: case\n", encoding="utf-8")
    (root / "scripts" / "validate_skill_package.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    return root


def _run_validator(package_dir: Path) -> tuple[int, str]:
    """以真实 CLI 方式运行 validator，返回 (退出码, 输出)。"""
    script = Path(__file__).resolve().parent.parent / "scripts" / "validate_skill_package.py"
    old_argv = sys.argv
    sys.argv = ["validate_skill_package.py", str(package_dir)]
    buf = io.StringIO()
    ret_code = 0
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            runpy.run_path(str(script), run_name="__main__")
    except SystemExit as exc:
        # SystemExit.code 可为 int/str/None；validator 用 raise SystemExit(main())，code 为 int
        ret_code = exc.code if isinstance(exc.code, int) else 1
    finally:
        sys.argv = old_argv
    return ret_code, buf.getvalue()


class TestPackageValidator:
    def test_valid_package_passes(self, tmp_path):
        """主路径：结构完整的包返回 PASS（退出码 0）。"""
        pkg = _make_valid_package(tmp_path / "repo")
        code, output = _run_validator(pkg)
        assert code == 0, output
        assert "PASS" in output

    def test_secret_in_python_file_fails(self, tmp_path):
        """回归：密钥出现在 .py 文件中必须 FAIL（漏扫是发布安全缺陷）。"""
        pkg = _make_valid_package(tmp_path / "repo")
        (pkg / "tools").mkdir()
        (pkg / "tools" / "leak.py").write_text(
            "# -*- coding: utf-8 -*-\nAPI_KEY = 'sk-live-abcdef1234567890'\n",
            encoding="utf-8",
        )
        code, output = _run_validator(pkg)
        assert code == 1
        assert "credential-like" in output

    def test_absolute_path_in_html_fails(self, tmp_path):
        """回归：绝对路径出现在 .html（Page 部署文件）中必须 FAIL。"""
        pkg = _make_valid_package(tmp_path / "repo")
        (pkg / "docs").mkdir()
        (pkg / "docs" / "index.html").write_text(
            '<html><body>src="/Users/joe/secret/data"</body></html>',
            encoding="utf-8",
        )
        code, output = _run_validator(pkg)
        assert code == 1
        assert "absolute local path" in output