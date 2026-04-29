"""One-shot Playwright verifier for /book.

Mobile + desktop screenshots, conditional-section visibility checks,
and /contact -> /book redirect confirmation. Delete after the
verification round; git history preserves it.
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


OUT = (
    Path(__file__).resolve().parent
    / "_screenshots"
    / time.strftime("book-detail-%Y%m%d-%H%M%S")
)
OUT.mkdir(parents=True, exist_ok=True)


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)

        # MOBILE viewport (375x812 — iPhone X-ish)
        ctx = b.new_context(viewport={"width": 375, "height": 812})
        page = ctx.new_page()
        page.goto("http://localhost:8081/book", wait_until="networkidle", timeout=30000)
        page.screenshot(path=str(OUT / "01-mobile-pristine.png"), full_page=False)
        print("[1] mobile pristine -> 01-mobile-pristine.png")

        # Click Balloon Twisting
        page.locator("#svc_twisting").check()
        page.wait_for_timeout(200)
        twisting_visible = page.locator(
            '[data-visibility-condition="Balloon Twisting"].lt-book__conditional'
        ).is_visible()
        env_visible = page.locator(
            '[data-visibility-comparator="set"].lt-book__conditional'
        ).is_visible()
        print(f"[2] Twisting checked: twisting={twisting_visible}, environment={env_visible}")
        page.locator(".lt-book__services").scroll_into_view_if_needed()
        page.wait_for_timeout(150)
        page.screenshot(path=str(OUT / "02-mobile-twisting.png"), full_page=False)

        page.locator("#svc_decor").check()
        page.wait_for_timeout(200)
        decor_visible = page.locator(
            '[data-visibility-condition="Balloon Decor"].lt-book__conditional'
        ).is_visible()
        print(f"[3] Decor checked: decor={decor_visible}")
        page.screenshot(path=str(OUT / "03-mobile-decor-twisting.png"), full_page=False)
        ctx.close()

        # DESKTOP viewport
        ctx = b.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.goto("http://localhost:8081/book", wait_until="networkidle", timeout=30000)
        page.screenshot(path=str(OUT / "04-desktop-pristine.png"), full_page=False)
        print("[4] desktop pristine -> 04-desktop-pristine.png")

        page.locator("#svc_twisting").check()
        page.locator("#svc_painting").check()
        page.wait_for_timeout(200)
        page.evaluate(
            "document.querySelector('.lt-book__services').scrollIntoView({block: 'center'})"
        )
        page.wait_for_timeout(200)
        page.screenshot(
            path=str(OUT / "05-desktop-twisting-painting.png"), full_page=False
        )
        print("[5] desktop twisting+painting -> 05-desktop-twisting-painting.png")

        # /contact -> /book redirect
        page.goto(
            "http://localhost:8081/contact", wait_until="domcontentloaded", timeout=30000
        )
        landed = page.url
        print(f"[6] /contact lands at -> {landed}")
        assert "/book" in landed, f"Expected /contact to redirect to /book; got {landed}"

        b.close()
    print(f"\nScreenshots: {OUT}")


if __name__ == "__main__":
    main()
