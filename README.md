# toolkit-skills

A collection of [Claude Code skills](https://code.claude.com/docs/en/skills) for research software development workflows, with a focus on [MC2 Center](https://github.com/mc2-center) tooling and the [Software Gardening Almanack](https://github.com/software-gardening/almanack).

## Skills

Skills live in [`.claude/skills/`](.claude/skills/) and are available in any Claude Code session run from this repo. You can also copy them to `~/.claude/skills/` to use them across all your projects.

### General dev workflow

| Skill | Description | Invocation |
|---|---|---|
| [`commit`](.claude/skills/commit/SKILL.md) | Create Conventional Commits from staged/unstaged changes | `/commit` |
| [`review-pr`](.claude/skills/review-pr/SKILL.md) | Review a pull request for correctness, security, and test coverage | `/review-pr <pr-number>` |
| [`fix-issue`](.claude/skills/fix-issue/SKILL.md) | Fix a GitHub issue end-to-end (read → implement → test → commit) | `/fix-issue <issue-number>` |

### Research software quality

| Skill | Description | Invocation |
|---|---|---|
| [`assess-repo`](.claude/skills/assess-repo/SKILL.md) | Full sustainability report for any GitHub repo — almanack + JOSS + weighted score + prioritized action items | `/assess-repo <github-url>` or automatic |
| [`improve-repo`](.claude/skills/improve-repo/SKILL.md) | Fork a repo, make real engineering improvements (refactoring, tests, CI, docs), show before/after score, and offer to open a PR | `/improve-repo <github-url>` |
| [`almanack-check`](.claude/skills/almanack-check/SKILL.md) | Run a Software Gardening Almanack sustainability assessment | `/almanack-check <repo>` or automatic |
| [`joss-review`](.claude/skills/joss-review/SKILL.md) | Assess a repository against JOSS submission criteria | `/joss-review <repo>` or automatic |
| [`notebook-review`](.claude/skills/notebook-review/SKILL.md) | Review a Jupyter notebook for reproducibility and clarity | `/notebook-review <path>` or automatic |

### CCKP benchmark analysis (for the Bioinformatics paper)

These skills operate on the local `~/cckp-toolkit-workflow/` dataset (956 tools across 10 bioinformatics domains).

| Skill | Description | Invocation |
|---|---|---|
| [`almanack-weights`](.claude/skills/almanack-weights/SKILL.md) | Compute weighted almanack scores using nf-core as gold standard; produces sensitivity analysis for paper | `/almanack-weights [output-dir]` or automatic |
| [`software-deadness`](.claude/skills/software-deadness/SKILL.md) | Analyze "dead" software (no commits 2+ years); alive vs dead score comparison, longevity predictors | `/software-deadness [output-dir]` or automatic |
| [`domain-distribution`](.claude/skills/domain-distribution/SKILL.md) | Star-filtered (≥5) within-domain distribution analysis; tests the 0.1 score threshold hypothesis | `/domain-distribution [min-stars] [output-dir]` or automatic |

## Usage

**Invoke a skill directly** using its slash command:

```
/almanack-check https://github.com/mc2-center/cckp-toolkit-workflow
/joss-review ./my-research-tool
/commit
```

**Let Claude invoke skills automatically** — skills with no `disable-model-invocation` set will be loaded by Claude when relevant. For example, if you ask "does this repo meet JOSS standards?", Claude will use the `joss-review` skill automatically.

Skills marked with `disable-model-invocation: true` (like `/commit`, `/review-pr`, `/fix-issue`) only run when you explicitly invoke them — they have side effects you should control.

## Installation

### As a plugin

If Claude Code supports your plugin directory, install directly from GitHub:

```bash
/plugin install toolkit-skills@aditigopalan
```

Or clone and reference locally:

```bash
claude --plugin-dir ./toolkit-skills
```

### Manual (copy skills to your home directory)

```bash
cp -r .claude/skills/* ~/.claude/skills/
```

### GitHub MCP server (recommended)

The skills work better with the GitHub MCP server — `assess-repo` can check files without cloning, `improve-repo` can create PRs via the API, and `review-pr` gets richer diff context.

The `.mcp.json` in this repo configures it automatically. You'll need a GitHub token:

```bash
export GITHUB_TOKEN=ghp_...
npx -y @modelcontextprotocol/server-github  # installs the server
```

## Related projects

- [mc2-center/cckp-toolkit-workflow](https://github.com/mc2-center/cckp-toolkit-workflow) — Nextflow pipeline for batch repository quality assessment
- [software-gardening/almanack](https://github.com/software-gardening/almanack) — Python package and handbook for sustainable software development
