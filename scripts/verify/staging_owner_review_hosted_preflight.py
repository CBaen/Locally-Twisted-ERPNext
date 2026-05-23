#!/usr/bin/env python3
"""Run the hosted staging owner-review bootstrap preflight in read-only mode.

This verifier calls only the whitelisted
`preflight_staging_owner_review_bootstrap` method on the staging site. It does
not enqueue bootstrap, import catalog rows, migrate, cache clear, deploy, or
touch live/DNS/Stripe/Search Console state.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "verify"))

from staging_owner_review_gate import (  # noqa: E402
    CONFIRMATION,
    DEFAULT_APP_MIRROR,
    DEFAULT_CREDENTIALS,
    DEFAULT_SITE,
    DEFAULT_TEAM,
    PressClient,
    normalize_expected_hash,
    resolve_mirror_head,
    stage_method,
    staging_session,
)


PREFLIGHT_METHOD = (
    "locally_twisted.staging_owner_review_bootstrap."
    "preflight_staging_owner_review_bootstrap"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default=os.environ.get("LT_STAGING_SITE", DEFAULT_SITE))
    parser.add_argument("--team", default=os.environ.get("LT_FC_TEAM", DEFAULT_TEAM))
    parser.add_argument(
        "--credentials",
        type=Path,
        default=Path(os.environ.get("LT_FC_CREDENTIALS", str(DEFAULT_CREDENTIALS))),
    )
    parser.add_argument("--expected-hash", default=os.environ.get("LT_EXPECTED_APP_HASH"))
    parser.add_argument("--expected-hash-from-mirror", action="store_true")
    parser.add_argument("--mirror-url", default=DEFAULT_APP_MIRROR)
    parser.add_argument("--backup-artifact-file", type=Path)
    parser.add_argument("--zero-data-proof-file", type=Path)
    parser.add_argument("--output", type=Path, help="Write hosted preflight JSON artifact to this path.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true", help="Run offline artifact-shape checks.")
    args = parser.parse_args()

    try:
        if args.self_test:
            result = run_self_test()
        else:
            if args.expected_hash_from_mirror:
                args.expected_hash = resolve_mirror_head(args.mirror_url)
            if not args.expected_hash:
                raise RuntimeError(
                    "expected app hash is required; pass --expected-hash, set LT_EXPECTED_APP_HASH, "
                    "or use --expected-hash-from-mirror"
                )
            args.expected_hash = normalize_expected_hash(args.expected_hash)
            result = run_probe(args)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            result["output"] = str(args.output)
    except Exception as exc:
        result = {"ok": False, "failures": [f"{type(exc).__name__}: {exc}"]}

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[STAGING OWNER REVIEW HOSTED PREFLIGHT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in result.get("failures", []):
            print(f"  - {failure}")
        if result.get("output"):
            print(f"  output: {result['output']}")
    return 0 if result["ok"] else 1


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    press = PressClient(args.credentials, args.team)
    session = staging_session(press, args.site)
    params = {
        "confirm": CONFIRMATION,
        "expected_app_hash": args.expected_hash,
    }
    if args.backup_artifact_file:
        params["backup_artifact"] = read_json_argument(args.backup_artifact_file)
    if args.zero_data_proof_file:
        params["zero_data_proof"] = read_json_argument(args.zero_data_proof_file)

    try:
        response = stage_method(args.site, session, PREFLIGHT_METHOD, params)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "failures": [f"hosted preflight HTTP {exc.code}"],
            "site": args.site,
            "method": PREFLIGHT_METHOD,
            "status_code": exc.code,
            "error_summary": summarize_http_error_body(body),
            "provider_mutation_executed": False,
        }

    message = response.get("message") or {}
    preflight = message.get("preflight") if isinstance(message, dict) else {}
    failures = list((preflight or {}).get("failures") or [])
    if message.get("ok") is not True and not failures:
        failures.append("hosted preflight did not return ok=true")
    return {
        "ok": not failures,
        "failures": failures,
        "site": args.site,
        "method": PREFLIGHT_METHOD,
        "expected_app_hash": args.expected_hash,
        "preflight": preflight,
        "provider_mutation_executed": False,
    }


def read_json_argument(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return json.dumps(data, sort_keys=True)


def summarize_http_error_body(body: str) -> dict[str, str]:
    """Keep the Frappe failure reason without storing traceback or secrets."""
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return {"message": sanitize_error_text(body)}

    summary: dict[str, str] = {}
    if isinstance(payload, dict):
        for key in ("exc_type", "exception", "message"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                summary[key] = sanitize_error_text(value)
    if not summary:
        summary["message"] = "Frappe returned an HTTP error; raw body omitted from sanitized artifact"
    return summary


def sanitize_error_text(value: str, limit: int = 700) -> str:
    text = value.replace("\r", "\n")
    safe_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if lower.startswith("traceback ") or lower.startswith("file "):
            continue
        if "traceback (most recent call last)" in lower:
            continue
        safe_lines.append(stripped)
    collapsed = " ".join(safe_lines) or "HTTP error body omitted from sanitized artifact"
    redacted = re.sub(
        r"(?i)\b(api[_-]?key|api[_-]?secret|authorization|cookie|password|secret|session[_-]?id|sid|token)\b"
        r"\s*[:=]\s*['\"]?[^'\"\s,;}]+",
        lambda match: f"{match.group(1)}=[REDACTED]",
        collapsed,
    )
    if len(redacted) > limit:
        return redacted[: limit - 3].rstrip() + "..."
    return redacted


def run_self_test() -> dict[str, Any]:
    passing = {
        "message": {
            "ok": True,
            "preflight": {"ok": True, "failures": []},
        }
    }
    failing = {
        "message": {
            "ok": False,
            "preflight": {"ok": False, "failures": ["target_hash: mismatch"]},
        }
    }
    failures: list[str] = []
    if build_result_from_fixture(passing)["ok"] is not True:
        failures.append("passing hosted preflight fixture did not pass")
    if build_result_from_fixture(failing)["ok"] is not False:
        failures.append("failing hosted preflight fixture did not fail")
    sanitized = summarize_http_error_body(
        json.dumps(
            {
                "exc_type": "ValidationError",
                "exception": "frappe.exceptions.ValidationError: Missing method",
                "exc": '["Traceback (most recent call last):\\n  File \\"apps/frappe/frappe/app.py\\", line 120"]',
                "sid": "secret-session-value",
            }
        )
    )
    sanitized_text = json.dumps(sanitized, sort_keys=True).lower()
    if "traceback" in sanitized_text or "secret-session-value" in sanitized_text:
        failures.append("HTTP error sanitizer leaked traceback or secret-like content")
    return {"ok": not failures, "failures": failures}


def build_result_from_fixture(response: dict[str, Any]) -> dict[str, Any]:
    message = response.get("message") or {}
    preflight = message.get("preflight") if isinstance(message, dict) else {}
    failures = list((preflight or {}).get("failures") or [])
    if message.get("ok") is not True and not failures:
        failures.append("hosted preflight did not return ok=true")
    return {"ok": not failures, "failures": failures, "preflight": preflight}


if __name__ == "__main__":
    sys.exit(main())
