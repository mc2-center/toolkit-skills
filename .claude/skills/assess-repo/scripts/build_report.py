#!/usr/bin/env python3
"""Compose the final sustainability report from parsed Almanack + JOSS results.

Reads:
  /tmp/parsed_checks.json   (from parse_checks.py)
  /tmp/joss_results.json    (from the JOSS phase of the subagent)
  ../reference/cct-spec.json

Writes:
  /tmp/<repo>_sustainability_report.md

Also prints the full report to stdout so the calling subagent can return it.
"""
import json
import sys
from pathlib import Path

SPEC_PATH = Path(__file__).resolve().parent.parent / "reference" / "cct-spec.json"

ACTION_NARRATIVES = {
    "readme": {
        "missing": "no README at the repo root, or it is empty.",
        "how": "add a `README.md` at the root that covers purpose, install, and a usage example.",
        "why": "the README is the first thing every user, reviewer, and search engine reads. Without one, the repo is effectively invisible.",
    },
    "contributing": {
        "missing": "no CONTRIBUTING.md.",
        "how": "add a short `CONTRIBUTING.md` describing how to file issues, run tests locally, and submit PRs.",
        "why": "contributing guides reduce reviewer load and signal an active project. Strong predictor of sustained outside contribution.",
    },
    "code_of_conduct": {
        "missing": "no CODE_OF_CONDUCT.md.",
        "how": "copy the Contributor Covenant into `CODE_OF_CONDUCT.md` at the repo root.",
        "why": "low-effort baseline community signal; required for many funders and venues.",
    },
    "license": {
        "missing": "no OSI-approved license file at the repo root.",
        "how": "copy a standard OSI license (MIT, Apache-2.0, BSD-3-Clause) into a file named `LICENSE` at the repo root.",
        "why": "the strongest empirical predictor of community adoption in our analysis of 4,431 starred research tools. Without one, default copyright law blocks reuse, modification, and redistribution.",
    },
    "citable": {
        "missing": "no CITATION.cff or .zenodo.json.",
        "how": "add a `CITATION.cff` with title, authors, version, repo URL, and DOI.",
        "why": "second-strongest empirical predictor of community adoption. Tells citation tools how to credit the software.",
    },
    "branch_not_master": {
        "missing": "default branch is still `master`.",
        "how": "rename to `main` on GitHub (Settings → Branches), then update your local clone with `git branch -m master main && git fetch && git branch -u origin/main main && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main`.",
        "why": "current Git/GitHub default. Most CI examples and contributor instructions assume `main`.",
    },
    "common_docs": {
        "missing": "missing CHANGELOG.md and/or a `docs/` folder.",
        "how": "add a `CHANGELOG.md` (Keep a Changelog format is fine) and a minimal `docs/` folder with at least an architecture or design doc.",
        "why": "signals that the project is maintained and documented; reduces onboarding time for new contributors.",
    },
    "uses_issues": {
        "missing": "GitHub Issues is disabled or unused.",
        "how": "enable Issues in repo settings and triage incoming reports. This is a behavioral practice, not a one-time fix.",
        "why": "discoverable bug tracker is the lowest-friction way for users to surface problems and for maintainers to demonstrate responsiveness.",
    },
    "prs_enabled": {
        "missing": "pull requests are disabled.",
        "how": "enable PRs in repo settings (it's a single toggle).",
        "why": "PRs are the standard contribution mechanism on GitHub. Disabling them blocks outside contribution entirely.",
    },
    "doi_valid": {
        "missing": "no registered DOI for the software.",
        "how": "connect the repo to Zenodo (Settings → Integrations → Zenodo), cut a GitHub Release, and Zenodo will mint a DOI automatically.",
        "why": "a DOI gives the software a citable, archived identifier. Required by many journals for software citations.",
    },
    "doi_resolvable": {
        "missing": "the DOI listed in CITATION.cff does not resolve over HTTPS HEAD requests.",
        "how": "ensure the primary `doi:` field in `CITATION.cff` is the Zenodo software DOI (resolves cleanly), and put any related publication DOIs under `identifiers:` instead. Some publisher DOIs (Nature, Elsevier) reject HEAD requests and will fail this check even though they work in browsers.",
        "why": "downstream tooling (citation graphs, archival services) uses programmatic DOI resolution. A DOI that requires a browser is half-broken.",
    },
}

PASSED_LABEL = {
    "readme": "README present",
    "contributing": "CONTRIBUTING.md present",
    "code_of_conduct": "CODE_OF_CONDUCT.md present",
    "license": "OSI-approved LICENSE file present",
    "citable": "Citable (CITATION.cff present)",
    "branch_not_master": "Default branch is not `master`",
    "common_docs": "Standard docs present (CHANGELOG, docs/)",
    "uses_issues": "GitHub Issues enabled and used",
    "prs_enabled": "Pull requests enabled",
    "doi_valid": "DOI registered and valid",
    "doi_resolvable": "DOI resolves correctly",
}


def main(repo_name: str) -> int:
    spec = json.loads(SPEC_PATH.read_text())
    parsed = json.loads(Path("/tmp/parsed_checks.json").read_text())
    joss = json.loads(Path("/tmp/joss_results.json").read_text())

    checks = parsed["checks"]
    meta = parsed["meta"]
    tier = spec["tier"]
    tier_label = spec["tier_label"]
    shap = spec["shap_weight"]

    passed = [k for k, v in checks.items() if v["passed"]]
    failed = [k for k, v in checks.items() if not v["passed"]]

    failed.sort(key=lambda k: (tier[k], -shap.get(k, 0.0)))

    joss_score = sum(joss["scores"].values())
    joss_total = len(joss["scores"])

    lines = []
    lines.append(f"# Sustainability Assessment: {repo_name}\n")
    lines.append("## Pass rates\n")
    lines.append("| Instrument | Pass rate |")
    lines.append("|---|---|")
    lines.append(f"| Almanack (11 checks) | {len(passed)} / 11 |")
    lines.append(f"| JOSS-style criteria | {joss_score:g} / {joss_total} |")
    lines.append("")

    if passed:
        lines.append("## What's working\n")
        for k in passed:
            lines.append(f"- {PASSED_LABEL.get(k, k)}")
        lines.append("")

    if failed:
        lines.append("## Action items (ordered by ease-of-fix tier, then by empirical importance)\n")
        for i, k in enumerate(failed, 1):
            t = tier[k]
            w = shap.get(k, 0.0)
            narrative = ACTION_NARRATIVES.get(k, {})
            lines.append(f"### {i}. {checks[k]['fix']}  [{tier_label[str(t)]}]  [empirical importance: {w:.3f}]\n")
            if "missing" in narrative:
                lines.append(f"- What's missing: {narrative['missing']}")
            if "how" in narrative:
                lines.append(f"- How to fix: {narrative['how']}")
            if "why" in narrative:
                lines.append(f"- Why it matters: {narrative['why']}")
            lines.append("")

    if joss["scores"]:
        lines.append("## JOSS-style detail\n")
        for label, score in joss["scores"].items():
            mark = "x" if score >= 1.0 else ("~" if score >= 0.5 else " ")
            lines.append(f"- [{mark}] {label}")
        lines.append("")

    if meta:
        lines.append("## Repository metadata\n")
        commits = meta.get("commits")
        days = meta.get("days_of_development")
        files = meta.get("file_count")
        if commits is not None:
            lines.append(f"- Total commits: {commits}")
        if days is not None:
            years = float(days) / 365.25 if days else 0
            lines.append(f"- Days of development: {days} ({years:.1f} years)")
        if files is not None:
            lines.append(f"- Files tracked: {files}")
        lines.append("")

    report = "\n".join(lines)
    out_path = Path(f"/tmp/{repo_name}_sustainability_report.md")
    out_path.write_text(report)

    print(report)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("usage: build_report.py <repo-name>\n")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
