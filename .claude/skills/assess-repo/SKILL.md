---
name: assess-repo
description: Assess any GitHub repository's software sustainability with Software Gardening Almanack metrics, JOSS-style criteria, and a prioritized action plan ordered by ease-of-fix and empirical importance from a 4,431-tool regression. Use when a user provides a GitHub URL and asks how sustainable, well-engineered, or citable a research tool is, or how to improve it. Delegates the work to the sustainability-assessor subagent so intermediate Almanack output stays out of the main context.
argument-hint: "<github-url>"
allowed-tools: Read, Bash, Write, Task, TodoWrite
---

Assess the sustainability of the GitHub repository: $ARGUMENTS

This skill is a thin wrapper: it shows the user what is about to happen, sets up a live progress checklist, and delegates the actual work to the `sustainability-assessor` subagent. The subagent has its own context window, so the multi-thousand-token intermediate Almanack output never enters the main conversation.

## Step 0 — Preamble

Parse the repo name from `$ARGUMENTS` (the part after the last slash, minus any `.git` suffix). Then print, verbatim, substituting the repo name:

```
I'm about to assess <repo-name>. This will:
  - run a fast MCP-first preflight against GitHub (no clone needed for the JOSS-style file checks)
  - run the Software Gardening Almanack across the commit history. The Almanack walks every commit, so wall-clock time scales with history size: ~1 min on small repos, ~5 min on medium, 10–15+ min on large or long-lived repos (e.g. pycytominer at ~900 commits took ~12 min). There is no shortcut for accurate metrics.
  - check JOSS-style artifacts (paper, tests, CI, manifest)
  - write a markdown report to /tmp/<repo-name>_sustainability_report.md

No fork. No push. No PR. Read-only.

The Almanack run happens inside a subagent so the intermediate output stays out of this conversation — you will see progress checkmarks and the final report, nothing else.

Proceeding…
```

Do not wait for confirmation. `/assess-repo` is read-only by design.

## Step 1 — Live progress checklist

Immediately call `TodoWrite` with these four todos:

1. Preflight via GitHub MCP (file existence checks)
2. Run Almanack across commit history (slow on large repos)
3. Build prioritized action plan
4. Return report to main conversation

Mark each one `in_progress` when starting and `completed` the moment it finishes. The checklist + elapsed-time + token counter is the primary progress UI; do not emit verbose status lines on top of it.

## Step 2 — Delegate to the subagent

Use the `Task` (Agent) tool to invoke the `sustainability-assessor` subagent. Pass exactly:

- `subagent_type`: `sustainability-assessor`
- `description`: `Assess <repo-name> sustainability`
- `prompt`: The GitHub URL from `$ARGUMENTS`, followed by one line: `Return the full markdown report as your final message. Save it to /tmp/<repo-name>_sustainability_report.md.`

The subagent does the work in its own context. Its final message will be the full markdown report. Update the TodoWrite items as the phases complete (the subagent does not have access to your TodoWrite — you update it based on the subagent's progress signal lines, or just mark all four complete when it returns).

## Step 3 — Display the report

When the subagent returns, the main-context-visible output is its final message. Print it as-is. Add one line at the end:

```
Saved to /tmp/<repo-name>_sustainability_report.md
```

Do not summarize the report, do not editorialize, do not re-run any checks. The subagent is authoritative.

## Failure modes

- **Subagent returns an error**: surface it verbatim. The most common cause is a private repo without a `GITHUB_TOKEN`; the second is a non-GitHub URL.
- **MCP unavailable**: the subagent falls back to a shallow clone for the JOSS-style checks. The Almanack still runs the same way. The user does not need to do anything.
- **Almanack times out or crashes**: surface the error; do not fabricate metrics.

## What this skill does NOT do

- Does not fork. Does not push. Does not open a PR. Does not modify the upstream repo in any way.
- Does not score or weight composite metrics. The pass rates and per-check empirical-importance values are the only numbers shown.
- Does not compute new SHAP weights. The empirical-importance numbers come from a frozen analysis (manuscript §4.3, n=4,431). To recompute, see `cckp-toolkit-workflow/bin/stars_shap_model.py`.

For background on the check IDs, ease-of-fix tiers, and SHAP weights, see [reference/cct-spec.json](reference/cct-spec.json).
