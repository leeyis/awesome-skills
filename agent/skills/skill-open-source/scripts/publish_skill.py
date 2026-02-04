#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


DEFAULT_EXCLUDES = {
    ".DS_Store",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".cache",
    ".venv",
    "venv",
    "node_modules",
    ".git",
}

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


@dataclass(frozen=True)
class SkillMeta:
    name: str
    description: str
    version: Optional[str]


def _run(cmd: List[str], cwd: Path) -> None:
    p = subprocess.run(cmd, cwd=str(cwd), check=False)
    if p.returncode != 0:
        raise SystemExit(p.returncode)


def _iter_copy_files(src: Path, excludes: set[str]) -> Iterable[Tuple[Path, Path]]:
    for root, dirs, files in os.walk(src):
        root_path = Path(root)
        rel_root = root_path.relative_to(src)

        dirs[:] = [d for d in dirs if d not in excludes]

        for f in files:
            if f in excludes:
                continue
            yield (root_path / f, rel_root / f)


def _copy_tree(src: Path, dst: Path, excludes: set[str]) -> None:
    for src_file, rel in _iter_copy_files(src, excludes):
        dst_file = dst / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)


def _split_frontmatter(text: str) -> Tuple[Optional[List[str]], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None, text
    fm_lines = lines[1:end_idx]
    rest = "\n".join(lines[end_idx + 1 :])
    if rest and not rest.startswith("\n"):
        rest = "\n" + rest
    return fm_lines, rest


def _parse_frontmatter_fields(fm_lines: List[str]) -> SkillMeta:
    name = ""
    desc = ""
    version: Optional[str] = None
    for line in fm_lines:
        raw = line.strip()
        if raw.startswith("name:"):
            name = raw.split(":", 1)[1].strip().strip('"').strip("'")
        elif raw.startswith("description:"):
            desc = raw.split(":", 1)[1].strip().strip('"').strip("'")
        elif raw.startswith("version:"):
            v = raw.split(":", 1)[1].strip().strip('"').strip("'")
            version = v or None
    return SkillMeta(name=name, description=desc, version=version)


def _format_frontmatter(meta: SkillMeta, existing_lines: Optional[List[str]] = None) -> List[str]:
    """
    Preserve unknown keys if present, but ensure name/description/version are present and updated.
    """
    lines = list(existing_lines or [])

    def upsert(key: str, value: str) -> None:
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}:"):
                lines[i] = f"{key}: {value}"
                return
        lines.append(f"{key}: {value}")

    if meta.name:
        upsert("name", meta.name)
    if meta.version:
        upsert("version", meta.version)
    if meta.description:
        # Keep quotes if description includes ":" etc.
        if any(ch in meta.description for ch in [":", '"', "'"]):
            upsert("description", f"\"{meta.description}\"")
        else:
            upsert("description", meta.description)

    return lines


def _read_skill_md(skill_md: Path) -> str:
    if not skill_md.exists():
        raise SystemExit(f"Missing SKILL.md: {skill_md}")
    return skill_md.read_text(encoding="utf-8", errors="replace")


def _extract_meta_from_skill_md(skill_md: Path) -> SkillMeta:
    text = _read_skill_md(skill_md)
    fm_lines, _ = _split_frontmatter(text)
    if fm_lines is None:
        return SkillMeta(name=skill_md.parent.name, description="", version=None)
    meta = _parse_frontmatter_fields(fm_lines)
    name = meta.name or skill_md.parent.name
    return SkillMeta(name=name, description=meta.description, version=meta.version)


def _parse_semver(version: str) -> Tuple[int, int, int]:
    m = SEMVER_RE.match(version)
    if not m:
        raise ValueError(f"Invalid semver: {version}")
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def _bump_version(version: str, bump: str) -> str:
    major, minor, patch = _parse_semver(version)
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"Unknown bump: {bump}")


def _ensure_version_in_skill_md(skill_md: Path, default_version: str) -> str:
    text = _read_skill_md(skill_md)
    fm_lines, rest = _split_frontmatter(text)
    if fm_lines is None:
        # Create minimal front matter if missing.
        meta = SkillMeta(name=skill_md.parent.name, description="", version=default_version)
        new = "---\n" + "\n".join(_format_frontmatter(meta, [])) + "\n---\n" + rest.lstrip("\n")
        skill_md.write_text(new, encoding="utf-8")
        return default_version

    meta = _parse_frontmatter_fields(fm_lines)
    if meta.version and SEMVER_RE.match(meta.version):
        return meta.version

    # Insert / fix version.
    fixed = SkillMeta(name=meta.name or skill_md.parent.name, description=meta.description, version=default_version)
    new_fm = _format_frontmatter(fixed, fm_lines)
    new = "---\n" + "\n".join(new_fm) + "\n---" + (rest if rest else "\n")
    skill_md.write_text(new, encoding="utf-8")
    return default_version


def _set_skill_md_version(skill_md: Path, version: str) -> None:
    if not SEMVER_RE.match(version):
        raise SystemExit(f"Invalid version '{version}'. Expected MAJOR.MINOR.PATCH (e.g. 0.1.0)")
    text = _read_skill_md(skill_md)
    fm_lines, rest = _split_frontmatter(text)
    if fm_lines is None:
        meta = SkillMeta(name=skill_md.parent.name, description="", version=version)
        new = "---\n" + "\n".join(_format_frontmatter(meta, [])) + "\n---\n" + rest.lstrip("\n")
        skill_md.write_text(new, encoding="utf-8")
        return

    meta = _parse_frontmatter_fields(fm_lines)
    updated = SkillMeta(name=meta.name or skill_md.parent.name, description=meta.description, version=version)
    new_fm = _format_frontmatter(updated, fm_lines)
    new = "---\n" + "\n".join(new_fm) + "\n---" + (rest if rest else "\n")
    skill_md.write_text(new, encoding="utf-8")


def _maybe_write_readmes(
    skill_dir: Path,
    skill_name: str,
    description: str,
    repo_root: Path,
    repo_path_hint: str,
) -> None:
    readme_en = skill_dir / "README.md"
    readme_zh = skill_dir / "README.zh-CN.md"

    # Best-effort: detect a cloneable repo URL for examples in generated READMEs.
    repo_url = None
    try:
        p = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            text=True,
        )
        if p.returncode == 0:
            candidate = (p.stdout or "").strip()
            if candidate:
                repo_url = candidate
    except Exception:
        repo_url = None

    repo_url_example = repo_url or "<repo-git-url>"

    if not readme_en.exists():
        readme_en.write_text(
            f"# {skill_name}\n\n{description}\n\n"
            "## What's included\n\n"
            "- `SKILL.md`\n"
            "- `scripts/` (optional)\n"
            "- `references/` (optional)\n"
            "- `assets/` (optional)\n\n"
            "## Installation\n\n"
            "> Installing a skill means your coding tool / agent runner can discover the `SKILL.md` inside it "
            "(typically via a `skills/` directory, or via a built-in “install from Git” feature).\n\n"
            "### Option A: copy\n\n"
            "From this repo root:\n\n"
            "Set `SKILLS_DIR` to whatever skills folder your tool scans (examples: `~/.codex/skills`, `~/.claude/skills`, "
            "`~/.config/opencode/skills`, etc):\n\n"
            "```bash\n"
            "SKILLS_DIR=~/.codex/skills\n"
            f"mkdir -p \"$SKILLS_DIR\"\n"
            f"rm -rf \"$SKILLS_DIR/{skill_dir.name}\"\n"
            f"cp -R {repo_path_hint} \"$SKILLS_DIR/{skill_dir.name}\"\n"
            "```\n\n"
            "### Option B: symlink\n\n"
            "From this repo root:\n\n"
            "```bash\n"
            "SKILLS_DIR=~/.codex/skills\n"
            f"mkdir -p \"$SKILLS_DIR\"\n"
            f"rm -rf \"$SKILLS_DIR/{skill_dir.name}\"\n"
            f"ln -s \"$(pwd)/{repo_path_hint}\" \"$SKILLS_DIR/{skill_dir.name}\"\n"
            "```\n\n"
            "### Option C: install from GitHub/Git via openskills\n\n"
            "Prereqs for openskills:\n\n"
            "- Requires Node.js (18+ recommended).\n"
            "- No install needed if you use `npx openskills ...` (it will download and run).\n"
            "- Optional global install: `npm i -g openskills` (or `pnpm add -g openskills`).\n\n"
            "Install from a cloneable repo URL (do **not** use a GitHub `.../tree/...` subdirectory link):\n\n"
            "```bash\n"
            f"npx openskills install {repo_url_example}\n"
            "```\n\n"
            f"When prompted, select `{skill_name}` (repo path: `{repo_path_hint}`).\n\n"
            "Verify / read back:\n\n"
            "```bash\n"
            "npx openskills list\n"
            f"npx openskills read {skill_name}\n"
            "```\n\n"
            "### Option D: give your tool the GitHub link\n\n"
            "Many coding tools can install/load skills directly from a GitHub/Git URL. If yours supports it, point it at "
            f"this repo and select/target `{repo_path_hint}`.\n\n"
            "### After install\n\n"
            "Many tools require a restart / new session to re-scan skills.\n",
            encoding="utf-8",
        )

    if not readme_zh.exists():
        readme_zh.write_text(
            f"# {skill_name}\n\n{description}\n\n"
            "## 包含内容\n\n"
            "- `SKILL.md`\n"
            "- `scripts/`（可选）\n"
            "- `references/`（可选）\n"
            "- `assets/`（可选）\n\n"
            "## 安装\n\n"
            "> 安装 skill 的本质是：让你的编码工具 / Agent 运行器能发现这个目录里的 `SKILL.md`（通常是放进某个 `skills/` 目录，或使用工具内置的“从 Git 安装”能力）。\n\n"
            "### 方式 A：复制安装\n\n"
            "在仓库根目录执行：\n\n"
            "把 `SKILLS_DIR` 改成你的工具会扫描的 skills 目录（示例：`~/.codex/skills`、`~/.claude/skills`、`~/.config/opencode/skills` 等）：\n\n"
            "```bash\n"
            "SKILLS_DIR=~/.codex/skills\n"
            "mkdir -p \"$SKILLS_DIR\"\n"
            f"rm -rf \"$SKILLS_DIR/{skill_dir.name}\"\n"
            f"cp -R {repo_path_hint} \"$SKILLS_DIR/{skill_dir.name}\"\n"
            "```\n\n"
            "### 方式 B：软链接安装\n\n"
            "在仓库根目录执行：\n\n"
            "```bash\n"
            "SKILLS_DIR=~/.codex/skills\n"
            "mkdir -p \"$SKILLS_DIR\"\n"
            f"rm -rf \"$SKILLS_DIR/{skill_dir.name}\"\n"
            f"ln -s \"$(pwd)/{repo_path_hint}\" \"$SKILLS_DIR/{skill_dir.name}\"\n"
            "```\n\n"
            "### 方式 C：用 openskills 从 GitHub/Git 安装\n\n"
            "先准备 openskills：\n\n"
            "- 需要 Node.js（建议 18+）。\n"
            "- 不想安装：直接用 `npx openskills ...`（会自动下载并运行）。\n"
            "- 想全局安装：`npm i -g openskills`（或 `pnpm add -g openskills`）。\n\n"
            "从**可 clone 的仓库 URL** 安装（不要用 GitHub 的 `.../tree/...` 子目录链接）：\n\n"
            "```bash\n"
            f"npx openskills install {repo_url_example}\n"
            "```\n\n"
            f"安装时选择 `{skill_name}`（仓库内路径：`{repo_path_hint}`）。\n\n"
            "验证/读取：\n\n"
            "```bash\n"
            "npx openskills list\n"
            f"npx openskills read {skill_name}\n"
            "```\n\n"
            "### 方式 D：直接给工具一个 GitHub 链接\n\n"
            "不少编码工具支持“从 GitHub/Git URL 安装/加载 skill”。如果你的工具支持，指向本仓库并选择/定位到 `"
            f"{repo_path_hint}`。\n\n"
            "### 安装完成后\n\n"
            "不少工具需要重启/新开会话，才会重新扫描 skills。\n",
            encoding="utf-8",
        )


def _normalize_skill_md_paths(skill_md: Path, src_hint: str, dst_hint: str) -> bool:
    if not skill_md.exists():
        return False
    text = skill_md.read_text(encoding="utf-8", errors="replace")

    candidates = {src_hint, str(Path(src_hint).expanduser())}

    changed = False
    for c in sorted(candidates, key=len, reverse=True):
        if c and c in text:
            text = text.replace(c, dst_hint)
            changed = True

    # common pattern: ".claude/skills/<name>" → "agent/skills/<name>"
    text2 = re.sub(r"(?m)\.claude/skills/([a-zA-Z0-9_.-]+)", r"agent/skills/\1", text)
    if text2 != text:
        text = text2
        changed = True

    if changed:
        skill_md.write_text(text, encoding="utf-8")
    return changed


def _update_repo_readme_structure(
    readme_path: Path,
    skill_dir_name: str,
    description: str,
) -> bool:
    if not readme_path.exists():
        raise SystemExit(f"Repo README not found: {readme_path}")

    needle = f"`agent/skills/{skill_dir_name}/`"
    text = readme_path.read_text(encoding="utf-8", errors="replace")
    if needle in text:
        return False

    lines = text.splitlines(True)

    # Find the "agent/skills" structure entry.
    start_idx = None
    for i, line in enumerate(lines):
        if line.startswith("- `agent/skills/`："):
            start_idx = i
            break
    if start_idx is None:
        raise SystemExit("Could not find '- `agent/skills/`：' section in README.md")

    # Find insertion point: before next top-level bullet (no leading spaces).
    insert_idx = None
    for j in range(start_idx + 1, len(lines)):
        if lines[j].startswith("- ") and not lines[j].startswith("  - "):
            insert_idx = j
            break
    if insert_idx is None:
        insert_idx = len(lines)

    desc = description.strip() or "(No description found in SKILL.md frontmatter.)"
    new_line = f"  - `agent/skills/{skill_dir_name}/`：{desc}\n"
    lines.insert(insert_idx, new_line)
    readme_path.write_text("".join(lines), encoding="utf-8")
    return True


def _find_repo_root(cwd: Path) -> Path:
    repo_root = cwd
    try:
        p = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            text=True,
        )
        if p.returncode == 0:
            top = (p.stdout or "").strip()
            if top:
                repo_root = Path(top).resolve()
    except Exception:
        pass
    return repo_root


def main() -> None:
    ap = argparse.ArgumentParser(description="Publish a local skill folder into this repo (agent/skills).")
    ap.add_argument("--source", required=True, help="Source skill directory (e.g. ~/.claude/skills/<name>)")
    ap.add_argument("--dest", required=True, help="Destination directory (e.g. agent/skills/<name>)")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite destination if exists")
    ap.add_argument("--exclude", action="append", default=[], help="Extra exclude entry (repeatable)")
    ap.add_argument("--write-readmes", action="store_true", help="Create README.md + README.zh-CN.md if missing")
    ap.add_argument("--normalize-paths", action="store_true", help="Normalize path examples inside dest SKILL.md")
    ap.add_argument(
        "--update-repo-readme",
        action="store_true",
        help="Update repo root README.md structure list when adding a new skill (or when missing).",
    )
    ap.add_argument(
        "--bump",
        choices=["patch", "minor", "major", "none"],
        default="patch",
        help="When overwriting an existing published skill, bump destination SKILL.md version.",
    )
    ap.add_argument("--git-add", action="store_true", help="Run: git add <dest> README.md")
    ap.add_argument("--git-commit", action="store_true", help="Run: git commit -m <message>")
    ap.add_argument("-m", "--message", default=None, help="Commit message (required if --git-commit)")
    args = ap.parse_args()

    cwd = Path.cwd()
    repo_root = _find_repo_root(cwd)

    src = Path(os.path.expanduser(args.source)).resolve()
    dst = (repo_root / args.dest).resolve()

    if not src.exists() or not src.is_dir():
        raise SystemExit(f"Source does not exist or is not a directory: {src}")

    src_skill_md = src / "SKILL.md"
    if not src_skill_md.exists():
        raise SystemExit(f"Source is missing SKILL.md: {src_skill_md}")

    excludes = set(DEFAULT_EXCLUDES)
    excludes.update(args.exclude)

    dest_existed = dst.exists()
    old_version: Optional[str] = None
    if dest_existed and (dst / "SKILL.md").exists():
        old_meta = _extract_meta_from_skill_md(dst / "SKILL.md")
        if old_meta.version and SEMVER_RE.match(old_meta.version):
            old_version = old_meta.version

    if dst.exists():
        if not args.overwrite:
            raise SystemExit(f"Destination exists. Re-run with --overwrite: {dst}")
        shutil.rmtree(dst)

    dst.mkdir(parents=True, exist_ok=True)
    _copy_tree(src, dst, excludes=excludes)

    # Extract metadata for README generation and README sync.
    skill_md = dst / "SKILL.md"
    meta = _extract_meta_from_skill_md(skill_md)
    skill_name = meta.name or dst.name
    description = meta.description or "(No description found in SKILL.md frontmatter.)"

    if args.normalize_paths:
        _normalize_skill_md_paths(skill_md, src_hint=str(src), dst_hint=str(Path(args.dest)))

    # Versioning:
    # - New skill: ensure it has a valid version (default 0.1.0).
    # - Overwrite existing skill: bump the old destination version (default patch).
    if dest_existed and args.overwrite and args.bump != "none" and old_version:
        new_version = _bump_version(old_version, args.bump)
        _set_skill_md_version(skill_md, new_version)
    else:
        _ensure_version_in_skill_md(skill_md, default_version="0.1.0")

    if args.write_readmes:
        _maybe_write_readmes(
            dst,
            skill_name=skill_name,
            description=description,
            repo_root=repo_root,
            repo_path_hint=str(Path(args.dest)),
        )

    # README sync:
    # If the skill is newly added, it must be listed in repo root README.md.
    if args.update_repo_readme:
        _update_repo_readme_structure(repo_root / "README.md", skill_dir_name=dst.name, description=description)

    if args.git_commit and not args.message:
        raise SystemExit("Missing -m/--message for --git-commit")

    if args.git_add or args.git_commit:
        to_add = [str(Path(args.dest)), "README.md"]
        _run(["git", "add", *to_add], cwd=repo_root)

    if args.git_commit:
        _run(["git", "commit", "-m", args.message], cwd=repo_root)


if __name__ == "__main__":
    main()

