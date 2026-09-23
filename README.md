<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/version-1.0.0-blue.svg">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green.svg">
  <img alt="Status" src="https://img.shields.io/badge/status-beta-yellow.svg">
  <img alt="Python" src="https://img.shields.io/badge/python-3.9%2B-blue.svg">
</p>
<h1 align="center">echo-me-skill</h1>
<p align="center">Distill yourself into a runnable digital self.</p>
<p align="center"><a href="./README.zh-CN.md">中文</a></p>
<p align="center">Discoverable · Installable · Evallable — a personal AI twin as a self-contained Skill package.</p>

<hr>

## Table of Contents

- [What is it](#what-is-it)
- [Why](#why)
- [Core concepts](#core-concepts)
- [Repository structure](#repository-structure)
- [Quick start](#quick-start)
- [Features & usage](#features--usage)
- [Configuration](#configuration)
- [Safety & boundaries](#safety--boundaries)
- [FAQ](#faq)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Maintainer](#maintainer)

---

## What is it

`echo-me-skill` is a **Skill package** built to the
[skill-spec](https://github.com/yourself-skill/skill-spec) engineering contract.
It decomposes your **chat history, diaries and photos** — plus your own
description of yourself — into a two-layer model, **Self Memory** + **Persona**,
and produces a digital mirror that thinks and speaks the way you do.

It is an **independent, fully rewritten** brand built on the open-source
[`create-yourself`](https://github.com/notdog1998/yourself-skill) project
(derived from `yourself-skill` by notdog1998). Function ideas are preserved;
code, copy and examples are original. Issues, PRs and derivatives are welcome
under the MIT License.

## Why

Most attempts to "digitize yourself" fall into one of two traps: they either
hallucinate a persona from nothing, or they dump raw transcripts without
structure. This package exists to avoid both.

| Pain point | Typical approach | echo-me-skill |
|-----------|------------------|---------------|
| No real material → fabricated persona | Model "guesses" your personality | Never fabricates: only raw material you provide, or explicitly stated facts |
| Raw data leaks into the repo | Transcripts committed to git | Material only lands in gitignored `.claude/skills/{slug}/memories/` |
| One flat blob, hard to evolve | A single "about me" file | Two-layer model (Self Memory + Persona) + Correction layer, append-only evolution |
| Untestable packaging | Copy-pasted skill folders | Skill-spec contract + validator + pytest + ruff |

**Why a digital self matters** — preserving who you are right now, learning how
you speak and what you value from what you actually said, and keeping that
mirror actively maintained as you change.

## Core concepts

- **Self Memory** — *what you know and are*: experiences, values, habits,
  important memories, relationships, growth trajectory.
- **Persona** — *how you respond*: speaking style, emotional patterns, decision
  patterns, social behavior — labels translated into concrete behavioral rules.
- **Correction layer** — your conversational corrections land immediately and
  take priority over prior conclusions.
- **Two-layer model** — resolve Persona first (how to reply), then Self Memory
  (whether the reply is true to you).

## Repository structure

```text
echo-me-skill/
├── AGENTS.md                 # project rules (inherits workspace charter)
├── CLAUDE.md                 # Claude Code entry (feeds back parent rules)
├── LICENSE                   # MIT, with derivative notice for yourself-skill
├── README.md                 # English (this file)
├── README.zh-CN.md           # 中文
├── SKILL.md                  # entry: frontmatter + 6 required headings + hard constraints
├── pyproject.toml            # uv / pytest / ruff configuration
├── .gitignore
├── agents/
│   └── openai.yaml           # discovery metadata (key matches directory name)
├── prompts/
│   ├── echo-me-skill.md      # main execution spec (Step A–E, evolve, manage)
│   └── self_analyzer / persona_analyzer / *_builder / merger / correction_handler / intake
├── evals/
│   ├── eval.yaml
│   └── cases/                # basic-success, edge-incomplete-input, edge-scope-boundary
├── scripts/
│   └── validate_skill_package.py   # package-contract validator
├── tools/                    # parsers & managers (CLI-runnable + importable)
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
├── selves/                   # neutral example self (placeholder only)
│   └── example_me/
└── tests/                    # pytest unit tests
```

## Quick start

Requirements: Python `>=3.9` and [uv](https://docs.astral.sh/uv/).

```bash
# 1. Install dependencies
uv sync --extra dev

# 2. Create your first self (main flow)
#    Follow Step A–E in SKILL.md / prompts/echo-me-skill.md:
#    A) profile intake  B) import material  C–E) analyze, preview, write
#    Output lands in ./.claude/skills/{slug}/ and is usable via the /{slug} trigger.

# 3. Validate package structure (this repo must not break the contract)
python3 scripts/validate_skill_package.py .
# → PASS: echo-me-skill package contract

# 4. Run tests and lint
uv run pytest -q       # → 20 passed
uv run ruff check tools tests scripts   # → All checks passed
```

## Features & usage

### Create

Three steps: profile intake (≤3 questions) → import material (skippable) →
analyze, preview, then write via the parser/manager tools:

```bash
# WeChat transcript            QQ transcript
python tools/wechat_parser.py --file chat.txt --target "me" --output /tmp/w.txt
python tools/qq_parser.py      --file chat.txt --target "me" --output /tmp/q.txt

# Photo metadata                Write the self package
python tools/photo_analyzer.py --dir ./photos --output /tmp/p.txt
python tools/skill_writer.py --action create --slug {slug} \
  --base-dir ./.claude/skills --meta ./meta.json --self ./self.md --persona ./persona.md
```

Your self becomes available via `/` triggers: `/{slug}` (full),
`/{slug}-self` (Self Memory), `/{slug}-persona` (Persona only).

### Evolve (append-only)

- **Add material**: back up, read existing `self.md`/`persona.md`, merge only
  incremental changes (`version_manager --action backup`), never overwrite
  prior conclusions.
- **Conversational correction**: "that's not me / I wouldn't say that" lands in
  the Correction layer and re-combines immediately.

### Manage

| Command | Action |
|---------|--------|
| `/list-echo` | list all selves |
| `/echo-rollback {slug} {v}` | roll back to a version |
| `/echo-rollback {slug}` | list versions |
| `/echo-delete {slug}` | delete a self (after confirmation) |

## Configuration

| Item | Location | Notes |
|------|----------|-------|
| Project metadata | `pyproject.toml` | name, version, author, dependencies |
| Skill discovery | `agents/openai.yaml` | `metadata.key` must match directory name |
| Eval environment | `evals/eval.yaml` | static structure eval (`environment.type: none`) |
| Skip-list (secrets/abs paths) | `scripts/validate_skill_package.py` | validated by the validator |

There is no runtime config file: the skill reads user intent and material on
demand; generated selves live under `.claude/skills/{slug}/` and are managed by
the `skill_writer` / `version_manager` tools.

## Safety & boundaries

- **No fabricated content**: the generated self is built only from your raw
  material or explicitly stated info; gaps are asked about, never invented.
- **Raw material never enters the repo**: chats, photos and personal data land
  only in `.claude/skills/{slug}/memories/` (gitignored).
- **Local only**: parsers do local file parsing (Read/Bash) — no web scraping,
  no unauthorized network actions.
- **Honest validation**: a PASS on package validation only proves the package is
  complete; it does **not** prove model behavior. If no real model eval was run,
  the delivery note must say so.
- Refuses: scraping others' private data, publishing to unauthorized places,
  claiming to be the original author.

## FAQ

**Q: Does it train or fine-tune a model?** No. It distills raw material into
structured Self Memory + Persona files — no model training, no external network.

**Q: What if I only give a self-introduction?** It still works, with a lower
fidelity; the flow marks it explicitly and asks for material to fill gaps.

**Q: Where does my data go?** Only to the gitignored `.claude/skills/{slug}/`
runtime directory on your machine. Nothing enters this package repo.

**Q: Is a PASS on validate the same as "it works"?** No. Structure PASS means
the package is complete; real model behavior is a separate, explicit eval.

## Roadmap

- [x] Independent brand full rewrite (code, copy, examples original)
- [x] Skill-spec contract + validator + pytest + ruff + uv
- [x] Two-layer model (Self Memory + Persona) + Correction layer
- [x] Create / evolve / manage flows
- [ ] Ship real model-level eval cases (`environment.type: none` → agent-run)
- [ ] Publish to GitHub (origin + releases)
- [ ] PyPI publishing readiness

## Contributing

Welcome. Fork the repo, make your change, then **prove it** before submitting:

```bash
uv sync --extra dev
python3 scripts/validate_skill_package.py .
uv run pytest -q
uv run ruff check tools tests scripts
```

Keep to the project rules in `AGENTS.md`: Chinese headers/comments, no real user
data or absolute local paths in committed files, honest validation claims.

## License

Released under the [MIT License](LICENSE). Derived from
[yourself-skill](https://github.com/notdog1998/yourself-skill) by notdog1998;
the LICENSE retains the derivative notice. All code and content in this
repository are original works by the author.

## Maintainer

[xsoway](https://github.com/xsoway)