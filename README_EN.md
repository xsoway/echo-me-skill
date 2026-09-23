# echo-me-skill

> Distill yourself into a runnable digital self.

echo-me-skill is a Skill package built to the
skill-spec 工程契约 engineering contract. It
decomposes your **chat history, diaries and photos** — plus your own description
of yourself — into a two-layer model, **Self Memory** + **Persona**, and produces
a digital mirror that thinks and speaks the way you do.

It is an **independent, fully rewritten** brand built on the open-source
`create-yourself` project (derived from
[yourself-skill](https://github.com/notdog1998/yourself-skill)). Function
ideas are preserved; code, copy and examples are original.

---

## What it does

- **Create**: a three-step flow (profile intake → material import → generate &
  write) yields a self Skill usable via the `/slug` trigger.
- **Evolve**: keep updating with new chats/diaries/photos; conversational
  corrections land in the Correction layer immediately.
- **Manage**: `/list-echo`, `/echo-rollback`, `/echo-delete`.
- **Engineering**: pytest unit tests, ruff static checks, `uv` dependency
  management, and a package-contract validator.

## Quick start

```bash
# 1. Install deps (python>=3.9, requires uv)
uv sync --extra dev

# 2. Create your first self (main flow)
#    Follow Step A–E in SKILL.md / prompts/echo-me-skill.md

# 3. Validate package structure (this repo must not break the contract)
python3 scripts/validate_skill_package.py .

# 4. Run tests and lint
uv run pytest -q
uv run ruff check tools tests scripts
```

## Docs

| Doc | Purpose |
|-----|---------|
| [SKILL.md](SKILL.md) | Entry: routing + hard constraints (6 required headings) |
| [prompts/echo-me-skill.md](prompts/echo-me-skill.md) | Main execution spec |
| [references/package-contract.md](references/package-contract.md) | Package contract |
| [references/skill-up-integration.md](references/skill-up-integration.md) | Eval integration & honesty boundary |
| [docs/PRD.md](docs/PRD.md) | Product requirements (Chinese) |

## License & compliance

- Released under the MIT License.
- Derived from [yourself-skill](https://github.com/notdog1998/yourself-skill) by
  notdog1998; the LICENSE retains the derivative notice.
- **Important**: replace the `<YOUR_NAME>` placeholder in `LICENSE` and
  `agents/openai.yaml` with your real name or GitHub username **before publishing**.

## Safety & boundaries

- Raw material (chats, photos, personal info) only lands in
  `.claude/skills/{slug}/memories/` (gitignored) — never in this package repo.
- Generated self content is based only on your material or stated info; the
  persona never fabricates experience, relationships or values.
- A PASS on structure validation only proves packaging; if no real model eval
  was run, the delivery note must say so.