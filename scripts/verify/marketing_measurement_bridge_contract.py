#!/usr/bin/env python3
"""Verify LT's disabled-by-default marketing measurement bridge."""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "apps" / "locally_twisted" / "locally_twisted"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_python_contract() -> None:
    sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))
    module = importlib.import_module("locally_twisted.marketing_measurement")
    attribution = module.normalize_public_attribution(
        json.dumps(
            {
                "utm_source": "Google Ads!!!",
                "utm_medium": "cpc",
                "utm_campaign": "arches summer",
                "utm_term": "balloon arch near me",
                "utm_content": "headline-a",
                "landing_path": "/contact?utm_source=Google",
                "referrer": "https://example.com/path?secret=remove",
                "email": "should-not-pass@example.com",
            }
        )
    )
    assert_true(attribution["utm_source"] == "Google Ads", "utm_source should be sanitized")
    assert_true("email" not in attribution, "raw customer fields must not pass through attribution")
    assert_true(attribution["landing_path"] == "/contact", "landing path should strip query string")
    assert_true(attribution["referrer"] == "https://example.com/path", "referrer should strip query string")

    envelope = module.build_no_send_event_envelope(
        event_name="generate_lead",
        source_record="CRM-LEAD-TEST",
        attribution=attribution,
        value=25,
        currency="USD",
    )
    assert_true(envelope["send_enabled"] is False, "event envelopes must default to no-send")
    assert_true(envelope["dedupe_id"] == "lead:CRM-LEAD-TEST", "Lead dedupe id should be stable")
    assert_true(envelope["event_name"] == "generate_lead", "lead envelope event should be GA4-compatible")


def check_browser_bridge_source() -> None:
    source = (APP / "public" / "js" / "lt-marketing-bridge.js").read_text(encoding="utf-8")
    forbidden = ("gtag(", "fbq(", "connect.facebook.net", "googletagmanager.com", "google-analytics.com")
    for marker in forbidden:
        assert_true(marker not in source, f"disabled bridge must not contain live tag marker {marker!r}")
    assert_true("lt_marketing_attribution" in source, "bridge should attach attribution to public forms")
    assert_true("sessionStorage" in source, "bridge should persist attribution for the session")


def check_hooks_include() -> None:
    hooks = (APP / "hooks.py").read_text(encoding="utf-8")
    assert_true("lt-marketing-bridge.js" in hooks, "marketing bridge script must be included on public pages")
    assert_true(
        "lt-marketing-measurement.js" in hooks,
        "consent-gated marketing measurement script must be included on public pages",
    )


def check_ga4_loader_source() -> None:
    source = (APP / "public" / "js" / "lt-marketing-measurement.js").read_text(encoding="utf-8")
    base = (APP / "templates" / "base.html").read_text(encoding="utf-8")
    assert_true(
        "lt-marketing-tracking-config" in base,
        "base template should expose safe public tracking config",
    )
    assert_true("G-0Z0WY5XQRB" in source, "GA4 loader should preserve the verified LT measurement ID fallback")
    assert_true("lt-marketing-tracking-config" in source, "GA4 loader should read field-based tracking config")
    assert_true("gtmContainerId" in source, "measurement loader should support GTM container IDs")
    assert_true("googleAdsConversionId" in source, "measurement loader should support Google Ads conversion IDs")
    assert_true("hasAcceptedOptional" in source, "GA4 loader must honor optional cookie/tracking consent")
    assert_true("lt-cookie-consent" in source, "GA4 loader must react when a visitor accepts tracking")
    assert_true("send_page_view" in source, "GA4 loader should send a page view after consent")
    assert_true("fbq(" not in source, "measurement loader must not include direct Meta Pixel before Meta is approved")


def check_contact_submit_integration() -> None:
    book = (APP / "www" / "book.py").read_text(encoding="utf-8")
    assert_true("marketing_measurement" in book, "book.py should import marketing measurement helpers")
    assert_true("ATTRIBUTION_FORM_FIELD" in book, "submit path should read attribution payload")
    assert_true("record_lead_attribution_note" in book, "submit path should record attribution on the new Lead")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    checks = [
        check_python_contract,
        check_browser_bridge_source,
        check_ga4_loader_source,
        check_hooks_include,
        check_contact_submit_integration,
    ]
    failures: list[str] = []
    for check in checks:
        try:
            check()
            print(f"[PASS] {check.__name__}")
        except Exception as exc:
            failures.append(f"{check.__name__}: {exc}")
            print(f"[FAIL] {check.__name__}: {exc}")
    if failures:
        print("\n[MARKETING MEASUREMENT BRIDGE CONTRACT] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("\n[MARKETING MEASUREMENT BRIDGE CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
