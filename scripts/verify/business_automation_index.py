#!/usr/bin/env python3
"""Index LT business automation surfaces and fail loudly on broken required links."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.business_automation_index.run"
ROOT = Path(__file__).resolve().parents[2]


class AutomationIndexFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=90,
    )
    if proc.returncode != 0:
        raise AutomationIndexFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise AutomationIndexFail("business automation index returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AutomationIndexFail(f"business automation index returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise AutomationIndexFail(f"business automation index returned {type(parsed).__name__}, expected object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    args = parser.parse_args()

    try:
        result = bench_execute()
    except AutomationIndexFail as exc:
        print(f"[BUSINESS AUTOMATION INDEX] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(result, indent=2, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[BUSINESS AUTOMATION INDEX] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(result)

    return 0 if result.get("ok") else 1


def _print_summary(result: dict[str, Any]) -> None:
    print("[BUSINESS AUTOMATION INDEX] " + ("PASS" if result.get("ok") else "FAIL"))
    print(f"  generated_at: {result.get('generated_at')}")
    for key in (
        "exists_and_connected",
        "exists_but_not_connected",
        "missing_needs_connection",
        "missing_should_connect",
        "loud_failure_gaps",
    ):
        rows = result.get(key) or []
        print(f"  {key}: {len(rows)}")
        for row in rows[:8]:
            print(f"    - {row.get('id')}: {row.get('summary')}")
        if len(rows) > 8:
            print(f"    - ... {len(rows) - 8} more")

    failures = result.get("failures") or []
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
