#!/usr/bin/env python3
"""Run the Software Gardening Almanack on a GitHub URL and write /tmp/almanack_result.json.

Uses almanack.metrics.data.get_table, which is the underlying function that the
`almanack table` CLI wraps. Returns the same list-of-dicts shape: one entry per
metric, each with keys `id`, `name`, `result`, etc.
"""
import json
import sys
from pathlib import Path


def run_almanack(url: str, out_path: str = "/tmp/almanack_result.json") -> int:
    from almanack.metrics.data import get_table

    rows = get_table(repo_path=url)
    Path(out_path).write_text(json.dumps(rows, indent=2, default=str))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("usage: run_almanack.py <github-url-or-local-path>\n")
        sys.exit(2)
    sys.exit(run_almanack(sys.argv[1]))
