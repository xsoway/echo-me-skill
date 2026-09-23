---
name: echo-me-skill
description: >-
  Create, evolve and manage a runnable digital self. Distil your chat history,
  diaries and photos into a two-layer model (Self Memory + Persona) that speaks
  and thinks like you. Use when the user asks to 创建自我镜像、把聊天记录/日记/照片变成数字副本、
  蒸馏自己为 Skill、生成像你一样说话的 AI、追加材料进化自我 or build a personal AI twin.
version: 1.0.0
argument-hint: "[your-name-or-slug]"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# echo-me-skill

> **语言 / Language**: 中英双语。根据用户第一条消息的语言全程使用同一语言。指令以 `prompts/echo-me-skill.md` 为准，本文件只做路由与硬约束。

## 何时使用

用户表达以下任意意图时启动主流程：
- `/echo-me` / "创建一个我的数字副本" / "把聊天记录蒸馏成我自己"
- "生成一个像我一样思考说话的 AI" / "我想把自己变成 Skill" / "新建自我镜像"
- 对已有自我说 "追加" / "更新" / "这不对，我不会这样说" / `/update-echo-me {slug}` 进入进化模式

## 输出格式选项

- 默认产物：一个完整的自我 Skill 目录 `.claude/skills/{slug}/`（Entrance + self.md + persona.md + meta.json）。
- 可选产物：仅 Self Memory（`-self`）、仅 Persona（`-persona`）、历史版本回滚、删除。
- 任何外部评测、验证或评测运行结果不得伪造为"已通过"。

## 如何使用

1. 先读 `prompts/echo-me-skill.md`（主执行规范），按它的 Step 流程推进；需要单个模板时读对应 `prompts/*.md`。
2. 需要解析聊天记录/照片时调用 `tools/` 下的解析器（见主 prompt 的命令表）。
3. 生成或改动包后，自行用 `scripts/validate_skill_package.py` 校验本包结构。

## 参考文件

- `prompts/echo-me-skill.md` — 主执行规范（输入、判断、Step、输出、质量、边界）。
- 包契约与独立安装要求：`references/package-contract.md`。
- Skill-up 评测与验证边界：`references/skill-up-integration.md`。
- 标准包目录骨架：`examples/skill-package-tree.md`。

## 常见误区

- 只建一个 `SKILL.md`，没有主 Prompt、元数据、评测与可执行验证。
- 把 YAML/静态结构校验通过说成"模型行为已验证"。
- 把仓库分类、安装器、CI、发布流程等与本工程无关的内容塞进 Skill。
- 在文档、示例、评测或日志中放入真实密钥、用户数据或绝对本机路径。

## 最佳实践

- 入口保持轻量：路由 + 硬约束；完整细节放 `prompts/`，按需加载。
- 新/改 Skill 至少具备成功、信息不完整、范围/风险边界三类 Eval。
- 先声明已知事实、信息缺口与最小假设，再执行；缺少外部数据时完成静态产物并明确标注未运行项。
- 生成自我的所有内容都基于用户提供的原材料，不臆造经历。

---

## 硬约束（最高优先级）

1. **品牌与署名**：本包是 `echo-me-skill`，独立作者；任何对外文案不得声称是原 `yourself-skill` 的延续。涉及衍生声明时引用 LICENSE 中的原始项目即可。
2. **数据安全**：任何原材料、用户聊天记录、照片、个人信息，**绝不**写入本包仓库、README、示例或评测。生成的自我 Skill 落在 `.claude/skills/{slug}/`（gitignored）。
3. **不臆造**：Self Memory 只能来自用户提供的原材料或明说的信息；信息缺口必须询问，不得编造经历、价值观或人际关系。
4. **工具边界**：解析器只做本地文件解析（Read/Bash），不做任何外部网络抓取或未授权动作。
5. **验证诚实**：结构校验 PASS 只证明"包完整"，不代表模型效果达标；未运行真实评测时必须在交付里标注。

---

## 触发词快速路由

| 用户意图 | 动作 |
|----------|------|
| 创建新自我 | 主流程（读 `prompts/echo-me-skill.md`） |
| 追加文件进化 | 进化模式 Step（merge） |
| 对话纠正 | correction 流程，写入 Correction 层 |
| `/list-echo` | 列出所有自我 |
| `/echo-rollback {slug} {v}` | 回滚版本 |
| `/echo-delete {slug}` | 删除 |