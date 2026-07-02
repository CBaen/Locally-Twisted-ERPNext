#!/usr/bin/env python3
"""Static guard for the three-brand DBA operating-brand boundary.

Default mode proves the current safe claim: docs guards exist, but runtime
`operating_brand` support is not implemented yet. It intentionally does not
read secrets, call ERPNext, call Meta, touch Stripe, or inspect customer data.

Use `--require-runtime` only after implementation work starts; that mode fails
until every critical runtime surface carries an explicit operating-brand hook.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_OPERATING_BRANDS = (
    "locally_twisted",
    "commercial_balloon_decor",
    "memorial_balloons",
)

GUARD_DOCS = (
    "BRAND-BOUNDARY.md",
    "capabilities/recipes/three-brand-dba-boundary-contract.md",
    "workstreams/three-brand-dba-boundary-2026-06-28.md",
)

CRITICAL_RUNTIME_SURFACES = (
    "apps/locally_twisted/locally_twisted/seed/sync_contact_intake_backend.py",
    "apps/locally_twisted/locally_twisted/www/book.py",
    "apps/locally_twisted/locally_twisted/www/contact.py",
    "apps/locally_twisted/locally_twisted/lead_cascade.py",
    "apps/locally_twisted/locally_twisted/www/checkout.py",
    "apps/locally_twisted/locally_twisted/payments/stripe_session.py",
    "apps/locally_twisted/locally_twisted/payments/stripe_webhook.py",
    "apps/locally_twisted/locally_twisted/www/payment_success.py",
    "apps/locally_twisted/locally_twisted/customer_email_theme.py",
    "apps/locally_twisted/locally_twisted/customer_portal.py",
    "apps/locally_twisted/locally_twisted/customer_portal_pages.py",
    "apps/locally_twisted/locally_twisted/outbound_documents/registry.py",
    "apps/locally_twisted/locally_twisted/outbound_documents/send_readiness.py",
    "apps/locally_twisted/locally_twisted/seed/sync_invoice_branding.py",
    "apps/locally_twisted/locally_twisted/seed/sync_site_branding.py",
    "apps/locally_twisted/locally_twisted/seo.py",
    "apps/locally_twisted/locally_twisted/website_context.py",
    "apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_marketing_tracking_settings/lt_marketing_tracking_settings.py",
)

PARTIAL_RUNTIME_THRESHOLD = 1


@dataclass(frozen=True)
class FileHit:
    path: str
    count: int


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable evidence.")
    parser.add_argument(
        "--require-runtime",
        action="store_true",
        help="Fail unless critical runtime surfaces contain operating_brand hooks.",
    )
    args = parser.parse_args(argv)

    result = evaluate(require_runtime=args.require_runtime)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_summary(result)
    return 0 if result["ok"] else 1


def evaluate(*, require_runtime: bool) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []

    guard_doc_results = _guard_docs()
    failures.extend(guard_doc_results["failures"])

    runtime_hits = _runtime_operating_brand_hits()
    missing_runtime = [
        path
        for path in CRITICAL_RUNTIME_SURFACES
        if not (PROJECT_ROOT / path).exists()
    ]
    if missing_runtime:
        failures.extend(f"critical runtime surface missing: {path}" for path in missing_runtime)

    surfaces_with_hooks = {hit.path for hit in runtime_hits if hit.count >= PARTIAL_RUNTIME_THRESHOLD}
    missing_hooks = [
        path
        for path in CRITICAL_RUNTIME_SURFACES
        if path not in surfaces_with_hooks
    ]

    runtime_status = "implemented" if not missing_hooks else "not_implemented"
    if runtime_hits and not require_runtime and missing_hooks:
        failures.append(
            "partial operating_brand implementation detected; run --require-runtime and finish every critical surface"
        )
    if require_runtime and missing_hooks:
        failures.extend(f"missing operating_brand hook: {path}" for path in missing_hooks)

    if not require_runtime and not runtime_hits:
        warnings.append(
            "runtime operating_brand support is not implemented; safe claim is docs-only guard, not multi-brand runtime readiness"
        )

    return {
        "ok": not failures,
        "mode": "require_runtime" if require_runtime else "guard_only",
        "allowed_operating_brands": list(ALLOWED_OPERATING_BRANDS),
        "guard_docs": guard_doc_results["docs"],
        "critical_runtime_surface_count": len(CRITICAL_RUNTIME_SURFACES),
        "runtime_status": runtime_status,
        "runtime_operating_brand_hits": [hit.__dict__ for hit in runtime_hits],
        "missing_runtime_hooks": missing_hooks,
        "safe_claim": (
            "runtime-ready operating_brand support"
            if runtime_status == "implemented"
            else "docs-only three-brand guard; runtime operating_brand support remains blocked"
        ),
        "mutation": "none",
        "external_calls": "none",
        "warnings": warnings,
        "failures": failures,
    }


def _guard_docs() -> dict[str, object]:
    failures: list[str] = []
    docs: dict[str, object] = {}
    required_terms = [*ALLOWED_OPERATING_BRANDS]

    for rel_path in GUARD_DOCS:
        path = PROJECT_ROOT / rel_path
        if not path.exists():
            failures.append(f"missing guard doc: {rel_path}")
            docs[rel_path] = {"exists": False}
            continue
        text = path.read_text(encoding="utf-8")
        missing_terms = [term for term in required_terms if term not in text]
        if missing_terms:
            failures.append(f"{rel_path} missing guard terms: {', '.join(missing_terms)}")
        if "fourth" not in text.lower():
            failures.append(f"{rel_path} missing fourth-brand scope guard")
        docs[rel_path] = {
            "exists": True,
            "missing_terms": missing_terms,
        }

    return {"docs": docs, "failures": failures}


def _runtime_operating_brand_hits() -> list[FileHit]:
    hits: list[FileHit] = []
    for rel_path in CRITICAL_RUNTIME_SURFACES:
        path = PROJECT_ROOT / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        count = text.count("operating_brand")
        if count:
            hits.append(FileHit(path=rel_path, count=count))
    return hits


def print_summary(result: dict[str, object]) -> None:
    status = "PASS" if result["ok"] else "FAIL"
    print(f"[OPERATING BRAND EXPOSURE CONTRACT] {status}")
    print(f"  mode: {result['mode']}")
    print(f"  runtime_status: {result['runtime_status']}")
    print(f"  safe_claim: {result['safe_claim']}")
    print(f"  critical_runtime_surface_count: {result['critical_runtime_surface_count']}")
    print(f"  mutation: {result['mutation']}")
    for warning in result.get("warnings") or []:
        print(f"  WARNING: {warning}")
    for failure in result.get("failures") or []:
        print(f"  FAIL: {failure}")


if __name__ == "__main__":
    sys.exit(main())
