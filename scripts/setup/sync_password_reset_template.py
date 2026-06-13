#!/usr/bin/env python3
"""Install or verify the Locally Twisted branded password-reset Email Template."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
SYNC_METHOD = "locally_twisted.password_reset_email.sync_password_reset_template"
VERIFY_METHOD = "locally_twisted.password_reset_email.verify_password_reset_template"
DEFAULT_EMAIL = "marketing@exploringnotboring.com"
DEFAULT_SITE_URL = "https://locallytwisted.com"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true", help="Only verify current System Settings/template; do not install or change anything.")
    parser.add_argument("--no-commit", action="store_true", help="Run the sync method without committing changes.")
    parser.add_argument("--account-email", default=DEFAULT_EMAIL, help="Preview account email used for render-contract verification.")
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL, help="Expected site URL shown in the rendered email.")
    parser.add_argument("--json", action="store_true", help="Print full JSON payload.")
    args = parser.parse_args()

    method = VERIFY_METHOD if args.verify_only else SYNC_METHOD
    kwargs: dict[str, Any]
    if args.verify_only:
        kwargs = {"account_email": args.account_email, "site_url": args.site_url}
    else:
        kwargs = {"commit": not args.no_commit}

    try:
        result = _bench_execute(method=method, kwargs=kwargs)
    except Exception as exc:
        print("[PASSWORD RESET TEMPLATE] FAIL")
        print(f"  - {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        print("[PASSWORD RESET TEMPLATE] " + ("PASS" if result.get("ok") else "FAIL"))
        verification = result.get("verification") or result
        print(f"  template: {verification.get('template_name') or result.get('template_name')}")
        print(f"  configured_template: {verification.get('configured_template') or result.get('system_setting_after')}")
        print(f"  subject: {verification.get('subject') or result.get('template_subject')}")
        print(f"  greeting: {verification.get('greeting')}")
        print(f"  account_email: {verification.get('account_email')}")
        print(f"  site_url: {verification.get('site_url')}")
        print(f"  generic_fallback_blocked: {verification.get('generic_fallback_blocked')}")
        if not args.verify_only:
            print(f"  created: {result.get('created')}")
            print(f"  updated: {result.get('updated')}")
            print(f"  committed: {result.get('commit_requested')}")
        failures = result.get("failures") or verification.get("failures") or []
        if failures:
            print("  failures:")
            for failure in failures:
                print(f"    - {failure}")
        excerpt = verification.get("message_excerpt")
        if excerpt:
            print("  message_excerpt:")
            print("    " + excerpt[:500])

    return 0 if result.get("ok") else 1


def _bench_execute(method: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", method, "--kwargs", repr(kwargs)],
        text=True,
        capture_output=True,
        timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return _parse_json_stdout(proc.stdout)


def _parse_json_stdout(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        raise RuntimeError("template helper returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start == -1:
            raise RuntimeError(f"template helper returned non-JSON output: {text}") from None
        parsed, _ = json.JSONDecoder().raw_decode(text[start:])
    if not isinstance(parsed, dict):
        raise RuntimeError(f"template helper returned {type(parsed).__name__}, expected object")
    return parsed


if __name__ == "__main__":
    sys.exit(main())
