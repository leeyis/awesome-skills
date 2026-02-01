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

### 风险提示（使用 Skills 前必读）

Skills 本质上是一段“可执行的工作流/提示词 + 脚本/工具调用约定”。它们可能会触发（或引导你触发）诸如：运行命令、读写文件、联网请求、安装依赖、抓取第三方内容等行为。

使用任何 Skill（包括本仓库的）前，请默认它是**不可信输入**，并遵循以下安全原则：

1. **先审计再使用**：阅读 `SKILL.md`，检查 `scripts/`、`references/`、`assets/` 等目录（如果存在），确认具体会用哪些工具、执行哪些命令、访问哪些外部资源/域名、以及可能产生的副作用（写盘/删改文件/网络请求等）。
2. **防提示词注入/工具注入（Prompt/Tool Injection）**：Skill 内容或它抓取的网页/文档可能夹带“诱导指令”，让你执行危险命令、扩大权限、泄露密钥、修改敏感文件。对 AI 生成的命令/补丁/脚本**逐行复核**，不要“复制粘贴就跑”。
3. **最小权限 + 隔离运行**：优先在容器/沙盒/低权限账号里验证；对涉及网络、写文件、执行命令的 Skill，建立明确的允许清单（allowlist）；不要在含生产凭据/真实数据的环境里直接运行。
4. **保护秘密与隐私**：不要把 token、cookie、私钥、内部链接、用户数据等放进上下文或日志；必要时用假数据或环境变量注入，并确保不会被打印/上传到第三方服务。

如果你希望更系统地审计一个 Skill：可以先用 `agent/skills/skill-review-audit/` 对目标目录做审计，确认风险点与改进建议后再安装/启用。

以上仅覆盖常见风险点，不保证穷尽所有场景；请结合你的运行环境与数据敏感性自行评估。

当然，也欢迎你把这些技能当成“可复用素材库”随意取用：有问题提 Issue，想改进就直接 PR。

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
