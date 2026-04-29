"""One-shot: capture http://5.78.136.133/ for visual reference comparison.

GL pointed at the Hetzner Odoo deploy as the visual target for nav header
styling (font, underline, heading). This grabs desktop + mobile so we can
diff against localhost:8081 and figure out the exact CSS delta.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://5.78.136.133/"
OUT = Path("C:/Users/baenb/.claude")


def capture(p, viewport, output, *, is_mobile=False):
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport=viewport, is_mobile=is_mobile)
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(1000)
    page.screenshot(path=str(output), full_page=True)

    facts = {
        "title": page.title(),
        "h1_text": page.locator("h1").first.inner_text() if page.locator("h1").count() else None,
        "h1_font": page.locator("h1").first.evaluate("el => getComputedStyle(el).fontFamily") if page.locator("h1").count() else None,
        "h1_size": page.locator("h1").first.evaluate("el => getComputedStyle(el).fontSize") if page.locator("h1").count() else None,
        "h1_weight": page.locator("h1").first.evaluate("el => getComputedStyle(el).fontWeight") if page.locator("h1").count() else None,
        "body_font": page.locator("body").first.evaluate("el => getComputedStyle(el).fontFamily"),
        "nav_link_count": page.locator("nav a, header a").count(),
        "first_nav_link_font": page.locator("nav a, header a").first.evaluate("el => getComputedStyle(el).fontFamily") if page.locator("nav a, header a").count() else None,
        "first_nav_link_decoration": page.locator("nav a, header a").first.evaluate("el => getComputedStyle(el).textDecoration") if page.locator("nav a, header a").count() else None,
        "first_nav_link_color": page.locator("nav a, header a").first.evaluate("el => getComputedStyle(el).color") if page.locator("nav a, header a").count() else None,
        "head_link_fonts": [el.get_attribute("href") for el in page.locator("link[href*='font'], link[href*='Font']").all()],
    }
    browser.close()
    return facts


def main():
    with sync_playwright() as p:
        print("→ Hetzner desktop (1366x900)…")
        d = capture(p, {"width": 1366, "height": 900}, OUT / "hetzner-desktop.png")
        print(f"  saved: {OUT / 'hetzner-desktop.png'}")
        for k, v in d.items():
            print(f"    {k}: {v}")
        print()
        print("→ Hetzner mobile (375x812)…")
        m = capture(p, {"width": 375, "height": 812}, OUT / "hetzner-mobile.png", is_mobile=True)
        print(f"  saved: {OUT / 'hetzner-mobile.png'}")
        for k, v in m.items():
            print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
