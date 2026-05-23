#!/usr/bin/env python3
"""Validate sanitized Frappe Cloud deploy/update payload shape offline.

The 2026-05-22 staging failure proved that nested `apps` and `sites` values
must be typed JSON arrays/objects, not strings that look like JSON.
The 2026-05-23 retry proved typed JSON is still not enough: deploy/update site
rows must carry the complete current provider site object, not only `name`.

Examples:
  python scripts/verify/frappe_cloud_payload_contract.py --self-test
  python scripts/verify/frappe_cloud_payload_contract.py --payload-file output/sanitized-payload.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_SITE_FIELDS = ("name", "server", "bench", "skip_backups", "skip_failing_patches")


def load_payload_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"payload file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"payload file is not valid JSON: {path}: {exc}") from exc


def unwrap_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    for wrapper_key in ("payload", "body", "data"):
        wrapped = payload.get(wrapper_key)
        if isinstance(wrapped, dict) and ("apps" in wrapped or "sites" in wrapped):
            return wrapped
    return payload


def validate_frappe_cloud_payload(payload: Any) -> list[str]:
    body = unwrap_payload(payload)
    if not isinstance(body, dict):
        return ["Frappe Cloud payload must be a JSON object"]

    failures: list[str] = []
    content_type = extract_content_type(payload)
    if content_type != "application/json":
        failures.append(
            "payload artifact must include content_type or Content-Type set to application/json"
        )

    for key in ("apps", "sites"):
        value = body.get(key)
        if isinstance(value, str):
            failures.append(f"{key} must be a typed JSON array, not a stringified nested JSON value")
            continue
        if not isinstance(value, list):
            failures.append(f"{key} must be a JSON array")
            continue
        if not value:
            failures.append(f"{key} must not be empty")
            continue
        for index, item in enumerate(value):
            if isinstance(item, str):
                failures.append(f"{key}[{index}] must be a JSON object, not a string")
            elif not isinstance(item, dict):
                failures.append(f"{key}[{index}] must be a JSON object")
            elif not item:
                failures.append(f"{key}[{index}] must not be empty")
            elif key == "sites":
                failures.extend(validate_site_object(item, index))
    return failures


def validate_site_object(site: dict[str, Any], index: int) -> list[str]:
    failures: list[str] = []
    for field in REQUIRED_SITE_FIELDS:
        if field not in site:
            failures.append(f"sites[{index}] must include {field}")

    for field in ("name", "server", "bench"):
        if field in site and not isinstance(site[field], str):
            failures.append(f"sites[{index}].{field} must be a string")
        elif field in site and not site[field].strip():
            failures.append(f"sites[{index}].{field} must not be blank")

    for field in ("skip_backups", "skip_failing_patches"):
        if field in site and not isinstance(site[field], bool):
            failures.append(f"sites[{index}].{field} must be a boolean")

    return failures


def extract_content_type(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    direct = payload.get("content_type") or payload.get("Content-Type")
    if isinstance(direct, str):
        return direct.split(";", 1)[0].strip().lower()
    headers = payload.get("headers")
    if isinstance(headers, dict):
        header = headers.get("Content-Type") or headers.get("content-type")
        if isinstance(header, str):
            return header.split(";", 1)[0].strip().lower()
    return None


def run_self_test() -> list[str]:
    valid_site = {
        "name": "locallytwisted-staging.frappe.cloud",
        "server": "f4-virginia.frappe.cloud",
        "bench": "bench-40102-000013-f4v",
        "skip_backups": False,
        "skip_failing_patches": False,
    }
    valid_body = {
        "apps": [
            {
                "app": "locally_twisted",
                "repository": "https://github.com/CBaen/Locally-Twisted-Frappe-App.git",
                "hash": "a" * 40,
            }
        ],
        "sites": [valid_site],
    }
    valid_payload = {"content_type": "application/json", "body": valid_body}
    invalid_apps_string = {
        "content_type": "application/json",
        "body": {"apps": json.dumps(valid_body["apps"]), "sites": valid_body["sites"]},
    }
    invalid_sites_string = {
        "content_type": "application/json",
        "body": {"apps": valid_body["apps"], "sites": json.dumps(valid_body["sites"])},
    }
    invalid_item_string = {
        "content_type": "application/json",
        "body": {"apps": ["locally_twisted"], "sites": valid_body["sites"]},
    }
    incomplete_site = {
        "content_type": "application/json",
        "body": {"apps": valid_body["apps"], "sites": [{"name": valid_site["name"]}]},
    }
    missing_sites = {"content_type": "application/json", "body": {"apps": valid_body["apps"]}}
    invalid_content_type = {"content_type": "application/x-www-form-urlencoded", "body": valid_body}

    failures: list[str] = []
    if validate_frappe_cloud_payload(valid_payload):
        failures.append("valid typed payload did not pass")
    if not validate_frappe_cloud_payload(invalid_content_type):
        failures.append("form-encoded content type did not fail")
    if not validate_frappe_cloud_payload(invalid_apps_string):
        failures.append("stringified apps payload did not fail")
    if not validate_frappe_cloud_payload(invalid_sites_string):
        failures.append("stringified sites payload did not fail")
    if not validate_frappe_cloud_payload(invalid_item_string):
        failures.append("string item payload did not fail")
    if not validate_frappe_cloud_payload(incomplete_site):
        failures.append("incomplete site object did not fail")
    if not validate_frappe_cloud_payload(missing_sites):
        failures.append("missing sites payload did not fail")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--payload-file", type=Path, help="Sanitized Frappe Cloud JSON payload artifact to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run local contract self-tests.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result.")
    args = parser.parse_args()

    try:
        if args.payload_file:
            failures = validate_frappe_cloud_payload(load_payload_file(args.payload_file))
        else:
            failures = run_self_test()
    except Exception as exc:
        failures = [f"{type(exc).__name__}: {exc}"]

    result = {"ok": not failures, "failures": failures}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[FRAPPE CLOUD PAYLOAD CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in failures:
            print(f"  - {failure}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
