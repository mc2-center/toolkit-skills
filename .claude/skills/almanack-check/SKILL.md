---
name: almanack-check
description: Run a Software Gardening Almanack sustainability assessment on a repository. Use when asked to evaluate a repo's health, sustainability, or software quality metrics.
argument-hint: "[repo-url-or-path]"
---

Run a Software Gardening Almanack assessment on: $ARGUMENTS

The [Almanack](https://github.com/software-gardening/almanack) is a tool that evaluates repository sustainability and software quality. This skill runs it and interprets the results.

## Steps

1. **Check if almanack is installed**
   ```bash
   python -m almanack --version 2>/dev/null || pip install almanack
   ```

2. **Run the assessment**
   For a local repo:
   ```bash
   python -m almanack $ARGUMENTS
   ```
   For a GitHub URL, almanack accepts it directly.

3. **Interpret the results**
   Review the generated metrics across these dimensions:

   ### Community & Documentation
   - README present and informative?
   - CONTRIBUTING guide present?
   - Code of Conduct present?
   - License clearly defined?
   - Issue/PR templates present?

   ### Software Engineering
   - Tests present and structured?
   - CI/CD pipeline configured?
   - Dependencies declared (requirements.txt, pyproject.toml, etc.)?
   - Semantic versioning used?

   ### Sustainability signals
   - Recent commit activity?
   - Open issues being responded to?
   - Multiple contributors?
   - Changelog maintained?

4. **Produce a summary report**

   | Dimension | Status | Score | Notes |
   |---|---|---|---|
   | Documentation | ... | ... | ... |
   | Testing | ... | ... | ... |
   | CI/CD | ... | ... | ... |
   | Community | ... | ... | ... |
   | Sustainability | ... | ... | ... |

   Include:
   - **Top 3 strengths** of the repository
   - **Top 3 actionable improvements** (most impactful first)
   - **Overall sustainability grade** (A–F or numeric if almanack provides one)

## Notes

- If the target is a GitHub URL, ensure network access is available
- For large repos, the analysis may take a minute
- Results can be saved with `python -m almanack $ARGUMENTS --output results.json`
