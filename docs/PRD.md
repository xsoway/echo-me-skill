# echo-me-skill 产品需求文档（PRD）

> 版本：1.0.0 · 状态：实现中 → 待发布
> 对应开源衍生来源：[yourself-skill](https://github.com/notdog1998/yourself-skill)。本项目为独立品牌全量重写。

## 1. 背景与目标

用户希望有一个能"蒸馏自己"的 Skill：把聊天记录、日记、照片与自我描述转化为一个可运行的数字副本，让它像自己一样思考和说话。原 `create-yourself`/`yourself-skill` 提供了雏形，但存在工程化不足、品牌混淆、无法独立开源的问题。

**目标**：交付一个符合 skill-spec 工程规范、可独立开源、品牌独立的 Skill 包 `echo-me-skill`。

**非目标**：
- 不追踪真实用户数据，不把原材料入库。
- 不做模型训练或微调；不接入任何外部网络抓取。
- 不冒充原作者或他人作品。

## 2. 用户与场景

- **角色**：想保留"被蒸馏那一刻的自己"的个人用户。
- **场景 A（创建）**：首次把历史材料变成自我镜像。
- **场景 B（进化）**：持续追加新材料/对话纠正，保持镜像鲜活。
- **场景 C（管理）**：列表、回滚、删除多个自我。
- **场景 D（贡献）**：开发者 fork 本包做二次开发与评测。

## 3. 核心概念

- **Self Memory（自我记忆）**：经历、价值观、生活习惯、重要记忆、人际关系、成长轨迹。
- **Persona（人格）**：说话风格、情感模式、决策模式、人际行为——把标签翻译成具体行为规则。
- **Correction 层**：用户纠正即时写入，优先级高于既有结论。
- **两层模型**：先判断 Persona（怎么回应），再由 Self Memory 补充（回得是否真实）。

## 4. 功能需求

### F1 创建新自我（P0）
- 三步流程：Step A 信息录入（≤3 问，代号必填）→ Step B 原材料导入（可跳过）→ Step C-E 分析、预览、写盘。
- 产物：`.claude/skills/{slug}/`（SKILL.md + self.md + persona.md + meta.json + versions/）。
- 触发词：`/{slug}`、`/{slug}-self`、`/{slug}-persona`。

### F2 进化模式（P1）
- 追加文件（merge）：进化前先 backup；只追加增量，不覆盖既有结论。
- 对话纠正：写 Correction 层，立即生效，重新 combine。

### F3 管理命令（P1）
- `/list-echo`、`/echo-rollback {slug} {v}`、`/echo-rollback {slug}`（列出）、`/echo-delete {slug}`。

### F4 工程化与合规（P0）
- 可执行校验：`scripts/validate_skill_package.py` 校验包结构（name/key/6 标题/3 case/秘密/绝对路径）。
- pytest 单测 + ruff 静态检查 + uv 依赖管理。
- 数据安全：原材料落到 gitignored 目录，不进仓库。

## 5. 数据与隐私

- 输入：聊天记录/日记/照片/口述——全部用户本地材料。
- 存储：`memories/` gitignored；本包仓库零原材料。
- 绝不臆造：信息缺口必须询问，不编造经历、价值观、人际关系。

## 6. 评测与验收

- **结构**：`validate_skill_package.py` MUST PASS。
- **行为**：三类 eval case（成功 / 信息不完整 / 范围边界）。
- **工程**：`uv run pytest -q` 全绿；`uv run ruff check` 通过。
- **诚实**：结构 PASS ≠ 模型行为验证；未运行真实评测须标注。

## 7. 发布清单

- [x] LICENSE / agents / pyproject 作者署名已替换为 `xsoway`
- [ ] `git init` 从零重建历史，脱钩原 origin（当前单提交，无 origin）
- [x] `validate` + pytest + ruff 全绿
- [ ] 文档（README.md / README.zh-CN.md / PRD）齐全
- [ ] 归档 verify-log

## 8. 风险与回滚

- **风险**：占位符未替换就发布 → 合规问题。缓解：发布清单强制项。
- **风险**：与新 Agent 环境契约不兼容 → 缓解：严格按 skill-spec 契约 + validate 脚本兜底。
- **回滚**：生成的自我 Skill 由 `version_manager` 支持版本回滚；代码由 git 历史回滚。