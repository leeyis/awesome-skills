---
name: skill-open-source
version: 0.1.0
description: Open-source/publish any local skill into this repo under agent/skills with a repeatable workflow. Copies a skill folder, excludes vendored deps (node_modules, etc.), generates bilingual READMEs, normalizes paths inside SKILL.md, enforces per-skill semver versioning, and updates the repo root README when adding a new skill.
---

# Skill Open Source（通用技能开源/发布流程）

目标：把任意一个本地 skill 以**可复用**的方式发布到当前仓库的 `agent/skills/<skill-name>/`，并补齐中英文 README，方便仓库内复用与开源分发。

## Quick Start

从仓库根目录执行（把 `<name>` 换成实际技能名）：

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

## What this skill does

- Copy a skill directory into `agent/skills/<name>` (keeping structure intact)
- Exclude common trash / vendored deps (e.g. `node_modules`, `.DS_Store`)
- Optionally generate bilingual READMEs (English + zh-CN)
- Optionally normalize path examples inside `SKILL.md` (e.g. `.claude/skills/<name>` → `agent/skills/<name>`)
- **Versioning (required by this repo)**:
  - Ensure `SKILL.md` has `version: MAJOR.MINOR.PATCH` in YAML front matter
  - When overwriting an existing published skill, bump its version (default: patch)
- **Repo README sync (required when adding a new skill)**:
  - When a new skill is added under `agent/skills/`, update the repo root `README.md` to list it in the “结构（Structure）” section

## Recommended workflow（推荐流程）

1) 选择源 skill 路径（例如 `~/.claude/skills/<name>`）
2) 运行 `publish_skill.py` 完成复制 + 清理 + README 生成 +（可选）路径规范化
3) **版本号检查（必须）**：
   - 新 skill：确保 `SKILL.md` front matter 中存在 `version`（脚本会补默认 `0.1.0`）
   - 更新 skill：确保版本号已 bump（脚本默认 bump patch；也可手动改）
4) **仓库 README 同步（新增 skill 必须）**：
   - 新增 skill 时，把它加入仓库根目录 `README.md` 的 `agent/skills/` 清单（脚本可 `--update-repo-readme` 自动做）
5) 本地快速自检（可选但推荐）：

```bash
python3 agent/skills/_tools/check_skill_versions.py --base HEAD --head WORKTREE
```

6) `git status` 确认变更后再提交

## Script: publish_skill.py

查看参数：

```bash
python3 agent/skills/skill-open-source/scripts/publish_skill.py --help
```

常用参数：

- `--source <path>`：源 skill 目录（必须）
- `--dest <path>`：目标目录（必须，通常是 `agent/skills/<name>`）
- `--overwrite`：覆盖已存在的目标目录
- `--write-readmes`：生成 `README.md` 与 `README.zh-CN.md`（如果不存在）
- `--normalize-paths`：尝试自动修正 `SKILL.md` 中的路径示例
- `--update-repo-readme`：新增 skill 时自动更新仓库根目录 `README.md`
- `--bump {patch,minor,major,none}`：当覆盖已存在 skill 时，对“目的地 skill”的版本号做 bump（默认 `patch`）
- `--git-add`：执行 `git add <dest> README.md`
- `--git-commit -m "<msg>"`：执行 `git commit -m ...`

## Notes / Pitfalls

- 本 skill 默认不会把 `node_modules` 之类依赖目录拷进仓库（排除列表可用 `--exclude` 扩展）。
- 版本号是“仓库内发布版本”，以 `agent/skills/<name>/SKILL.md` 的 `version` 为准（不强制与你本地 skill 的版本一致）。
- 自动更新 `README.md` 只做**最小可用**的清单插入；如果你希望更好的中文描述/分类位置，可在插入后手动润色。

