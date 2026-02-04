# skill-open-source

Open-source/publish any local skill into this repo under `agent/skills` with a repeatable workflow. Copies a skill folder, excludes vendored deps (node_modules, etc.), generates bilingual READMEs, normalizes paths inside `SKILL.md`, enforces per-skill semver versioning, and updates the repo root README when adding a new skill.

## What's included

- `SKILL.md`
- `scripts/` (CLI utilities)

## Usage

From repo root:

```bash
python3 agent/skills/skill-open-source/scripts/publish_skill.py --help
```

Publish a local skill into this repo:

```bash
python3 agent/skills/skill-open-source/scripts/publish_skill.py \
  --source ~/.claude/skills/<name> \
  --dest agent/skills/<name> \
  --overwrite \
  --write-readmes \
  --normalize-paths \
  --update-repo-readme \
  --bump patch
```

## Notes

- This repo requires `version: MAJOR.MINOR.PATCH` in each published `SKILL.md` front matter.
- If you overwrite an existing published skill, bump its version (default: patch).
- When you add a new skill under `agent/skills/`, update the repo root `README.md` (the script can do it via `--update-repo-readme`).

