# Skill-up 评测与验证边界（Integration）

本文件说明 echo-me-skill 如何与第三方 Skill 评测体系（如 skill-up / skill-spec 生态）接轨，以及哪些验证是允许、哪些是严禁伪报的。

## 1. 评测定位

echo-me-skill 是一个"生成自我镜像"的工作流型 Skill，其产物是 `.claude/skills/{slug}/` 目录下的内容。评测应当针对**工作流行为**（是否录入信息、是否读取原材料、是否生成两层模型、是否遵守边界），而不是一个固定返回值。

## 2. 本包自带的评测

- `evals/eval.yaml` 声明评测环境为静态（`environment.type: none`），即当前不做模型级自动评测，只做包结构校验。
- 三个 case 覆盖：基础成功、信息不完整（仅凭自我介绍生成 + 标注还原度）、范围/风险边界（拒绝越界请求）。

## 3. 接入第三方评测

若要接入 skill-up 或等价评测器：

1. 将 `evals/cases/*.yaml` 映射到评测器支持的 case 格式（见各评测器文档）。
2. 评测器运行 agent 走完整 `prompts/echo-me-skill.md` 流程，输入模拟的用户意图。
3. 判定维度建议：是否澄清信息缺口、是否读取原材料、Self Memory 与 Persona 是否分层、是否遵守"不臆造/不越界"。

## 4. 验证诚实原则（严禁）

- 结构校验（`validate_skill_package.py` PASS）仅证明"包完整"，**不等于**"模型行为已通过评测"。
- 未运行真实模型评测时，交付说明必须标注"未运行项"，不得伪造"已通过"。
- 评测日志不得包含真实密钥、用户数据或本机绝对路径。

## 5. 推荐的发布前检查表

- [ ] `validate_skill_package.py` PASS
- [ ] 单元测试 `uv run pytest -q` 通过
- [ ] ruff 静态检查通过
- [ ] LICENSE / agents 中的作者占位符已替换
- [ ] 未把本机绝对路径或真实数据写入任何仓库文件