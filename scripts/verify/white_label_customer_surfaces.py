#!/usr/bin/env python3
"""Fail-loud white-label checks for customer/client-facing LT surfaces.

This verifier is intentionally narrower than a repository-wide grep. Backend code
must still use Frappe/ERPNext DocTypes internally; this gate checks surfaces that
can render or be reviewed as customer/client output.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT / "apps" / "locally_twisted" / "locally_twisted" / "outbound_documents" / "templates"
PREVIEW_ROOT = ROOT / "output" / "playwright"

STRICT_PLATFORM_RE = re.compile(
    r"\b(?:ERPNext|Frappe|Odoo)\b|Built on Frappe|frappe\.io|erpnext\.com|odoo\.com",
    re.IGNORECASE,
)

RENDERED_SOURCE_LEAK_RE = re.compile(
    r"Built on Frappe|name=[\"']generator[\"']\s+content=[\"']frappe[\"']|custom Frappe app|frappe\.io/erpnext",
    re.IGNORECASE,
)

# Terms that are valid backend machinery, but should not appear in customer-facing
# document body copy when a friendlier label exists. Accounting words like
# "invoice" and "quote" are deliberately not banned.
CUSTOMER_BACKEND_RE = re.compile(
    r"\b(?:DocType|Payment Entry|Payment Request|Sales Order|Lead|Quotation|Webshop|Shopping Cart|Administrator|Desk)\b",
)

PUBLIC_ROUTES = (
    "/",
    "/corporate-events",
    "/schools-campuses",
    "/civic-community",
    "/private-celebrations",
    "/balloon-twisting-and-face-painting",
    "/contact",
    "/faq",
    "/portfolio",
    "/ready-to-order-paused",
    "/search",
    "/login",
    "/checkout",
    "/thank-you?status=payment-check",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="", help="Optional local site base URL for rendered route checks, e.g. http://localhost:8081")
    parser.add_argument("--preview-dir", default="", help="Optional outbound preview directory to scan")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()

    failures: list[dict[str, str]] = []
    evidence: dict[str, object] = {
        "template_dir": str(TEMPLATE_DIR),
        "checked_templates": [],
        "checked_preview_html": [],
        "checked_routes": [],
    }

    check_outbound_template_bodies(failures, evidence)
    check_preview_html(args.preview_dir, failures, evidence)
    if args.base_url:
        check_rendered_routes(args.base_url.rstrip("/"), failures, evidence)

    result = {"ok": not failures, "failures": failures, "evidence": evidence}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if failures:
            print("WHITE-LABEL CUSTOMER SURFACE CHECK FAILED")
            for failure in failures:
                print(f"- {failure['surface']}: {failure['term']} :: {failure['snippet']}")
        else:
            print("WHITE-LABEL CUSTOMER SURFACE CHECK PASSED")
            print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if not failures else 1


def check_outbound_template_bodies(failures: list[dict[str, str]], evidence: dict[str, object]) -> None:
    if not TEMPLATE_DIR.exists():
        failures.append({"surface": str(TEMPLATE_DIR), "term": "missing", "snippet": "Outbound document template directory is missing"})
        return
    checked: list[str] = []
    for path in sorted(TEMPLATE_DIR.glob("*.md")):
        body = strip_frontmatter(path.read_text(encoding="utf-8"))
        checked.append(str(path.relative_to(ROOT)))
        scan_text(path.relative_to(ROOT).as_posix() + " body", body, STRICT_PLATFORM_RE, failures)
        scan_text(path.relative_to(ROOT).as_posix() + " body", body, CUSTOMER_BACKEND_RE, failures)
    evidence["checked_templates"] = checked


def check_preview_html(preview_dir: str, failures: list[dict[str, str]], evidence: dict[str, object]) -> None:
    roots: list[Path] = []
    if preview_dir:
        roots.append(Path(preview_dir))
    checked: list[str] = []
    for root in roots:
        if not root.exists():
            failures.append({"surface": str(root), "term": "missing", "snippet": "Requested preview directory is missing"})
            continue
        for path in sorted(root.glob("*.html")):
            text = path.read_text(encoding="utf-8", errors="replace")
            checked.append(str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path))
            scan_text(str(path), text, STRICT_PLATFORM_RE, failures)
            visible = strip_html_noise(text)
            scan_text(str(path) + " visible text", visible, CUSTOMER_BACKEND_RE, failures)
    evidence["checked_preview_html"] = checked


def check_rendered_routes(base_url: str, failures: list[dict[str, str]], evidence: dict[str, object]) -> None:
    checked: list[dict[str, object]] = []
    for route in PUBLIC_ROUTES:
        url = base_url + route
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                status = int(response.status)
                body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            status = int(exc.code)
            body = exc.read().decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001 - verifier should report actionable evidence
            failures.append({"surface": url, "term": "fetch_error", "snippet": repr(exc)})
            continue
        checked.append({"route": route, "status": status, "bytes": len(body)})
        if status >= 500:
            failures.append({"surface": url, "term": f"HTTP {status}", "snippet": "Rendered route returned server error"})
        # Rendered HTML must not expose generator banners/meta or LT-authored
        # framework comments. Framework asset URLs and runtime globals are
        # implementation plumbing, not customer-visible branding.
        scan_text(url + " source", body, RENDERED_SOURCE_LEAK_RE, failures)
        visible = strip_html_noise(body)
        scan_text(url + " visible text", visible, STRICT_PLATFORM_RE, failures)
        scan_text(url + " visible text", visible, CUSTOMER_BACKEND_RE, failures)
    evidence["checked_routes"] = checked


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    return text[end + 5 :]


def strip_html_noise(text: str) -> str:
    text = re.sub(r"<script\b.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def scan_text(surface: str, text: str, pattern: re.Pattern[str], failures: list[dict[str, str]]) -> None:
    for match in pattern.finditer(text):
        start = max(0, match.start() - 70)
        end = min(len(text), match.end() + 70)
        snippet = re.sub(r"\s+", " ", text[start:end]).strip()
        failures.append({"surface": surface, "term": match.group(0), "snippet": snippet})


if __name__ == "__main__":
    sys.exit(main())
