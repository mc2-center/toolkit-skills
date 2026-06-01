---
name: fix-issue
description: Fix a GitHub issue. Reads the issue, implements the fix, writes tests, and prepares a commit.
disable-model-invocation: true
argument-hint: "[issue-number]"
---

Fix GitHub issue #$ARGUMENTS.

## Steps

1. **Read the issue**
   ```bash
   gh issue view $ARGUMENTS
   ```
   Understand the reported behavior, expected behavior, and any reproduction steps.

2. **Explore the codebase**
   - Find the relevant files using Glob and Grep
   - Read the surrounding code to understand the context before making changes
   - Do not modify code you haven't read

3. **Implement the fix**
   - Make the minimal change required to address the issue
   - Do not refactor unrelated code, add features, or clean up surrounding areas
   - Prefer editing existing files over creating new ones

4. **Write or update tests**
   - Add a test that would have caught this bug (regression test)
   - Ensure existing tests still pass

5. **Verify the fix**
   - Run the relevant tests to confirm the fix works
   - Check that no other tests are broken

6. **Prepare a commit**
   - Stage the changed files
   - Use the `/commit` skill or write a commit message following Conventional Commits:
     `fix(<scope>): <short description>`
   - Reference the issue in the commit body: `Closes #$ARGUMENTS`

## Constraints

- Fix only what the issue describes — no scope creep
- Do not skip hooks or bypass safety checks
- If the fix requires architectural decisions, pause and discuss with the user before proceeding
