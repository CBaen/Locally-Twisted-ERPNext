#!/usr/bin/env python3
"""Send or dry-run a fail-loud LT account access password reset."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.marketing_access_reset.execute"
PREVIEW_METHOD = "locally_twisted.marketing_access_reset.send_preview"
DEFAULT_EMAIL = "marketing@exploringnotboring.com"
DEFAULT_LIVE_SITE_URL = "https://locallytwisted.com"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--mode", choices=("review", "builder"), default="builder")
    parser.add_argument("--send", action="store_true", help="Actually send the reset email. Omit for dry-run readiness check.")
    parser.add_argument("--wait-seconds", type=int, default=0, help="Poll Email Queue after sending.")
    parser.add_argument("--preview-email", help="Send a safe preview email to this recipient instead of sending the real account reset.")
    parser.add_argument("--site-url", default=DEFAULT_LIVE_SITE_URL, help="Site URL to show in preview emails. Default: https://locallytwisted.com")
    parser.add_argument("--expected-site-url", default="", help="For real sends, fail if the generated reset link does not start with this URL.")
    parser.add_argument("--json", action="store_true", help="Print full JSON payload.")
    args = parser.parse_args()

    if args.preview_email:
        method = PREVIEW_METHOD
        kwargs = {
            "preview_email": args.preview_email,
            "access_email": args.email,
            "mode": args.mode,
            "wait_seconds": args.wait_seconds or 20,
            "site_url": args.site_url,
        }
    else:
        method = METHOD
        kwargs = {
            "email": args.email,
            "mode": args.mode,
            "send": args.send,
            "wait_seconds": args.wait_seconds,
            "expected_site_url": args.expected_site_url,
        }

    try:
        result = _bench_execute(kwargs, method=method)
    except Exception as exc:
        print("[MARKETING ACCESS RESET] FAIL")
        print(f"  - {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        label = "PASS" if result.get("ok") and args.send else "READY" if result.get("ok") else "FAIL"
        if result.get("preview_only") and result.get("ok"):
            label = "PREVIEW SENT"
        print(f"[MARKETING ACCESS RESET] {label}")
        print(f"  email: {result.get('email') or result.get('access_email')}")
        if result.get("preview_email"):
            print(f"  preview_email: {result.get('preview_email')}")
            print(f"  visible_greeting: {result.get('visible_greeting')}")
        print(f"  mode: {result.get('mode')}")
        print(f"  expected_role: {result.get('expected_role')}")
        print(f"  expected_user_type: {result.get('expected_user_type')}")
        print(f"  expected_site_url: {result.get('expected_site_url')}")
        print(f"  current_site_url: {result.get('current_site_url')}")
        print(f"  sender: {result.get('sender')}")
        print(f"  send_requested: {result.get('send_requested')}")
        print(f"  reset_key_written: {result.get('reset_key_written')}")
        contract = result.get("email_contract") or {}
        if contract:
            print(f"  subject: {contract.get('subject')}")
            print(f"  greeting: {contract.get('greeting')}")
            print(f"  style: {contract.get('style')}")
        sent_contract = result.get("sent_email_contract") or {}
        if sent_contract:
            print(f"  sent_contract_queue: {sent_contract.get('queue_name')}")
            print(f"  sent_contract_greeting: {sent_contract.get('greeting_verified')}")
        user = result.get("user") or {}
        if user:
            print(f"  current_user_type: {user.get('user_type')}")
            print(f"  current_roles: {', '.join(user.get('roles') or [])}")
            print(f"  last_login: {user.get('last_login') or '(never)'}")
            print(f"  last_password_reset_date: {user.get('last_password_reset_date') or '(none)'}")
        accounts = (result.get("outgoing_email") or {}).get("accounts") or []
        print(f"  outgoing_accounts: {len(accounts)}")
        for account in accounts[:3]:
            default = " default" if account.get("default_outgoing") else ""
            print(f"    - {account.get('name')} <{account.get('email_id')}> via {account.get('smtp_server')}:{account.get('smtp_port')}{default}")
        queues = result.get("queue") or []
        print(f"  queue_rows: {len(queues)}")
        for row in queues:
            print(f"    - {row.get('name')} status={row.get('status')} recipient_status={row.get('recipient_status')} account={row.get('email_account')} sender={row.get('sender')}")
        failures = result.get("failures") or []
        if failures:
            print("  failures:")
            for failure in failures:
                print(f"    - {failure}")

    return 0 if result.get("ok") else 1


def _bench_execute(kwargs: dict[str, Any], method: str = METHOD) -> dict[str, Any]:
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
        raise RuntimeError("reset helper returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start == -1:
            raise RuntimeError(f"reset helper returned non-JSON output: {text}") from None
        parsed, _ = json.JSONDecoder().raw_decode(text[start:])
    if not isinstance(parsed, dict):
        raise RuntimeError(f"reset helper returned {type(parsed).__name__}, expected object")
    return parsed


if __name__ == "__main__":
    sys.exit(main())
