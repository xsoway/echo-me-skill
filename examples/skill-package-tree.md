# 标准包目录骨架（Skill Package Tree）

这是一个符合 skill-spec 契约的 Skill 包应具备的目录布局，以 echo-me-skill 为实例。

```text
echo-me-skill/
├── AGENTS.md                 # 项目级规则（继承工作区总纲）
├── CLAUDE.md                 # Claude Code 入口（回读父级规则）
├── LICENSE                   # MIT（含对原 yourself-skill 的衍生声明）
├── README.md                 # 中文说明
├── README_EN.md              # English description
├── SKILL.md                  # 轻量入口：frontmatter + 6 必需标题 + 硬约束
├── pyproject.toml            # uv / pytest / ruff 工程化配置
├── .gitignore
├── agents/
│   └── openai.yaml           # 发现元数据（key 与目录名一致）
├── prompts/
│   ├── echo-me-skill.md      # 主执行规范
│   └── *_analyzer/_builder/_merger/_correction 等模板
├── evals/
│   ├── eval.yaml
│   └── cases/
│       ├── basic-success.yaml
│       ├── edge-incomplete-input.yaml
│       └── edge-scope-boundary.yaml
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
├── selves/                   # 示例自我（中性占位，原材料式内容 gitignored）
│   └── example_me/
└── tests/                    # pytest 单测
```

## 说明

- `SKILL.md` 只做路由与硬约束，细节全部下沉到 `prompts/`。
- 运行时生成的自我落地到 `.claude/skills/{slug}/`（不在本包仓库内）。
- 原材料目录 `memories/` 一律 gitignored，不进版本库。