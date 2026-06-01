---
name: almanack-weights
description: Compute a weighted almanack sustainability score using nf-core pipelines as a gold-standard reference. Use when asked about weighting almanack components, computing a better sustainability score, or using nf-core as a benchmark.
argument-hint: "[output-dir]"
---

Compute a weighted almanack sustainability score for the CCKP toolkit benchmark dataset.

## Context

The current `almanack_score` is an unweighted ratio: (checks passed) / (total checks).
The 11 contributing checks (from the almanack JSON files, `sustainability_correlation=1`) are:

| ID | Check name |
|---|---|
| SGA-GL-0001 | `repo-includes-readme` |
| SGA-GL-0002 | `repo-includes-contributing` |
| SGA-GL-0003 | `repo-includes-code-of-conduct` |
| SGA-GL-0004 | `repo-includes-license` |
| SGA-GL-0005 | `repo-is-citable` |
| SGA-GL-0006 | `repo-default-branch-not-master` |
| SGA-GL-0007 | `repo-includes-common-docs` |
| SGA-GL-0015 | `repo-uses-issues` |
| SGA-GL-0017 | `repo-pull-requests-enabled` |
| SGA-GL-0025 | `repo-doi-valid-format` |
| SGA-GL-0026 | `repo-doi-https-resolvable` |

The goal: weight these checks by their prevalence in high-quality nf-core pipelines,
so that checks that well-maintained tools reliably pass count for more.

## Data locations

- **S3 — all tools**: `s3://mc2-project-tower-bucket/cc_toolkit/struct_bio_output/` (authoritative source, ~956 tools)
- **S3 — nf-core only**: `s3://mc2-project-tower-bucket/cc_toolkit/nfcore_output/` (nf-core pipelines only)
- **Local sync target — all tools**: `~/cckp-toolkit-workflow/s3_results/all_tools/`
- **Local sync target — nf-core**: `~/cckp-toolkit-workflow/s3_results/nfcore/`
- **Aggregated data**: `~/cckp-toolkit-workflow/benchmark_analysis_combined/aggregated_data.csv`
- **nf-core repo list**: `~/cckp-toolkit-workflow/nf_core_repos.csv` (format: `https://github.com/nf-core/<name>.git`)
- **Output**: `$ARGUMENTS` or default to `~/cckp-toolkit-workflow/weighted_almanack/`

## Analysis steps

### Step 0 — Sync JSON files from S3

Check if the local sync directories already exist and are populated. If not (or if the user
wants fresh data), sync from S3. Only almanack JSON files are needed — skip the HTML files.

```bash
mkdir -p ~/cckp-toolkit-workflow/s3_results/all_tools
mkdir -p ~/cckp-toolkit-workflow/s3_results/nfcore

# Sync only almanack JSONs (skip ai_analysis HTML files)
aws s3 sync s3://mc2-project-tower-bucket/cc_toolkit/struct_bio_output/ \
    ~/cckp-toolkit-workflow/s3_results/all_tools/ \
    --exclude "*" --include "*_almanack_Results.json"

aws s3 sync s3://mc2-project-tower-bucket/cc_toolkit/nfcore_output/ \
    ~/cckp-toolkit-workflow/s3_results/nfcore/ \
    --exclude "*" --include "*_almanack_Results.json"
```

Report how many JSON files landed in each directory:
```bash
ls ~/cckp-toolkit-workflow/s3_results/all_tools/*_almanack_Results.json | wc -l
ls ~/cckp-toolkit-workflow/s3_results/nfcore/*_almanack_Results.json | wc -l
```

If `pandas` or `scikit-learn` are not installed, install them:
```bash
pip3 install pandas scikit-learn matplotlib seaborn
```

### Step 1 — Build the component matrix

Write a Python script that:
1. Scans all `*_almanack_Results.json` files
2. For each file, extracts the tool name (from filename: strip `_almanack_Results.json`) and the boolean result for each of the 11 checks
3. Handles `None` values as `False` (tool lacks GitHub API access or check not applicable)
4. Builds a DataFrame: rows = tools, columns = check names, values = True/False

```python
import json, glob, os, re
import pandas as pd

CHECK_IDS = {
    'SGA-GL-0001': 'readme', 'SGA-GL-0002': 'contributing',
    'SGA-GL-0003': 'code_of_conduct', 'SGA-GL-0004': 'license',
    'SGA-GL-0005': 'citable', 'SGA-GL-0006': 'branch_not_master',
    'SGA-GL-0007': 'common_docs', 'SGA-GL-0015': 'uses_issues',
    'SGA-GL-0017': 'prs_enabled', 'SGA-GL-0025': 'doi_valid',
    'SGA-GL-0026': 'doi_resolvable',
}

rows = []
for path in glob.glob(os.path.expanduser('~/cckp-toolkit-workflow/benchmark_results/**/*_almanack_Results.json'), recursive=True):
    tool = os.path.basename(path).replace('_almanack_Results.json', '')
    with open(path) as f:
        data = json.load(f)
    row = {'tool_name': tool}
    for item in data:
        if isinstance(item, dict) and item.get('id') in CHECK_IDS:
            row[CHECK_IDS[item['id']]] = bool(item.get('result')) if item.get('result') is not None else False
    if len(row) > 1:
        rows.append(row)

component_df = pd.DataFrame(rows)
```

### Step 2 — Identify nf-core tools

Parse `nf_core_repos.csv` to extract short tool names (`https://github.com/nf-core/ampliseq.git` → `ampliseq`).
Mark each tool in the component matrix as `is_nfcore = True/False`.

### Step 3 — Compute weights

Run **three weighting strategies** and compare:

**A. Pass-rate weights** (how often nf-core tools pass each check)
```python
nfcore_rows = component_df[component_df['is_nfcore']]
check_cols = list(CHECK_IDS.values())
weights_a = nfcore_rows[check_cols].mean()
weights_a = weights_a / weights_a.sum()  # normalize to sum=1
```

**B. Discriminative weights** (how much more likely nf-core tools are to pass vs everyone)
```python
overall_rate = component_df[check_cols].mean()
nfcore_rate = nfcore_rows[check_cols].mean()
weights_b = nfcore_rate / (overall_rate + 0.01)  # add epsilon to avoid div/0
weights_b = weights_b / weights_b.sum()
```

**C. Logistic regression weights** (predict nf-core membership from checks)
```python
from sklearn.linear_model import LogisticRegression
X = component_df[check_cols].fillna(False).astype(int)
y = component_df['is_nfcore'].astype(int)
lr = LogisticRegression(max_iter=1000)
lr.fit(X, y)
weights_c = pd.Series(lr.coef_[0], index=check_cols)
weights_c = weights_c.clip(lower=0)  # keep only positive contributions
weights_c = weights_c / weights_c.sum()
```

### Step 4 — Compute weighted scores

For each weighting strategy, compute:
```
weighted_score = sum(weight_i * check_i)  for each tool
```

Merge back with the main `aggregated_data.csv` (join on `tool_name`).

### Step 5 — Evaluate and compare

Produce these outputs:

1. **Weight comparison table**: side-by-side weights for all 3 strategies, sorted by strategy A
2. **Score correlation plot**: scatter of `almanack_score` vs `weighted_score_A` (and B, C)
3. **Rank change analysis**: which tools move up/down most under the new scoring?
   - Top 10 "underrated" tools (higher weighted rank than original)
   - Top 10 "overrated" tools (lower weighted rank than original)
4. **Domain impact**: does re-weighting change domain mean rankings? Box plots before/after.
5. **Saved CSV**: `weighted_almanack_scores.csv` with columns:
   `tool_name, domain, language, almanack_score, weighted_score_a, weighted_score_b, weighted_score_c, rank_original, rank_weighted_a`

### Step 6 — Summarize the formula

Write out the final weighted formula in the form:
```
weighted_score = 0.XX * readme + 0.XX * contributing + ... + 0.XX * doi_resolvable
```
for whichever strategy best separates known good tools (nf-core) from the rest.

## Important notes

- The entropy-related checks from the almanack are **not currently in the sustainability_correlation=1 set** — flag this for the paper
- `None` results (GitHub API-dependent checks) should be treated as `False`, but report how many tools have `None` for each check
- For the paper: Dave and Aditi are discussing weights — produce a sensitivity analysis showing how results change with different weight vectors
