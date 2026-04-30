"""Phase 4 verification — chrome rebuild screenshots.

Captures viewport-only screenshots of key routes at desktop + mobile so the
orchestrator can read them and compare against the Hetzner mirror.

Saves to _resources/audit-2026-04-30-chrome/<route>-<viewport>.png + a JSON
report of console errors per page.
"""
from __future__ import annotations

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "_resources" / "audit-2026-04-30-chrome"
OUT.mkdir(parents=True, exist_ok=True)

ROUTES = [
    ("home", "/"),
    ("book", "/book"),
    ("shop", "/shop"),
]
VIEWPORTS = [
    ("desktop", 1280, 800),
    ("mobile", 375, 667),
]
BASE = "http://localhost:8081"


def main() -> int:
    report = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for vp_name, vw, vh in VIEWPORTS:
            ctx = browser.new_context(viewport={"width": vw, "height": vh})
            page = ctx.new_page()
            errors = []
            page.on("pageerror", lambda exc: errors.append(f"PAGEERROR: {exc}"))
            page.on("console", lambda msg: errors.append(f"CONSOLE.{msg.type}: {msg.text}") if msg.type in ("error", "warning") else None)
            for route_slug, route_path in ROUTES:
                key = f"{route_slug}-{vp_name}"
                errors.clear()
                try:
                    page.goto(BASE + route_path, timeout=30000, wait_until="networkidle")
                except Exception as e:
                    report[key] = {"status": "load_failed", "error": str(e)}
                    continue
                screenshot_path = OUT / f"{key}.png"
                # viewport-only (NOT full_page=True per project convention)
                page.screenshot(path=str(screenshot_path))
                # Extract a couple of DOM facts so the report has signal
                try:
                    has_lt_header = page.locator(".lt-header").count() > 0
                except Exception:
                    has_lt_header = False
                try:
                    has_lt_footer = page.locator(".lt-footer").count() > 0
                except Exception:
                    has_lt_footer = False
                try:
                    has_lt_megamenu = page.locator(".lt-header__mega").count()
                except Exception:
                    has_lt_megamenu = 0
                try:
                    drawer_visible = page.locator(".lt-header__mobile-nav-collapse").is_visible()
                except Exception:
                    drawer_visible = None
                report[key] = {
                    "status": "ok",
                    "screenshot": str(screenshot_path.relative_to(ROOT)),
                    "viewport": f"{vw}x{vh}",
                    "has_lt_header": has_lt_header,
                    "has_lt_footer": has_lt_footer,
                    "lt_mega_panel_count": has_lt_megamenu,
                    "mobile_drawer_visible": drawer_visible,
                    "errors": list(errors),
                }
            ctx.close()
        browser.close()

    report_path = OUT / "audit-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nAudit report: {report_path}")
    for k, v in report.items():
        if v["status"] != "ok":
            print(f"  FAIL {k}: {v.get('error')}")
            continue
        err_count = len(v.get("errors", []))
        flags = []
        if not v["has_lt_header"]: flags.append("NO_HEADER")
        if not v["has_lt_footer"]: flags.append("NO_FOOTER")
        if v["mobile_drawer_visible"] is True and "mobile" in k: flags.append("DRAWER_VISIBLE_AT_LOAD")
        if "desktop" in k and v["lt_mega_panel_count"] == 0: flags.append("NO_MEGA_PANELS")
        flag_str = " ".join(flags) if flags else "OK"
        print(f"  {k}: {flag_str}  errors={err_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
