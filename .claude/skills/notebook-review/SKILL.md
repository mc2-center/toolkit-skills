---
name: notebook-review
description: Review a Jupyter notebook for reproducibility, clarity, code quality, and scientific best practices.
argument-hint: "[notebook-path]"
---

Review the Jupyter notebook at: $ARGUMENTS

## Dimensions to evaluate

### Reproducibility
- Does the notebook have a clear execution order (cells run top to bottom without errors)?
- Are all dependencies listed (requirements.txt, environment.yml, or inline pip installs)?
- Are random seeds set where needed?
- Are file paths hardcoded to local machines (should use relative paths or config)?
- Are any external data sources documented and accessible?

### Code quality
- Are cells short and focused (one logical step per cell)?
- Is repeated logic extracted into functions?
- Are variable names descriptive?
- Is there dead code (unused variables, commented-out blocks)?

### Clarity and documentation
- Does the notebook have a title and introductory markdown cell explaining its purpose?
- Are major sections separated by markdown headers?
- Are non-obvious steps explained inline?
- Are plots labeled (title, axis labels, units)?
- Is the conclusion or key findings clearly stated at the end?

### Data handling
- Is raw data never overwritten?
- Are intermediate outputs saved so steps can be resumed?
- Are large data files referenced by path rather than embedded in the notebook?

### Output cleanliness
- Are notebook outputs cleared before committing to version control (to minimize diff noise)?
- Are any outputs that contain sensitive information (API keys, PII, patient data) present?

## Output format

Produce a structured review with:

1. **Summary**: 2–3 sentence overall assessment
2. **Issues** (table with columns: Cell #, Severity, Category, Description, Suggestion)
   - Severity: `blocking` | `suggestion` | `nit`
3. **Recommendations**: top 3 actionable improvements

Be specific — reference cell numbers and variable names when possible.
