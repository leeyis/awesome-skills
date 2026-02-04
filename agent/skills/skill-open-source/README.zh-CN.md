# skill-open-source

把任意本地 skill 以可复用的方式发布到本仓库 `agent/skills` 下：复制目录、排除常见依赖/垃圾文件、生成中英文 README、规范化 `SKILL.md` 中的路径示例，并在覆盖更新时自动 bump 版本号；新增 skill 时同步更新仓库根目录 `README.md` 的技能清单。

## 包含内容

- `SKILL.md`
- `scripts/`（CLI 工具脚本）

## 用法

在仓库根目录执行：

```bash
python3 agent/skills/skill-open-source/scripts/publish_skill.py --help
```

发布本地 skill 到本仓库：

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

## 备注

- 本仓库要求每个发布出来的 `SKILL.md` 必须带 `version: MAJOR.MINOR.PATCH`（SemVer）。
- 覆盖更新一个已发布 skill 时必须 bump 版本号（默认 bump patch）。
- 新增 skill 时需要把它补到仓库根目录 `README.md` 的技能清单里（脚本可通过 `--update-repo-readme` 自动完成）。

