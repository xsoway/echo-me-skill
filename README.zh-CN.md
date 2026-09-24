---
updated: 2026-09-24 06:30:55
---

<p align="center">
  <img alt="版本" src="https://img.shields.io/badge/version-1.0.0-blue.svg">
  <img alt="协议" src="https://img.shields.io/badge/license-MIT-green.svg">
  <img alt="状态" src="https://img.shields.io/badge/status-beta-yellow.svg">
  <img alt="Python" src="https://img.shields.io/badge/python-3.9%2B-blue.svg">
</p>
<h1 align="center">echo-me-skill</h1>
<p align="center">蒸馏你自己，得到一个可运行的数字副本。</p>
<p align="center"><a href="./README.md">English</a></p>
<p align="center">可发现 · 可安装 · 可评测 —— 一个自包含的 Skill 包形式的个人 AI 分身。</p>

<hr>

## 目录

- [是什么](#是什么)
- [为什么需要](#为什么需要)
- [核心概念](#核心概念)
- [仓库结构](#仓库结构)
- [快速开始](#快速开始)
- [功能与用法](#功能与用法)
- [配置](#配置)
- [安全与边界](#安全与边界)
- [FAQ](#faq)
- [路线图](#路线图)
- [贡献指南](#贡献指南)
- [License](#license)
- [维护者](#维护者)

---

## 是什么

`echo-me-skill` 是一个符合 [skill-spec](https://github.com/xsoway/skill-spec) 工程契约的 **Skill 包**：把**聊天记录、日记、照片**和你对自我的描述，解构为两层模型——**Self Memory（自我记忆）** + **Persona（人格）**——生成一个能用你的口头禅思考、用你的逻辑回话的自我镜像。

本包是对开源项目 [create-yourself](https://github.com/notdog1998/yourself-skill)（`yourself-skill`，作者 notdog1998）的**独立品牌全量重写**：保留函数思路，但代码、文案、示例全部原创，独立署名，基于 MIT 许可分发，欢迎发 issue、PR 与二次开发。

## 为什么需要

多数"数字化自己"的尝试会掉进两个坑：要么凭空捏造一个人格，要么把原始聊天记录一股脑堆进去而毫无结构。本包为避开这两者而存在。

| 痛点 | 常见做法 | echo-me-skill |
|------|----------|---------------|
| 没有真实材料 → 人格全靠编 | 让模型"猜"你的性格 | 绝不臆造：只基于你提供的原材料或明说的事实 |
| 原材料泄漏进仓库 | 聊天记录被提交进 git | 原材料只落到 gitignored 的 `.claude/skills/{slug}/memories/` |
| 单一大块、难进化 | 一个"关于我"的文件 | 两层模型（Self Memory + Persona）+ Correction 层，增量进化 |
| 打包不可测试 | 复制粘贴的 skill 文件夹 | skill-spec 契约 + 校验器 + pytest + ruff |

**为什么要一个数字自我**——保存"此刻的你"：从你说过的话里学会你怎么说话、在意什么，并在你变化时持续维护这面镜子。

## 核心概念

- **Self Memory（自我记忆）** —— *你知道什么、你是谁*：经历、价值观、生活习惯、重要记忆、人际关系、成长轨迹。
- **Persona（人格）** —— *你怎么回应*：说话风格、情感模式、决策模式、人际行为——把标签翻译成具体行为规则。
- **Correction 层** —— 你的对话纠正立即写入，优先级高于既有结论。
- **两层模型** —— 先判 Persona（怎么回话），再由 Self Memory 补充（回得是否真实）。

## 仓库结构

```text
echo-me-skill/
├── AGENTS.md                 # 项目规则（继承工作区总纲）
├── CLAUDE.md                 # Claude Code 入口（回读父级规则）
├── LICENSE                   # MIT，含对 yourself-skill 的衍生声明
├── README.md                 # English
├── README.zh-CN.md           # 中文（本文件）
├── SKILL.md                  # 入口：frontmatter + 6 必需标题 + 硬约束
├── pyproject.toml            # uv / pytest / ruff 配置
├── .gitignore
├── agents/
│   └── openai.yaml           # 发现元数据（key 与目录名一致）
├── prompts/
│   ├── echo-me-skill.md      # 主执行规范（Step A–E、进化、管理）
│   └── self_analyzer / persona_analyzer / *_builder / merger / correction_handler / intake
├── evals/
│   ├── eval.yaml
│   └── cases/                # basic-success、edge-incomplete-input、edge-scope-boundary
├── scripts/
│   └── validate_skill_package.py   # 包结构校验
├── tools/                    # 解析器与管理器（可独立 CLI + 可导入）
│   ├── wechat_parser.py
│   ├── qq_parser.py
│   ├── social_parser.py
│   ├── photo_analyzer.py
│   ├── skill_writer.py
│   └── version_manager.py
├── references/
│   ├── package-contract.md
│   └── skill-up-integration.md
├── examples/
│   └── skill-package-tree.md
├── docs/
│   └── PRD.md
├── selves/                   # 中性示例自我（仅占位）
│   └── example_me/
└── tests/                    # pytest 单测
```

## 快速开始

环境要求：Python `>=3.9`，并安装 [uv](https://docs.astral.sh/uv/)。

```bash
# 1. 安装依赖
uv sync --extra dev

# 2. 创建你的第一个自我（触发主流程）
#    按 SKILL.md / prompts/echo-me-skill.md 的 Step A–E 执行：
#    A) 信息录入  B) 原材料导入  C–E) 分析、预览、写盘
#    产出落在 ./.claude/skills/{slug}/，通过 /{slug} 触发词使用。

# 3. 校验包结构（本仓库自身不破坏契约）
python3 scripts/validate_skill_package.py .
# → PASS: echo-me-skill package contract

# 4. 跑测试与静态检查
uv run pytest -q       # → 20 passed
uv run ruff check tools tests scripts   # → All checks passed
```

## 功能与用法

### 创建

三步：信息录入（≤3 问）→ 原材料导入（可跳过）→ 分析、预览、写盘（通过解析器/管理器工具）：

```bash
# 微信聊天记录                 QQ 聊天记录
python tools/wechat_parser.py --file chat.txt --target "我" --output /tmp/w.txt
python tools/qq_parser.py      --file chat.txt --target "我" --output /tmp/q.txt

# 照片元信息                    写盘创建自我
python tools/photo_analyzer.py --dir ./photos --output /tmp/p.txt
python tools/skill_writer.py --action create --slug {slug} \
  --base-dir ./.claude/skills --meta ./meta.json --self ./self.md --persona ./persona.md
```

创建后可通过 `/` 触发词使用：`/{slug}`（完整）、`/{slug}-self`（自我档案）、`/{slug}-persona`（仅人格）。

### 进化（增量追加）

- **追加材料**：先备份，读现有 `self.md`/`persona.md`，只合并增量（`version_manager --action backup`），绝不覆盖既有结论。
- **对话纠正**：你表示"这不对 / 我不会这样说"时，写入 Correction 层并立即重新 combine。

### 管理

| 命令 | 动作 |
|------|------|
| `/list-echo` | 列出全部自我 |
| `/echo-rollback {slug} {v}` | 回滚到指定版本 |
| `/echo-rollback {slug}` | 列出历史版本 |
| `/echo-delete {slug}` | 删除某个自我（需确认） |

## 配置

| 项 | 位置 | 说明 |
|----|------|------|
| 项目元数据 | `pyproject.toml` | name、version、author、依赖 |
| Skill 发现元数据 | `agents/openai.yaml` | `metadata.key` 必须与目录名一致 |
| 评测环境 | `evals/eval.yaml` | 静态结构评测（`environment.type: none`） |
| 秘密/绝对路径扫描 | `scripts/validate_skill_package.py` | 由校验器完成 |

无运行时配置文件：Skill 按需读取用户意图与原材料；生成的自我落在 `.claude/skills/{slug}/`，由 `skill_writer` / `version_manager` 工具管理。

## 安全与边界

- **不臆造**：生成的自我只基于你的原材料或明说的信息；信息缺口会询问，绝不编造。
- **原材料不入库**：聊天记录、照片、个人信息只落到 `.claude/skills/{slug}/memories/`（gitignored）。
- **仅本地**：解析器只做本地文件解析（Read/Bash）——不抓取网页、不做未授权网络动作。
- **验证诚实**：结构校验 PASS 只证明包完整，**不等于**模型行为已验证；未运行真实评测时交付说明必须标注。
- 拒绝：抓取他人隐私数据、发布到未授权位置、冒充原作者作品。

## FAQ

**Q：它会训练或微调模型吗？** 不会。它把原材料蒸馏为结构化的 Self Memory + Persona 文件——无模型训练、无外部网络。

**Q：只给我一段自我介绍可以吗？** 可以，但还原度较低；流程会明确标注并请你补材料来填补缺口。

**Q：我的数据会去哪？** 只落到你机器上 gitignored 的 `.claude/skills/{slug}/` 运行目录，绝不进入本包仓库。

**Q：validate 通过就等于"能用"吗？** 不等于。结构 PASS 只说明包完整；真实模型行为是另一项需显式评测的内容。

## 路线图

- [x] 独立品牌全量重写（代码、文案、示例全部原创）
- [x] skill-spec 契约 + 校验器 + pytest + ruff + uv
- [x] 两层模型（Self Memory + Persona）+ Correction 层
- [x] 创建 / 进化 / 管理流程
- [ ] 落地真实模型级评测（`environment.type: none` → agent 运行）
- [ ] 发布到 GitHub（配置 origin + releases）
- [ ] PyPI 发布就绪

## 贡献指南

欢迎 fork + PR。提交前请先**证明**改动：

```bash
uv sync --extra dev
python3 scripts/validate_skill_package.py .
uv run pytest -q
uv run ruff check tools tests scripts
```

遵守 `AGENTS.md` 项目规则：中文文件头/注释、已提交文件中不得含真实用户数据或本机绝对路径、验证声明诚实。

## License

基于 [MIT 协议](LICENSE) 发布。派生于 [yourself-skill](https://github.com/notdog1998/yourself-skill)（作者 notdog1998），LICENSE 保留衍生声明。本仓库所有代码与内容均为作者原创。

## 维护者

[xsoway](https://github.com/xsoway)