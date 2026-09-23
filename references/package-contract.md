# 包契约（Package Contract）

本文件定义 echo-me-skill 作为一个可独立安装的 Skill 包所必须满足的结构与内容约束。它是 `scripts/validate_skill_package.py` 的行为描述，也是"把它放到别的 Agent 环境能否正确被发现与加载"的判据。

## 1. 必需文件

| 相对路径 | 作用 |
|----------|------|
| `SKILL.md` | 轻量入口：frontmatter（`name` 与目录名一致）+ 6 个必需标题 + 硬约束 |
| `prompts/echo-me-skill.md` | 主执行规范：输入、判断、Step 流程、输出、质量与边界 |
| `agents/openai.yaml` | 发现元数据；`metadata.key` 必须与目录名一致 |
| `evals/eval.yaml` | 评测清单，声明评测环境（当前为 `none`，即静态结构评测） |
| `evals/cases/` | 三类评测样本：`basic-success`、`edge-incomplete-input`、`edge-scope-boundary` |
| `scripts/validate_skill_package.py` | 可独立执行的包结构校验脚本 |
| `references/`、`examples/` | SKILL.md 引用到的说明与标准骨架 |

## 2. 入口（SKILL.md）约束

- frontmatter `name` 必须等于目录名。
- 必须包含以下六个字面标题：`## 何时使用`、`## 输出格式选项`、`## 如何使用`、`## 参考文件`、`## 常见误区`、`## 最佳实践`。
- 入口保持轻量：只做路由 + 硬约束；完整流程放 `prompts/`。

## 3. 元数据约束

- `agents/openai.yaml` 的 `metadata.key` 必须等于目录名。
- `author` 必须为真实作者（github username 或真实姓名）；当前为 `xsoway`。缺失或为 `<YOUR_NAME>` 占位符时视为未就绪。

## 4. 评测约束

- 至少在成功、信息不完整、范围/风险边界三个维度各有一类 case。
- 结构校验 PASS 只证明"包完整"，不等于"模型行为已验证"；这不属于可伪造的指标。

## 5. 安全约束

- 任何 `.md` / `.yaml` 不得包含凭据样式内容（例如会话密钥前缀、授权请求头名、密钥字面量等）。
- 任何文档不得包含指向本机用户主目录的绝对路径。
- 原材料、聊天记录、照片、个人信息一律落到 `.claude/skills/{slug}/memories/`（gitignored），不进本包仓库。

## 6. 运行校验

```bash
python3 scripts/validate_skill_package.py <skill-dir>
```

输出 `PASS: <name> package contract` 且退出码 0 即通过。