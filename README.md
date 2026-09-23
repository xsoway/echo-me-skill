# echo-me-skill

> 蒸馏你自己，得到一个可运行的数字副本。
> Distill yourself into a runnable digital self.

echo-me-skill 是一个符合 skill-spec 工程契约 工程规范的 Skill 包：把**聊天记录、日记、照片**和你对自我的描述，解构为两层模型——**Self Memory（自我记忆）** + **Persona（人格）**——生成一个能用你的口头禅思考、用你的逻辑回话的自我镜像。

本包是对开源项目 `create-yourself`（[yourself-skill](https://github.com/notdog1998/yourself-skill) 衍生）的**独立品牌全量重写**与工程化升级，保留函数思路但代码、文案、示例全部原创。

---

## 它能做什么

- **创建**：三步（信息录入 → 原材料导入 → 生成写盘）完成一个 `/slug` 触发词可用的自我 Skill。
- **进化**：追加聊天/日记/照片持续更新自我；对话纠正立即写入 Correction 层。
- **管理**：`/list-echo`、`/echo-rollback`、`/echo-delete`。
- **工程化**：pytest 单测 + ruff 静态检查 + `uv` 依赖管理 + 包结构校验脚本。

## 快速开始

```bash
# 1. 安装依赖（python>=3.9，需 uv）
uv sync --extra dev

# 2. 创建你的第一个自我（触发主流程）
#    按 SKILL.md / prompts/echo-me-skill.md 的 Step A–E 执行

# 3. 校验包结构（本仓库自身不破坏契约）
python3 scripts/validate_skill_package.py .

# 4. 跑测试与静态检查
uv run pytest -q
uv run ruff check tools tests scripts
```

## 目录结构

见 [examples/skill-package-tree.md](examples/skill-package-tree.md)。

## 文档

| 文档 | 说明 |
|------|------|
| [SKILL.md](SKILL.md) | 入口：路由 + 硬约束（6 必需标题） |
| [prompts/echo-me-skill.md](prompts/echo-me-skill.md) | 主执行规范 |
| [references/package-contract.md](references/package-contract.md) | 包契约 |
| [references/skill-up-integration.md](references/skill-up-integration.md) | 评测接轨与验证边界 |
| [docs/PRD.md](docs/PRD.md) | 产品需求 |
| [README_EN.md](README_EN.md) | English |

## 许可与合规

- 本项目基于 MIT 许可发布。
- 派生于 [yourself-skill](https://github.com/notdog1998/yourself-skill)（原作者 notdog1998），LICENSE 中保留衍生声明。
- **重要**：`LICENSE` 与 `agents/openai.yaml` 中的 `<YOUR_NAME>` 占位符，**发布前必须替换**为你的真实姓名或 GitHub 用户名。

## 安全与边界

- 聊天记录、照片、个人信息等原材料只落到 `.claude/skills/{slug}/memories/`（gitignored），**绝不**进本包仓库。
- 生成的自我内容只能基于你提供的原材料或明说信息，**不臆造**经历、关系、价值观。
- 结构校验 PASS 只证明包完整；未运行真实模型评测时必须在交付中标注。

---

**贡献 / 反馈**：欢迎 fork + PR。先跑通 `validate` + pytest 再提交。