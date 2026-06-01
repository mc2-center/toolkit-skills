---
name: commit
description: Create a well-formatted git commit following Conventional Commits. Use when ready to commit staged or unstaged changes.
disable-model-invocation: true
argument-hint: "[optional message]"
---

Create a git commit for the current changes following the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Steps

1. Run `git status` to see what files have changed
2. Run `git diff` (and `git diff --staged`) to review the actual changes
3. Determine the appropriate commit type:
   - `feat`: a new feature
   - `fix`: a bug fix
   - `docs`: documentation only changes
   - `style`: formatting, missing semicolons, etc. (no logic change)
   - `refactor`: code change that neither fixes a bug nor adds a feature
   - `test`: adding or updating tests
   - `chore`: build process, dependency updates, tooling
   - `perf`: performance improvement
4. Stage all relevant files with `git add <files>` (prefer specific files over `git add -A`)
5. Write a commit message in this format:
   ```
   <type>(<optional scope>): <short summary in present tense, lowercase>

   <optional body: what and why, not how>

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
   ```
6. Create the commit using a HEREDOC to preserve formatting
7. Run `git status` to confirm success

## Rules

- Summary line must be 72 characters or fewer
- Use present tense ("add feature" not "added feature")
- Do NOT use `--no-verify` unless the user explicitly asks
- Do NOT force-push or amend published commits
- If a pre-commit hook fails, fix the issue and create a NEW commit — do not amend

$ARGUMENTS
