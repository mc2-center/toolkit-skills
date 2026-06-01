---
name: improve-repo
description: Fork a GitHub repository, make real engineering improvements (refactoring, tests, CI, docs fixes), measure the before/after sustainability score, and offer to open a PR. Use when someone provides a GitHub URL and wants the tool substantively improved, not just assessed.
disable-model-invocation: true
argument-hint: "<github-url>"
---

Improve the GitHub repository: $ARGUMENTS

Read the code, make real engineering improvements, write tests, and show a before/after sustainability score — all locally. **No fork, no push, no PR happens without explicit user approval.** The default is dry-run: clone read-only, commit locally, print the diff. Forking and pushing only happen if the user opts in at the end.

## Step 0 — Preamble and one upfront approval

Before doing anything else, print this preamble and **ask once for approval to run the whole local phase** so the user is not interrupted by a permission prompt at every file edit / bash call.

```
I'm about to engineer improvements to <repo-name>. Here's exactly what will happen, in order:

  Local-only phase (no remote side effects):
    1. Baseline scoring via /assess-repo (read-only; can take 1–15+ min on long-lived repos — see assess-repo Step 0 for details)
    2. Shallow-clone the repo into /tmp/<repo-name> (5–50 MB, deleted on reboot)
    3. Read the source to identify real engineering problems (no edits yet)
    4. Make minimal, targeted edits: deduplicate logic, fix imports, add input validation, add tests, add CI, fix doc examples
    5. Run the test suite locally to verify nothing broke
    6. Commit the changes on a new branch `engineering-improvements` (LOCAL ONLY — no push)
    7. Re-score the local clone for the before/after comparison
    8. Print the diff summary and the local clone path

  Remote phase (gated, off by default):
    - Only after I show you the summary will I ask whether to fork + push (Step 9a) and then whether to open a PR (Step 9b). You can decline either or both. Declining at 9a leaves nothing on your GitHub account.

Token cost: typically 5k–20k tokens depending on repo size. On a Claude Pro subscription this is invisible cost.

If you trust this skill, the smoothest run is to authorize the local phase once now. You can either:
  - Approve each tool call as it appears (default), or
  - Switch to permission mode `acceptEdits` via `/permission-mode acceptEdits` before I start, which auto-approves file edits but still gates risky bash. I'll still ask separately before any fork/push/PR.

Shall I proceed?
```

**Wait for explicit confirmation before any other step.** This is the only place `/improve-repo` blocks for approval during the local phase — once the user says yes, run Steps 1–8 in sequence with brief progress lines (one per step) and no other chatter.

After the user approves, immediately call `TodoWrite` with the eight local-phase steps as todos:

1. Baseline assessment via /assess-repo
2. Clone repo into /tmp
3. Read source to identify engineering problems
4. Apply minimal targeted fixes
5. Add tests and CI workflow
6. Run test suite
7. Commit locally (no push)
8. Re-score local clone

Mark each one `in_progress` when starting it and `completed` the moment it finishes — do not batch. This gives the user the live "Verifying reported bugs… (5m 10s · ↑ 7.6k tokens)" display with the checklist beneath, which is the primary progress UI for long runs. The plain-text `Step N/8:` lines are a fallback, not a replacement — emit both.

## Step 1 — Assess the current state

Print: `Step 1/8: baseline assessment…`

Run the full assessment first so you have a baseline score and know what's broken. Use the `/assess-repo $ARGUMENTS` skill (which is already optimized for quiet output and uses the `Write`-then-run pattern to avoid spurious permission prompts).

Capture from the assessment:
- Almanack pass rate (X / 11)
- JOSS-style pass rate (X / Y)
- The list of failing checks

Save the baseline scores — you'll need them for the before/after comparison at the end. Do not re-print the full report here; the user has already seen it from assess-repo.

## Step 2 — Clone read-only (no fork yet)

Print: `Step 2/8: cloning <repo-name>…`

Clone the upstream repo into a temp directory. **Do not fork at this stage** — forking is deferred until Step 9 after the user reviews the changes.

```bash
REPO_DIR=$(mktemp -d)/$(basename $ARGUMENTS .git)
git clone --depth 50 $ARGUMENTS $REPO_DIR
cd $REPO_DIR
git checkout -b engineering-improvements
```

Remember `$REPO_DIR` — you'll print it in the final report so the user can `cd` in and inspect the diff. Do not print clone progress or file listings.

## Step 3 — Read the code before touching anything

Read all source files — not just what exists, but what the code actually does:
- Entry points (`main.py`, `cli.py`, `__main__.py`, `app.py`, etc.)
- Core logic modules
- Any existing tests

**Do not make changes until you understand the code.** Flag any files you cannot read (binary, encrypted, etc.).

## Step 4 — Identify real engineering problems

Look for issues that affect correctness, maintainability, or usability. Prioritize:

### High value (fix these)
- **Duplicated logic** — the same block of code appearing 2+ times verbatim
- **Wildcard imports** (`from module import *`) — silent collision risk
- **Missing package structure** — no `__init__.py` when one is needed
- **Undeclared dependencies** — packages imported but absent from requirements
- **Hardcoded paths** — absolute paths to a specific machine embedded in code or docs
- **Missing `--output` / `--outdir` flag** — results silently written next to inputs
- **No input validation** at entry points (empty folders, missing files, etc.)

### Medium value (fix if straightforward)
- Dead code (commented-out blocks that add noise, not history)
- Inconsistent naming or style within a single file
- README examples that don't work (wrong flags, removed options, etc.)

### Do NOT touch
- Core algorithm logic — don't rewrite what you don't fully understand
- Performance optimizations unless you can verify correctness
- API-breaking changes to public functions unless the current API is clearly wrong

## Step 5 — Make the improvements

Apply the fixes identified in Step 4. Follow these rules:

- Read every file before editing it
- Make the minimal change that addresses each problem
- Prefer extracting to a shared module over duplicating a fix in multiple places
- After each group of related changes, run existing tests if any exist

For **tests**: write tests for the pure functions — those that take inputs and return outputs without I/O, network calls, or GPU/model dependencies. These can run in CI without special hardware.

For **CI**: add a GitHub Actions workflow that installs only the non-GPU dependencies and runs the tests. If the repo requires a model or data files to run at all, scope the CI to the model-free tests only and say so clearly in a comment.

For **docs**: fix any examples that contain hardcoded paths, obsolete flags, or references to internal systems. Replace with generic `/path/to/your/data` style paths.

## Step 6 — Verify

Print: `Step 6/8: running tests…`

Run the tests quietly (only show output on failure):
```bash
python -m pytest tests/ -q
```

If the suite passes, print one line: `Tests passing: X passed in Ys`. If it fails, surface the failure verbatim and stop — do not proceed with a broken test suite.

## Step 7 — Commit locally (do not push)

Stage specific files (not `git add -A`) and commit with a clear message:

```bash
git add <specific files>
git commit -m "$(cat <<'EOF'
refactor: <short summary of what changed>

- <bullet: what was extracted/fixed and why>
- <bullet: tests added and what they cover>
- <bullet: CI added>
- <bullet: other fixes>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

**Do not push.** The commit lives in the local clone only. Pushing happens in Step 9 if and only if the user opts in.

## Step 8 — Re-score

Print: `Step 8/8: re-scoring (this re-walks the commit history and can take as long as Step 1)…`

Re-run the almanack and JOSS checks on the **local** updated repo. Point almanack at `$REPO_DIR`, not a remote URL — nothing has been pushed yet. Use the `Write`-then-run pattern (a script file in `/tmp`, then `python3`), **not** inline `python3 -c "<heredoc>"` — the heredoc-with-braces pattern triggers a shell-expansion safety prompt for no good reason.

Capture the new Almanack pass rate, JOSS-style pass rate, and the diff vs. baseline. Do not print intermediate dicts.

## Step 9 — Report, then ask before any remote action

Print a summary:

```
## Engineering improvements: <repo-name>

### Local clone
$REPO_DIR  (commit: <short-sha> on branch engineering-improvements)
Review with: git -C $REPO_DIR diff main..engineering-improvements

### Changes made
- <bullet list of what was changed and why>

### Score delta
| Metric            | Before | After |
|---|---|---|
| Weighted almanack | X.XX   | X.XX  |
| JOSS criteria     | X.XX   | X.XX  |
| Composite         | X.XX   | X.XX  |

Grade: <before> → <after>

### Remaining gaps (not addressed)
- <things that require the original authors, e.g. DOI registration, CITATION.cff>

### Tests
- X tests added, all passing
- CI runs without GPU/model weights

### State
- Local commit only. No fork created. No branch pushed. No PR opened.
```

Then ask, as two separate decisions:

> **Step 9a:** The changes are committed locally at `$REPO_DIR`. Would you like me to fork the upstream repo to your GitHub account and push this branch? (yes / no)

Wait for explicit confirmation. If **no**, stop here — the user has a local clone they can inspect, modify, or discard, and nothing has touched their GitHub account or the upstream repo.

If **yes**, fork and push:

```bash
gh repo fork <upstream-url> --remote=true --remote-name=fork
git push -u fork engineering-improvements
```

Then ask:

> **Step 9b:** Branch pushed to your fork. Would you like me to open a PR to the upstream repo? I'll draft the PR description from the changes above. (yes / no)

Wait for explicit confirmation before opening a PR. Then:

- **If the GitHub MCP server is available**: use `create_pull_request` — more reliable and doesn't require `gh` CLI auth.
- **Otherwise**: use `gh pr create` with a HEREDOC body.

In either case: `--base main`, head is `<your-fork>:engineering-improvements`.

## Constraints

- **Never fork, push, or open a PR without explicit user approval at each stage.** The default end-state is a local commit only.
- Never modify core algorithm logic
- Never `git add -A` or `git add .` — always stage specific files
- If the repo has no tests at all and the code is too entangled to test modularly, say so and explain what would need to change first
- If a fix requires understanding domain-specific science (e.g. a bioinformatics algorithm), pause and ask the user rather than guessing
