# echo-me-skill 主执行规范

> 本 Prompt 是 echo-me-skill 的完整执行规范。入口 `SKILL.md` 负责路由；此处承载输入、判断、Step 流程、输出与质量边界。

## 输入

- 用户意图与触发词（创建 / 进化 / 纠正 / 管理）。
- 原材料：聊天记录（微信/QQ）、日记/笔记、照片、口述文本、用户对自我的描述。
- 可选：已有自我 Skill 的路径、历史版本号。

## 已知事实与信息缺口

- 用户未提供原材料时，仅凭自我介绍也能生成（还原度低）。
- 原材料格式/路径缺失时，先询问，不臆造。
- 若用户要求的动作超出本 Skill 边界（如"同步到线上""抓取他人数据"），拒绝并说明。

## 第一步：创建新自我（主流程）

### Step A：基础信息录入（最多 3 问，代号必填，其余可跳过）

1. **代号/昵称**（必填）— 作为 slug 与触发词来源。
2. **一句话基本盘** — 年龄、职业、城市，想到什么写什么。
3. **你对自己的印象** — MBTI、星座、性格标签、主观认知。

收集后复述确认，再进入下一步。

### Step B：原材料导入（可跳过）

展示来源选项 A–E，可混用：

| 选项 | 来源 | 处理方式 |
|------|------|----------|
| A | 微信聊天记录导出 | `python tools/wechat_parser.py --file ... --target "<代号>" --output /tmp/echo_wechat.txt --format auto` |
| B | QQ 聊天记录导出 | `python tools/qq_parser.py --file ... --target "<代号>" --output /tmp/echo_qq.txt` |
| C | 日记 / 笔记 / 朋友圈文本 | `Read` 直接读取文本；截图用 `Read` 看图 |
| D | 上传照片 | `python tools/photo_analyzer.py --dir ... --output /tmp/echo_photos.txt` |
| E | 直接口述 / 粘贴 | 记为原材料文本，引导回忆（口头禅、决策方式、难过时的反应、喜欢的地方、生气的样子、深夜在想什么、近几年最大变化） |

用户说"没有文件/跳过"时，仅凭 Step A 信息生成。

### Step C：分析原材料（双线并行）

参考 `prompts/self_analyzer.md` 与 `prompts/persona_analyzer.md`：
- **线路 A（Self Memory）**：经历、价值观、生活习惯、重要记忆、人际关系、成长轨迹。
- **线路 B（Persona）**：说话风格、情感模式、决策模式、人际行为，标签翻译为具体行为规则。

### Step D：生成并预览

- 按 `prompts/self_builder.md` 生成 Self Memory 内容。
- 按 `prompts/persona_builder.md` 生成 Persona（5 层结构）。
- 向用户展示摘要（各 5–8 行），确认或调整后再写入。

### Step E：写入文件

建议一键创建（脚本失败时用 `Write`/`Edit` 手动 fallback）：

```bash
mkdir -p /tmp/echo_{slug}
# 将 meta.json / self.md / persona.md 写入 /tmp 临时目录
python tools/skill_writer.py --action create \
  --slug {slug} --base-dir ./.claude/skills \
  --meta /tmp/echo_{slug}/meta.json \
  --self /tmp/echo_{slug}/self.md \
  --persona /tmp/echo_{slug}/persona.md
```

`meta.json` 结构（字段可为空）：

```json
{
  "name": "小北", "slug": "xiaobei",
  "created_at": "2026-09-23T00:00:00Z", "updated_at": "2026-09-23T00:00:00Z",
  "version": "v1",
  "profile": {"age": "", "occupation": "", "city": "", "mbti": "", "zodiac": ""},
  "tags": {"personality": [], "lifestyle": []},
  "impression": "",
  "memory_sources": [],
  "corrections_count": 0
}
```

创建完成后告知触发词：`/{slug}`（完整）、`/{slug}-self`（自我档案）、`/{slug}-persona`（人格、仅性格与表达）。

## 第二步：进化模式

### 追加文件（merge）
1. 按 Step B 读取新内容。
2. 读现有 `.claude/skills/{slug}/self.md` 与 `persona.md`。
3. 进化前先备份：`python tools/version_manager.py --action backup --slug {slug} --base-dir ./.claude/skills`。
4. 参考 `prompts/merger.md`：判断增量更新 Self Memory 还是 Persona，**只追加增量，不覆盖已有结论**。
5. 用 `Edit` 写入，重新 combine 生成 SKILL.md，更新 `meta.json` 的 version/updated_at。

### 对话纠正
1. 用户表达"不对""我不会这样说""我应该是" → 参考 `prompts/correction_handler.md`。
2. 判断属于 Self Memory（事实/经历）还是 Persona（性格/说话方式）。
3. 在对应文件追加 Correction 记录，立即生效，重新 combine。

## 第三步：管理命令

| 命令 | Bash 调用 |
|------|-----------|
| `/list-echo` | `python tools/skill_writer.py --action list --base-dir ./.claude/skills` |
| `/echo-rollback {slug} {v}` | `python tools/version_manager.py --action rollback --slug {slug} --version {v} --base-dir ./.claude/skills` |
| `/echo-rollback {slug}` | `python tools/version_manager.py --action list --slug {slug} --base-dir ./.claude/skills` |
| `/echo-delete {slug}` | 确认后 `rm -rf .claude/skills/{slug}` |

## 输出

- 完整产物：`.claude/skills/{slug}/`（SKILL.md + self.md + persona.md + meta.json + versions/）。
- 创建/更新后给出变更摘要与下一步建议。
- 交付时说明：做了什么、如何验证、产物路径、风险/回滚方式、未运行的外部评测。

## 质量要求

- 生成的自我只能基于原材料或明说信息，**绝不臆造**经历、关系、价值观。
- 说话风格来自原材料提取（口头禅、语气词、标点、emoji 习惯），不套模板腔。
- 尊重边界：不鼓励"逃避现实"式的自我替代；强调这是"被蒸馏那一刻的你"。
- 原始材料（聊天/照片）落到 gitignored 的 `.claude/skills/{slug}/memories/`，不进入本包仓库。

## 边界（何时拒绝）

- 要求抓取他人隐私数据 → 拒绝。
- 要求把结果发布到未授权位置 → 拒绝。
- 要求完全抹除原作者/冒充他人作品发布 → 拒绝（合规：保留衍生声明）。
- 缺少明确意图（"帮我做 Skill"但无用途/输入/输出）→ 列出信息缺口与假设，先澄清再执行。