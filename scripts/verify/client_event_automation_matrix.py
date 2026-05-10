#!/usr/bin/env python3
"""Create synthetic client/event/meeting records and verify LT automation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"


def bench_run() -> dict:
    proc = subprocess.run(
        [
            "docker",
            "exec",
            CONTAINER,
            "bench",
            "--site",
            SITE,
            "execute",
            "locally_twisted.verify.client_event_automation_matrix.run",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    text = proc.stdout.strip()
    if not text:
        raise RuntimeError("client event automation matrix returned no output")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"client event automation matrix returned non-JSON output: {text[:1000]}") from exc


def write_markdown(result: dict, path: Path) -> None:
    lines = [
        "# Client Event Automation Matrix",
        "",
        f"- Generated at: {result.get('generated_at')}",
        f"- Marker: `{result.get('marker')}`",
        f"- Scenarios: {result.get('scenario_count')}",
        f"- Result: {'PASS' if result.get('ok') else 'FAIL'}",
        "",
        "## Scenarios",
        "",
        "| Scenario | Client Type | Lead | Customer | Event | Meeting | Final Open Tasks |",
        "|---|---|---|---|---|---|---|",
    ]
    for scenario in result.get("scenarios") or []:
        open_tasks = scenario.get("final_open_tasks") or []
        task_text = "<br>".join(
            f"{task.get('custom_pipeline_stage')}: {task.get('subject')}" for task in open_tasks
        ) or "(none)"
        lines.append(
            "| {id} | {client_type} | {lead} | {customer} | {event} | {meeting} | {tasks} |".format(
                id=scenario.get("id") or "",
                client_type=scenario.get("client_type") or "",
                lead=scenario.get("lead") or "",
                customer=scenario.get("customer") or "",
                event=scenario.get("event") or "",
                meeting=scenario.get("meeting") or "",
                tasks=task_text,
            )
        )

    lines.extend(["", "## Failures", ""])
    failures = result.get("failures") or []
    if failures:
        lines.extend(f"- {failure}" for failure in failures)
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings / Automation Gaps", ""])
    warnings = result.get("warnings") or []
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")

    cleanup = result.get("cleanup") or {}
    lines.extend(["", "## Cleanup", ""])
    lines.append(f"- Deleted records: {len(cleanup.get('deleted') or [])}")
    cleanup_failures = cleanup.get("failures") or []
    if cleanup_failures:
        lines.append("- Cleanup failures:")
        lines.extend(f"  - {failure}" for failure in cleanup_failures)
    else:
        lines.append("- Cleanup failures: none")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        default="output/client-event-automation-matrix-20260510.json",
        help="JSON report output path.",
    )
    parser.add_argument(
        "--markdown",
        default="output/client-event-automation-matrix-20260510.md",
        help="Markdown report output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = bench_run()
    except RuntimeError as exc:
        print("[CLIENT EVENT AUTOMATION MATRIX] FAIL")
        print(f"  - {exc}")
        return 1

    report_path = ROOT / args.report
    markdown_path = ROOT / args.markdown
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    write_markdown(result, markdown_path)

    print(f"[CLIENT EVENT AUTOMATION MATRIX] {'PASS' if result.get('ok') else 'FAIL'}")
    print(f"  marker: {result.get('marker')}")
    print(f"  scenarios: {result.get('scenario_count')}")
    print(f"  report: {report_path}")
    print(f"  markdown: {markdown_path}")
    if result.get("warnings"):
        print("  warnings:")
        for warning in result.get("warnings") or []:
            print(f"    - {warning}")
    if not result.get("ok"):
        print("  failures:")
        for failure in result.get("failures") or ["Verifier returned no result"]:
            print(f"    - {failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
