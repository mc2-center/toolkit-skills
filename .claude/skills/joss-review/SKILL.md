---
name: joss-review
description: Assess a software repository against Journal of Open Source Software (JOSS) review criteria. Use when evaluating if a research tool is ready for JOSS submission or when doing a structured quality review.
argument-hint: "[repo-url-or-path]"
---

Assess whether the repository at $ARGUMENTS meets [JOSS review criteria](https://joss.readthedocs.io/en/latest/review_criteria.html).

JOSS is a peer-reviewed journal for research software. Its review criteria are a well-established baseline for research software quality.

## Review checklist

Work through each item and mark it as **Pass**, **Fail**, or **Partial** with brief notes.

### General software quality

- [ ] **Repository**: Is the software available in a public version-controlled repository?
- [ ] **License**: Is an OSI-approved license present (LICENSE file)?
- [ ] **Authorship**: Are authors and contributors identifiable (AUTHORS file, CITATION.cff, or CONTRIBUTORS)?
- [ ] **Version**: Is there evidence of a versioned release (tags, CHANGELOG, or version file)?

### Documentation

- [ ] **README**: Does the README clearly describe the software's purpose, target audience, and how to install/use it?
- [ ] **Installation instructions**: Are installation steps provided and tested?
- [ ] **Usage examples**: Are there usage examples (README, docs, or notebooks)?
- [ ] **API/function docs**: Are key functions and modules documented?
- [ ] **Statement of need**: Is there a clear explanation of why this software exists and who it serves?

### Functionality & testing

- [ ] **Tests present**: Is there a test suite (pytest, unittest, etc.)?
- [ ] **Tests pass**: Do the tests pass with the provided instructions?
- [ ] **CI**: Is there a CI configuration that runs tests automatically?
- [ ] **Core claims**: Does the software do what it says it does?

### Research context (JOSS-specific)

- [ ] **Paper draft**: Is there a `paper.md` with title, authors, affiliations, summary, and references?
- [ ] **Statement of need**: Does the paper explain the scientific/research problem being solved?
- [ ] **Comparison to related work**: Does the paper acknowledge similar tools and explain how this differs?
- [ ] **DOI/archive**: Is there a DOI or archived release (Zenodo, Figshare)?

## Output format

Produce a structured review:

```markdown
## JOSS Readiness Assessment: <repo name>

### Summary
<2-3 sentences overall assessment>

### Checklist Results

| Category | Item | Status | Notes |
|---|---|---|---|
| ... | ... | Pass/Fail/Partial | ... |

### Blocking issues (must fix before submission)
1. ...

### Recommended improvements
1. ...

### Overall readiness
- Ready for JOSS submission: Yes / Not yet
- Estimated effort to reach readiness: Low / Medium / High
```
