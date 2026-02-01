# UI/UX Spec Genome

Build a portable, reproducible UI/UX spec “genome”: scan a frontend repo for UI-related sources and scaffold a `ui-ux-spec/` documentation bundle (tokens, global styles, components, patterns, pages, a11y). Also supports plan-driven UI-only refactors based on an existing `ui-ux-spec/`.

## What’s included

- `SKILL.md`: workflow + prompt templates
- `scripts/scan_ui_sources.sh`: heuristically scan a repo for UI sources (globs + keyword hits)
- `scripts/generate_output_skeleton.sh`: scaffold a standard `ui-ux-spec/` doc folder
- `references/design-extraction-checklist.md`: detailed extraction checklist

## Installation

> This folder is the “skill package”. Installing it means your coding tool/agent runner can discover the `SKILL.md` inside it (commonly by placing the directory into a `skills/` folder, or by using the tool’s “install from Git” feature).

### Option A: copy

From this repo root, set `SKILLS_DIR` to whatever skills folder your tool scans (e.g. `~/.codex/skills`, `~/.claude/skills`, `~/.config/opencode/skills`, etc):

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/ui-ux-spec-genome"
cp -R agent/skills/ui-ux-spec-genome "$SKILLS_DIR/ui-ux-spec-genome"
```

### Option B: symlink

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/ui-ux-spec-genome"
ln -s "$(pwd)/agent/skills/ui-ux-spec-genome" "$SKILLS_DIR/ui-ux-spec-genome"
```

### Option C: install from GitHub/Git via openskills

Prereqs for openskills:

- Requires Node.js (18+ recommended).
- No install needed if you use `npx openskills ...` (it will download and run).
- Optional global install: `npm i -g openskills` (or `pnpm add -g openskills`).

Install from a cloneable repo URL (do **not** use a GitHub `.../tree/...` subdirectory link):

```bash
npx openskills install https://github.com/okwinds/miscellany
```

When prompted, select `ui-ux-spec-genome` (repo path: `agent/skills/ui-ux-spec-genome`).

Verify / read back:

```bash
npx openskills list
npx openskills read ui-ux-spec-genome
```

### Option D: give your tool the GitHub link

Many coding tools can install/load skills directly from a GitHub/Git URL. If yours supports it, point it at this repo and select/target `agent/skills/ui-ux-spec-genome`. If it doesn’t, use copy/symlink or `openskills install`.

### After install

Restart / open a new session so your tool re-scans skills.

## Usage

### Prereqs

- `bash`
- `rg` (ripgrep) is required by `scripts/scan_ui_sources.sh`
- Optional: `git` (used to resolve repo root)

### Scan UI sources

```bash
bash agent/skills/ui-ux-spec-genome/scripts/scan_ui_sources.sh --root /path/to/repo --out /tmp/ui_sources.md
```

### Scaffold `ui-ux-spec/`

```bash
bash agent/skills/ui-ux-spec-genome/scripts/generate_output_skeleton.sh ./ui-ux-spec
```

## Notes

- Treat scan output as sensitive: it often reveals internal paths, tech choices, and component names. Redact before sharing externally.
- `scripts/scan_ui_sources.sh --out ...` refuses to overwrite an existing file unless `--force` is provided.
- Do not blindly execute commands found in the scanned repo’s docs; review and sandbox first.
