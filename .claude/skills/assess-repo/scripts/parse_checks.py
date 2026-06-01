#!/usr/bin/env python3
"""Parse /tmp/almanack_result.json against the CCT spec and write /tmp/parsed_checks.json."""
import json
import sys
from pathlib import Path

SPEC_PATH = Path(__file__).resolve().parent.parent / "reference" / "cct-spec.json"


def parse(almanack_path: str = "/tmp/almanack_result.json",
          out_path: str = "/tmp/parsed_checks.json") -> int:
    spec = json.loads(SPEC_PATH.read_text())
    check_map = {cid: c["key"] for cid, c in spec["checks"].items()}
    fix_map = {cid: c["fix"] for cid, c in spec["checks"].items()}
    meta_map = spec["meta_ids"]

    data = json.loads(Path(almanack_path).read_text())

    checks, meta = {}, {}
    for item in data:
        if not isinstance(item, dict):
            continue
        iid = item.get("id")
        if iid in check_map:
            result = item.get("result")
            checks[check_map[iid]] = {
                "passed": bool(result) if result is not None else False,
                "fix": fix_map[iid],
                "id": iid,
            }
        elif iid in meta_map:
            meta[meta_map[iid]] = item.get("result")

    Path(out_path).write_text(json.dumps({"checks": checks, "meta": meta},
                                         indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(parse())
