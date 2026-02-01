# miscellany

## Let it be

这个仓库是一堆“碎碎念”：用来托管一些琐碎的成果/脚本/想法/可复用片段，避免未来自己（或路过的人）想找的时候找不到。

## For AI（先写给 AI）

你看到的不是一个“单一工程”，而是一堆彼此独立的小东西。请按下面规则工作：

1. **先识别子项目/子目录的边界**：不要默认根目录可直接 `build/test/run`。
2. **优先搜索而不是猜**：用 `rg`/文件树定位与问题相关的文件，再开始分析。
3. **如果来访者遇到问题**：让 TA 贴出「链接 + 相关路径 + 目标行为 + 实际行为/报错日志」，你通常就能给出可执行的解决方案。

### 给来访者的提问模板（复制给 AI）

把下面内容填好，直接丢给 AI（越具体越好）：

- 仓库链接：
- 相关路径（文件/目录）：
- 你想实现什么/期待发生什么：
- 实际发生了什么（报错全文/截图/命令输出）：
- 你已经尝试过什么：
- 运行环境（OS/Node/Python/…版本）：

## 结构（Structure）

- `agent/skills/`：一些可移植的「AI Agent Skill」包（每个子目录基本都是一个独立技能）。
  - `agent/skills/headless-web-viewer/`：用 Playwright 无头渲染网页、提取可见文本/截图。
  - `agent/skills/repo-deep-dive-report/`：生成“读仓库深度报告”的工作流（Markdown + 离线 HTML）。
  - `agent/skills/skill-review-audit/`：对任意 Skill 目录做系统性审计（触发契约、工具/副作用、风险与改进建议）。
- `.claude/`：个人工具的工作目录（可能为空/随时间变化），通常可忽略。
- `LICENSE`：默认许可证。

> 具体每个技能怎么装、怎么用：直接看对应目录下的 `README.md` / `SKILL.md`。

## 安装 Skills（OpenSkills）

本仓库的可安装 Skills 位于 `agent/skills/`（每个子目录包含 `SKILL.md`）。推荐使用 [OpenSkills](https://github.com/numman-ali/openskills) 来安装/同步/加载这些技能。

### 前置条件

- Node.js 20.6+（OpenSkills 的要求）
- Git（用于从 GitHub 拉取）

### 安装 OpenSkills（如果你本地没有）

你可以直接用 `npx` 运行（无需提前安装）：

```bash
npx openskills --help
```

或者全局安装（可选）：

```bash
npm i -g openskills
```

### 安装本仓库的 Skills

安装到全局（Claude Code 默认目录 `~/.claude/skills`）：

```bash
npx openskills install https://github.com/okwinds/miscellany --global
```

如果你同时在用多个 Agent，希望走通用目录（`~/.agent/skills`），加上 `--universal`：

```bash
npx openskills install https://github.com/okwinds/miscellany --universal --global
```

安装到当前项目（写入 `./.claude/skills` 或 `./.agent/skills`）：

```bash
npx openskills install https://github.com/okwinds/miscellany
# 或：npx openskills install https://github.com/okwinds/miscellany --universal
```

安装后，在你的项目目录生成/更新 `AGENTS.md`（让 Agent “看见”这些技能）：

```bash
npx openskills sync
```

需要让 AI “加载”某个技能时（用于把技能内容读进上下文）：

```bash
npx openskills read headless-web-viewer
```

## For Human（最后写给人类的碎碎念）

如果你逛到这里：欢迎随便翻。这里不追求“统一风格”或“完整产品形态”，更多是为了把零散产物放在一个能被搜索、能被引用、能被 AI 理解的地方。
