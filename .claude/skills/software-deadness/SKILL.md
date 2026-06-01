---
name: software-deadness
description: Analyze "dead" scientific software — tools with no commits in 2+ years. Use when asked about software longevity, maintenance patterns, dead vs alive tools, or what qualities help software survive long-term.
argument-hint: "[output-dir]"
---

Analyze software "deadness" in the CCKP toolkit benchmark dataset.

## Context

The paper question (from the team discussion): Is sustainable scientific software like Linux — needing perpetual maintenance — or is it OK to be impactful and then "move forward into separate repos or versioning"?

Define **dead software**: a tool whose `last_commit` date is more than 2 years before the analysis date.

The key question is whether dead tools differ from alive tools in:
1. Their sustainability/JOSS scores
2. Their domain distribution
3. Whether high-scoring tools "stay alive" longer
4. Whether some dead tools were impactful despite dying

## Data location

- **Aggregated data**: `~/cckp-toolkit-workflow/benchmark_analysis_combined/aggregated_data.csv`
- Columns available: `tool_name`, `last_commit`, `first_commit`, `days_of_development`, `commits`, `almanack_score`, `joss_overall_score`, `composite_score`, `domain`, `language`, `almanack_grade`
- **Output**: `$ARGUMENTS` or default to `~/cckp-toolkit-workflow/software_deadness/`

## Analysis steps

### Step 1 — Classify tools by status

```python
import pandas as pd
from datetime import date, timedelta

csv.field_size_limit(10**7)
df = pd.read_csv('~/cckp-toolkit-workflow/benchmark_analysis_combined/aggregated_data.csv')
df['last_commit'] = pd.to_datetime(df['last_commit'], errors='coerce')

DEAD_THRESHOLD = date.today() - timedelta(days=730)  # 2 years
df['is_dead'] = df['last_commit'].dt.date < DEAD_THRESHOLD
df['years_since_commit'] = (pd.Timestamp.today() - df['last_commit']).dt.days / 365
df['years_of_development'] = df['days_of_development'].astype(float) / 365
```

Report: how many tools are dead vs alive? What % per domain?

### Step 2 — Score comparison (dead vs alive)

For `almanack_score`, `joss_overall_score`, `composite_score`:
- Compute mean ± SD for dead vs alive groups
- Run Mann-Whitney U test (non-parametric, since scores are not normally distributed)
- Report effect size (Cohen's d or rank-biserial r)
- Visualize: violin plot or box plot comparing dead vs alive

Key question: **Do tools with higher scores stay alive longer?**

### Step 3 — Longevity analysis

Does sustainability score predict longevity? Use:
- `days_of_development` as outcome
- `almanack_score` and `joss_overall_score` as predictors
- Simple linear regression + scatter plot
- Correlate each of the 11 individual almanack checks with days_of_development

### Step 4 — "Impactful but dead" category

Identify tools that:
- Are dead (`is_dead = True`)
- Had relatively high scores (`composite_score` above median for their domain)

These are the "lived a good life" tools — impactful, then moved on. Report:
- How many fall in this category?
- What domain are they in?
- What was their development lifespan?

Contrast with "always low quality and dead" tools.

Create 4 quadrants based on `composite_score` (above/below median) × `is_dead`:
| | Alive | Dead |
|---|---|---|
| High score | Stable/Maturing | Impactful, moved on |
| Low score | Needs work | Never took off |

### Step 5 — What do long-lived tools have in common?

Filter to tools with `days_of_development > 2000` (≈5+ years of active development).
- What checks do they consistently pass? (feature profile)
- What domains are they in?
- Compare almanack component pass rates vs short-lived tools

### Step 6 — Output

Produce:
1. `deadness_summary.csv` — full dataset with `is_dead`, `years_since_commit`, quadrant label
2. `deadness_stats.json` — test results (Mann-Whitney U, effect sizes, counts)
3. Visualizations:
   - Box plot: scores by alive/dead status
   - Scatter: score vs days_of_development (colored by domain)
   - Stacked bar: alive/dead proportions by domain
   - Heatmap: feature presence for long-lived vs short-lived tools
4. `deadness_report.md` — written summary for the paper

## Note for the paper

The framing: software sustainability ≠ software immortality. A tool can be "done" (versioned, archived, cited) and still have been sustainable during its active life. The score should capture quality of maintenance *during active development*, not just whether it's still being updated.
