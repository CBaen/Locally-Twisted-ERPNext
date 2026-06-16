#!/usr/bin/env python3
"""
Playwright screenshot — visual verification before "done."

Takes a screenshot of each configured URL after deploy. Saves to
`<repo>/scripts/verify/_screenshots/<timestamp>/`. Used as the verification
step before any claim that visual work is done.

This gate exists because of the reporting-without-watching pattern that
fired across LT, BBC, and Frappe sessions: an instance declared visual
work "done" before observing it. The 2026-04-26 Slice 2 footer "renders
identically" while empty circles were on screen is the canonical receipt.

Self-contained: no imports outside the standard library + playwright.
"""
import argparse
import sys
import time
from pathlib import Path

from browser_runtime import MissingPlaywright, launch_chromium, require_playwright

def take_screenshots(base_url: str, paths: list[str], output_dir: Path) -> int:
    try:
        sync_playwright, PlaywrightTimeout = require_playwright()
    except MissingPlaywright as exc:
        print(exc)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    fails = 0
    with sync_playwright() as p:
        browser = launch_chromium(p)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        for path in paths:
            url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
            safe_name = path.strip("/").replace("/", "_") or "home"
            screenshot_path = output_dir / f"{safe_name}.png"
            print(f"\n[SCREENSHOT] {url}")
            try:
                page.goto(url, timeout=30000, wait_until="networkidle")
            except PlaywrightTimeout:
                print(f"             FAIL — could not load (timeout)")
                fails += 1
                continue

            # Critical check: is the page non-blank?
            body_text = page.locator("body").inner_text().strip()
            if not body_text:
                print(f"             FAIL — page body is empty (blank-white-page pattern)")
                fails += 1
                continue

            # Critical check: did the CSS load? Asset bundle silent failure
            # would cause the page to render as raw unstyled HTML.
            has_styled_content = page.evaluate("""
                () => {
                    const body = document.body;
                    const styles = window.getComputedStyle(body);
                    const fontFamily = styles.fontFamily;
                    const hasFonts = fontFamily && fontFamily !== 'serif' && fontFamily !== '';
                    const stylesheets = document.styleSheets.length;
                    return { hasFonts, stylesheets };
                }
            """)
            if has_styled_content["stylesheets"] == 0:
                print(f"             FAIL — no stylesheets loaded (asset bundle silent failure pattern)")
                fails += 1
                continue

            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"             PASS — saved {screenshot_path.name}")
            except Exception as e:
                print(f"             FAIL — screenshot capture: {e}")
                fails += 1
        browser.close()

    print(f"\n[SCREENSHOT SUMMARY] saved to {output_dir}")
    if fails == 0:
        print(f"                     All {len(paths)} URLs passed")
        return 0
    print(f"                     {fails} of {len(paths)} URLs FAILED")
    return 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--paths", required=True, help="Comma-separated paths: '/,/book,/blog'")
    parser.add_argument("--output-dir", default=None,
                        help="Where to save screenshots (default: scripts/verify/_screenshots/<timestamp>)")
    args = parser.parse_args()

    paths = [p.strip() for p in args.paths.split(",") if p.strip()]
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        ts = time.strftime("%Y%m%d-%H%M%S")
        output_dir = Path(__file__).resolve().parent / "_screenshots" / ts

    sys.exit(take_screenshots(args.base_url, paths, output_dir))

if __name__ == "__main__":
    main()
