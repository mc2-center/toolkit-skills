---
name: domain-distribution
description: Analyze sustainability score distributions within and across bioinformatics domains, with optional GitHub star filtering. Use when asked about domain-specific patterns, within-domain variance, star-filtered analysis, or intra-domain differences.
argument-hint: "[min-stars] [output-dir]"
---

Analyze sustainability score distributions by domain in the CCKP benchmark dataset.

## Context

From the team discussion:
- Filter by stars (suggest ≥ 5 instead of 10) and look at distribution per domain
- Analyze **within-domain** differences (not just across domains)
- The 0.1 score difference is posited as an actionable sustainability threshold (Dave's suggestion)

## Data locations

- **Aggregated data**: `~/cckp-toolkit-workflow/benchmark_analysis_combined/aggregated_data.csv`
- **nf-core data**: `~/cckp-toolkit-workflow/benchmark_analysis_nfcore/aggregated_data.csv`
- **Output**: `$ARGUMENTS[1]` or default to `~/cckp-toolkit-workflow/domain_distribution/`
- **Min stars**: `$ARGUMENTS[0]` or default to `5`

## Analysis steps

### Step 1 — Fetch GitHub stars (if not already in dataset)

The current `aggregated_data.csv` does not include a `github_stars` column.
You need to fetch stars for each tool via the GitHub API.

The `tool_name` column contains the short repository name (not the full URL).
Check if a `stars` column already exists; if not, fetch it:

```python
import requests, time

def get_stars(tool_name, token=None):
    """Try to find the GitHub repo by searching. Falls back to 0 if not found."""
    headers = {'Authorization': f'token {token}'} if token else {}
    # Try direct lookup under common orgs first, then search
    for url in [
        f'https://api.github.com/repos/bioconda/{tool_name}',
        f'https://api.github.com/search/repositories?q={tool_name}+in:name&sort=stars&per_page=1',
    ]:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            if 'stargazers_count' in data:
                return data['stargazers_count']
            if 'items' in data and data['items']:
                return data['items'][0].get('stargazers_count', 0)
        time.sleep(0.5)
    return None
```

**Important**: Check if `~/cckp-toolkit-workflow/repo_scores.csv` or other files already have stars data before making API calls — avoid re-fetching unnecessarily. Look for any existing CSV with a `stars` or `stargazers_count` column.

### Step 2 — Filter by stars

```python
MIN_STARS = int('$ARGUMENTS[0]' or 5)
df_filtered = df[df['github_stars'] >= MIN_STARS] if 'github_stars' in df.columns else df
print(f"Kept {len(df_filtered)} / {len(df)} tools with ≥ {MIN_STARS} stars")
```

Report how many tools are dropped by domain when applying the filter.

### Step 3 — Within-domain distribution analysis

For each domain with n ≥ 10 tools:

```python
domains = df_filtered.groupby('domain').filter(lambda x: len(x) >= 10)['domain'].unique()

for domain in domains:
    subset = df_filtered[df_filtered['domain'] == domain]
    print(f"\n{domain} (n={len(subset)})")
    print(subset['almanack_score'].describe())

    # Identify top/bottom quartile tools within the domain
    q25 = subset['almanack_score'].quantile(0.25)
    q75 = subset['almanack_score'].quantile(0.75)
    top = subset[subset['almanack_score'] >= q75]
    bottom = subset[subset['almanack_score'] <= q25]

    # What separates them? Compare check pass rates
    # (requires merging with component matrix from almanack-weights)
```

### Step 4 — The 0.1 threshold test

Dave's hypothesis: a **0.1 difference in composite score** represents a meaningful sustainability gap.

Test this empirically:
1. Pair tools within the same domain that differ by 0.1 in score
2. Check whether they differ meaningfully in `check_readme`, `check_dependencies`, `check_tests`, `commits`, `days_of_development`
3. Run a permutation test: randomly assign the 0.1 gap many times and compare to observed differences
4. Plot: score distribution with 0.1 bands highlighted

### Step 5 — Intra-domain variance

Compute:
- Coefficient of Variation (CV = std/mean) per domain — high CV = more heterogeneous domain
- Interquartile range per domain
- Are some domains more internally uniform than others?

A high-CV domain (like RNA-seq) has very mixed tool quality — this is where targeted improvement has highest impact.

### Step 6 — Cross-domain pattern (star-filtered)

Re-run the original ANOVA and pairwise comparisons but only on star-filtered tools.
Does the Structural Biology advantage persist after filtering for impactful tools (≥5 stars)?

Compare:
- Domain means before/after star filter
- Whether the ANOVA p-value changes substantially

### Step 7 — Output

Produce:
1. `domain_distribution_stats.csv` — per-domain: n, mean, median, std, CV, IQR, star-filtered n
2. `domain_violin_plots.png` — violin plots by domain (unfiltered and star-filtered, side by side)
3. `within_domain_heatmap.png` — heatmap: domains × almanack checks, showing pass rates
4. `threshold_analysis.png` — distribution with 0.1 bands marked
5. `domain_distribution_report.md` — written summary

## Note for the paper

The star filter addresses a key concern: many tools in the dataset may have minimal real-world use. Filtering to ≥5 stars ensures we're measuring tools that at least some researchers actually use, making the sustainability story more compelling.
