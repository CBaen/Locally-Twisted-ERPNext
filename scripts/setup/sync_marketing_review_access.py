#!/usr/bin/env python3
"""Sync LT website-only external marketing review access."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.seed.sync_marketing_review_access.execute"
APPROVED_REVIEWER_EMAIL = "marketing@exploringnotboring.com"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reviewer-email",
        type=_approved_reviewer_email,
        help=f"Create or repair the approved website-only marketing reviewer ({APPROVED_REVIEWER_EMAIL}).",
    )
    parser.add_argument(
        "--send-welcome-email",
        action="store_true",
        help="Ask Frappe to send the welcome email when creating/updating the reviewer user.",
    )
    args = parser.parse_args()
    try:
        result = bench_execute(
            reviewer_email=args.reviewer_email,
            send_welcome_email=args.send_welcome_email,
        )
    except Exception as exc:
        print("[MARKETING REVIEW ACCESS SYNC] FAIL")
        print(f"  - {exc}")
        return 1

    failures = result.get("boundary_failures") or []
    print("[MARKETING REVIEW ACCESS SYNC] " + ("PASS" if not failures else "FAIL"))
    print(f"  ensured_role: {result.get('ensured_role')}")
    if result.get("reviewer_user"):
        reviewer = result["reviewer_user"]
        print(f"  reviewer_user: {reviewer.get('email')} ({reviewer.get('action')})")
    print(f"  removed_docperm_rows: {len(result.get('removed_docperm_rows') or [])}")
    print(f"  boundary_ok: {result.get('boundary_ok')}")
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")
        return 1
    return 0


def bench_execute(*, reviewer_email: str | None = None, send_welcome_email: bool = False) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if reviewer_email:
        kwargs["reviewer_email"] = reviewer_email
        kwargs["send_welcome_email"] = send_welcome_email
    command = ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD]
    if kwargs:
        command.extend(["--kwargs", repr(kwargs)])
    proc = subprocess.run(
        command,
        text=True,
        capture_output=True,
        timeout=90,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return _parse_json_stdout(proc.stdout)


def _approved_reviewer_email(value: str) -> str:
    email = (value or "").strip().lower()
    if email != APPROVED_REVIEWER_EMAIL:
        raise argparse.ArgumentTypeError(
            f"refusing arbitrary marketing reviewer provisioning; approved email is {APPROVED_REVIEWER_EMAIL}"
        )
    return email


def _parse_json_stdout(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        raise RuntimeError("sync returned no output")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start == -1:
            raise RuntimeError(f"sync returned non-JSON output: {text}") from None
        parsed, _ = json.JSONDecoder().raw_decode(text[start:])
        if not isinstance(parsed, dict):
            raise RuntimeError(f"sync returned {type(parsed).__name__}, expected object")
        return parsed


if __name__ == "__main__":
    sys.exit(main())
