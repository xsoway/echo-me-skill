<!-- code_project: parent-agents-required -->

# AGENTS.md - echo-me-skill 项目规则

## 父级规则继承（强制）

本文件是 `echo-me-skill` 项目的局部规则。进入本目录前，必须按以下顺序读取并遵循：

1. `code_project/AGENTS.md`（工作区总纲）；
2. `code_project/src/AGENTS.md`（src 统一桥接规则）；
3. 本文件（`echo-me-skill` 项目局部规则）。

规则优先级固定为：用户当前明确要求 > 工作区根 `AGENTS.md` > `src/AGENTS.md` > 本文件。本文件只能补充更严格的业务、数据、安全或验证要求，不能放宽父级规则。

修改本文件的 `src/*/AGENTS.md`、`src/*/CLAUDE.md` 同级文件后，必须运行根目录审计脚本：
```bash
python3 -B tools/verify_agent_inheritance.py
```
未通过前不得声明规则改造完成。

## 项目概述

echo-me-skill 是一个符合 skill-spec 工程契约的 Skill 包：把聊天记录、日记、照片与自我描述蒸馏成可运行的"数字自画像"（Self Memory + Persona）。基于 `create-yourself`/`yourself-skill` 全量重写，独立品牌开源。

## 构建 / 测试 / 验证命令

- 依赖安装：`uv sync --extra dev`
- 单元测试：`uv run pytest -q`
- 静态检查：`uv run ruff check tools tests scripts`
- 包结构校验：`python3 scripts/validate_skill_package.py .`
- 运行时生成的是用户自我镜像（`.claude/skills/{slug}/`），不是本仓库代码；本仓库代码以 `tools/`、`tests/`、`prompts/` 为主。

## 工程规范（继承父级，补充本包约束）

- Python 文件必须含中文文件头（`@Time`/`@Filename`/`@Author`），中文注释，`if __name__ == "__main__"` 入口。
- `tools/` 下脚本既可独立 CLI 运行（`python tools/*.py`），也可被 `tests/` 导入测试；两者契约必须一致。
- 日志规范按根 AGENTS.md；本包脚本以 print/CLI 输出为主（作为 Skill 工具被 Bash 调用），不引入 OSS 日志框架。

## 数据与合规红线（本包特有，最高优先级）

1. **不臆造**：生成的自我内容只能来自用户提供的原材料或明说信息；信息缺口必须询问，不得编造经历、价值观、人际关系。
2. **原材料不入库**：聊天记录、照片、个人信息等只能落到 `.claude/skills/{slug}/memories/`（gitignored），绝不可写入本包仓库的文档、示例、评测或日志。
3. **无绝对路径 / 无密钥**：仓库内 `.md`/`.yaml` 不得含本机绝对路径（例如指向用户主目录的路径）或凭据样式内容。
4. **验证诚实**：`validate_skill_package.py` PASS 只证明包完整，不等于模型行为已验证；未运行真实评测时必须标注。
5. **合规署名**：LICENSE 与 `agents/openai.yaml` 的 `<YOUR_NAME>` 占位符是发布前置条件，未替换前不得宣称"可发布"。对原 `yourself-skill` 的衍生声明保留在 LICENSE。

## 检查清单（默认）

做代码/文档修改或审查时至少检查：是否有未处理异常、命名是否清晰、是否破坏工具 CLI 契约（`tools/*.py` 参数）、是否会泄露用户数据或绝对路径、是否补充/更新测试、是否跑通 `validate`+`pytest`+`ruff`、长结论是否沉淀到正确文档。