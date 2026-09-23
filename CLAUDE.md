<!-- code_project: parent-agents-required -->

# CLAUDE.md - echo-me-skill

本文件用于 Claude Code 进入本项目时的规则引导。

## 首要职责：回读父级规则

Claude Code 进入本目录后，**第一步**必须回读并按顺序遵循以下三个 `AGENTS.md`：

1. `code_project/AGENTS.md`（工作区总纲）——项目绝对路径位于
   `code_project 仓库根目录的 AGENTS.md（即工作区总纲）`；
2. `code_project/src/AGENTS.md`（src 统一桥接规则）；
3. 本项目的 `AGENTS.md`（当前目录下）。

规则优先级：用户当前明确要求 > 工作区根 `AGENTS.md` > `src/AGENTS.md` > 本项目 `AGENTS.md`。
项目文件只能增加更严格的约束，不能放宽父级规则。

修改本项目 `AGENTS.md` / `CLAUDE.md` 后，必须运行根目录审计脚本 `python3 -B tools/verify_agent_inheritance.py`，通过后方可声明规则改造完成。

## 项目一句话

echo-me-skill：把聊天记录/日记/照片蒸馏成可运行的"数字自画像"（Self Memory + Persona）的 Skill 包，基于 `yourself-skill` 全量重写、独立品牌开源。

## 常用命令

- 依赖：`uv sync --extra dev`
- 测试：`uv run pytest -q`
- lint：`uv run ruff check tools tests scripts`
- 校验：`python3 scripts/validate_skill_package.py .`

## 数据与合规红线（最高优先级）

1. **不臆造**：自我内容只能来自用户材料或明说信息，信息缺口必须询问。
2. **原材料不入库**：只落 `.claude/skills/{slug}/memories/`（gitignored）。
3. **无绝对路径/无密钥**：仓库内的 `.md`/`.yaml` 不得含本机绝对路径（指向用户主目录的路径）或凭据样式内容。
4. **验证诚实**：结构校验 PASS 不等于模型行为已验证。
5. **合规署名**：`LICENSE`/`agents/openai.yaml` 的 `<YOUR_NAME>` 未替换前不得宣称可发布。