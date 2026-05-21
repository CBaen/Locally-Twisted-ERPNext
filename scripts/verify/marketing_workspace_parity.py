#!/usr/bin/env python3
"""Verify LT internal marketing workspace and external-review boundary."""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
MARKETING_HOME = "LT Marketing Home"
MARKETING_TITLE = "Marketing Home"
EXTERNAL_REVIEW_ROLE = "LT Marketing Review Access"
EXPECTED_ROLES = {"LT Owner Access", "Website Manager", "Newsletter Manager", "System Manager"}

EXPECTED_NUMBER_CARDS = {
    "New Inquiries": {
        "label": "New Inquiries",
        "document_type": "Lead",
        "function": "Count",
        "filters_json": [["Lead", "custom_pipeline_stage", "=", "New Inquiry"]],
    },
    "Newsletter Signups": {
        "label": "Newsletter Signups",
        "document_type": "LT Newsletter Signup",
        "function": "Count",
        "filters_json": [],
    },
    "Live Shop Items": {
        "label": "Live Shop Items",
        "document_type": "Website Item",
        "function": "Count",
        "filters_json": [["Website Item", "published", "=", 1]],
    },
    "Blog Posts": {
        "label": "Blog Posts",
        "document_type": "Blog Post",
        "function": "Count",
        "filters_json": [],
    },
}

EXPECTED_URL_SHORTCUTS = {
    "Marketing Review Page": "/marketing-review",
    "Homepage": "/",
    "Portfolio": "/portfolio",
    "Contact Page": "/contact",
    "Shop": "/shop",
}

EXPECTED_DOCTYPE_SHORTCUTS = {
    "Web Pages": ("Web Page", "List"),
    "Website Items": ("Website Item", "List"),
    "Blog Posts": ("Blog Post", "List"),
    "Newsletters": ("Newsletter", "List"),
    "Email Groups": ("Email Group", "List"),
    "Campaigns": ("Campaign", "List"),
    "New Inquiries": ("Lead", "List"),
}

EXPECTED_TEXT = {
    "Marketing Home",
    "Public review links",
    "Content and shop surfaces",
    "Outreach and demand",
}


def bench_execute(method: str, *, kwargs: dict[str, Any] | None = None) -> Any:
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "execute",
        method,
    ]
    if kwargs is not None:
        cmd.extend(["--kwargs", json.dumps(kwargs)])

    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    return json.loads(text) if text else None


def get_doc(doctype: str, name: str) -> dict[str, Any]:
    return bench_execute("frappe.client.get", kwargs={"doctype": doctype, "name": name})


def try_get_doc(doctype: str, name: str) -> dict[str, Any] | None:
    try:
        return get_doc(doctype, name)
    except RuntimeError as exc:
        if "DoesNotExistError" in str(exc):
            return None
        raise


def decode_json(value: str | None) -> Any:
    if not value:
        return []
    return json.loads(value)


def check_workspace() -> list[str]:
    failures = []
    workspace = get_doc("Workspace", MARKETING_HOME)
    content = json.loads(workspace.get("content") or "[]")
    content_text = json.dumps(content)
    shortcut_blocks = {
        (block.get("data") or {}).get("shortcut_name")
        for block in content
        if block.get("type") == "shortcut"
    }
    card_blocks = {
        (block.get("data") or {}).get("number_card_name")
        for block in content
        if block.get("type") == "number_card"
    }
    shortcuts = {row.get("label"): row for row in workspace.get("shortcuts", [])}
    roles = {row.get("role") for row in workspace.get("roles", [])}
    workspace_cards = {row.get("number_card_name") for row in workspace.get("number_cards", [])}

    if workspace.get("title") != MARKETING_TITLE:
        failures.append(f"{MARKETING_HOME} title expected {MARKETING_TITLE!r}, found {workspace.get('title')!r}")
    if EXTERNAL_REVIEW_ROLE in roles:
        failures.append(f"{MARKETING_HOME} must not include website-only external role {EXTERNAL_REVIEW_ROLE!r}")
    missing_roles = sorted(EXPECTED_ROLES - roles)
    if missing_roles:
        failures.append(f"{MARKETING_HOME} missing roles: {', '.join(missing_roles)}")

    for text in EXPECTED_TEXT:
        if text not in content_text:
            failures.append(f"{MARKETING_HOME} content missing text {text!r}")

    for label, url in EXPECTED_URL_SHORTCUTS.items():
        shortcut = shortcuts.get(label)
        if not shortcut:
            failures.append(f"{MARKETING_HOME} missing shortcut {label!r}")
            continue
        if label not in shortcut_blocks:
            failures.append(f"{MARKETING_HOME} content missing shortcut block {label!r}")
        if shortcut.get("type") != "URL" or shortcut.get("url") != url:
            failures.append(
                f"{MARKETING_HOME} {label!r} expected URL {url}, found "
                f"{shortcut.get('type')} {shortcut.get('url')}"
            )

    for label, (doctype, view) in EXPECTED_DOCTYPE_SHORTCUTS.items():
        shortcut = shortcuts.get(label)
        if not shortcut:
            failures.append(f"{MARKETING_HOME} missing shortcut {label!r}")
            continue
        if label not in shortcut_blocks:
            failures.append(f"{MARKETING_HOME} content missing shortcut block {label!r}")
        if shortcut.get("link_to") != doctype or shortcut.get("doc_view") != view:
            failures.append(
                f"{MARKETING_HOME} {label!r} expected {doctype}/{view}, found "
                f"{shortcut.get('link_to')}/{shortcut.get('doc_view')}"
            )

    for card_name in EXPECTED_NUMBER_CARDS:
        if card_name not in workspace_cards:
            failures.append(f"{MARKETING_HOME} missing number card child row {card_name!r}")
        if card_name not in card_blocks:
            failures.append(f"{MARKETING_HOME} content missing number card block {card_name!r}")

    return failures


def check_number_cards() -> list[str]:
    failures = []
    for name, expected in EXPECTED_NUMBER_CARDS.items():
        card = try_get_doc("Number Card", name)
        if not card:
            failures.append(f"Missing Number Card {name!r}")
            continue
        for key in ("label", "document_type", "function"):
            if card.get(key) != expected[key]:
                failures.append(
                    f"Number Card {name!r} {key} expected {expected[key]!r}, found {card.get(key)!r}"
                )
        if decode_json(card.get("filters_json")) != expected["filters_json"]:
            failures.append(
                f"Number Card {name!r} filters expected {expected['filters_json']!r}, "
                f"found {decode_json(card.get('filters_json'))!r}"
            )
    return failures


def check_external_review_boundary() -> list[str]:
    result = bench_execute("locally_twisted.marketing_review_access.marketing_role_boundary")
    if not isinstance(result, dict):
        return ["marketing role boundary returned an invalid result"]
    if not result.get("ok"):
        return list(result.get("failures") or ["marketing role boundary failed"])
    if result.get("desk_access") != 0:
        return [f"{EXTERNAL_REVIEW_ROLE} desk_access expected 0, found {result.get('desk_access')!r}"]
    return []


def main() -> int:
    parse_noop_args(__doc__)
    failures = []
    try:
        failures.extend(check_workspace())
        failures.extend(check_number_cards())
        failures.extend(check_external_review_boundary())
    except Exception as exc:
        failures.append(str(exc))

    if failures:
        print("[MARKETING WORKSPACE PARITY] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[MARKETING WORKSPACE PARITY] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
