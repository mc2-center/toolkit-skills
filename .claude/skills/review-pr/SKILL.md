---
name: review-pr
description: Review a pull request for correctness, style, security, and test coverage. Use when asked to review a PR or check someone's code changes.
disable-model-invocation: true
argument-hint: "[pr-number or branch]"
---

Review pull request $ARGUMENTS thoroughly.

## Steps

1. Fetch PR context.

   **If the GitHub MCP server is available**, use it for richer data:
   - `get_pull_request(owner, repo, pull_number)` — description, metadata, checks status
   - `get_pull_request_files(owner, repo, pull_number)` — per-file diffs with patch context
   - `get_pull_request_comments(owner, repo, pull_number)` — existing review comments
   - `get_pull_request_reviews(owner, repo, pull_number)` — prior reviewer decisions

   **Otherwise**, use the CLI:
   ```bash
   gh pr view $ARGUMENTS
   gh pr diff $ARGUMENTS
   gh pr view $ARGUMENTS --comments
   ```

2. Read any changed files in full if the diff is incomplete or hard to follow
3. Evaluate the changes across these dimensions:

### Correctness
- Does the code do what the PR description says?
- Are there off-by-one errors, null/undefined edge cases, or logic bugs?
- Are error paths handled properly?

### Security
- Any SQL injection, XSS, command injection, or path traversal risks?
- Are secrets or credentials ever hardcoded?
- Are user inputs validated at system boundaries?

### Tests
- Are new features covered by tests?
- Do tests actually assert meaningful behavior (not just that code runs)?
- Are edge cases tested?

### Code quality
- Is the code readable and consistent with the surrounding style?
- Are there unnecessary abstractions or over-engineered solutions?
- Is there dead code or commented-out blocks?

### Documentation
- Are public APIs, functions, or modules documented where necessary?
- Is the PR description clear about what changed and why?

## Output format

Write your review as structured markdown with sections for each dimension. For each issue, include:
- **Location**: file and line number
- **Severity**: `blocking` | `suggestion` | `nit`
- **Description**: what the issue is
- **Suggestion**: how to fix it (when applicable)

End with an overall recommendation: **Approve**, **Request Changes**, or **Comment**.
