"""Tight closeup of the desktop header Contact Us button + computed styles."""
from playwright.sync_api import sync_playwright
from pathlib import Path

OUT = Path("output/playwright/lt-contact-cta-closeup.png")
OUT.parent.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1366, "height": 900})
    page = ctx.new_page()
    page.goto("http://localhost:8081/contact", wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(800)

    cta = page.locator(".lt-utility-bar__cta").first
    cta.scroll_into_view_if_needed()
    bbox = cta.bounding_box()
    print("CTA bounding box:", bbox)

    # Tight screenshot of just the button + a margin for context
    if bbox:
        page.screenshot(
            path=str(OUT),
            clip={
                "x": max(0, bbox["x"] - 80),
                "y": max(0, bbox["y"] - 20),
                "width": min(1366, bbox["width"] + 160),
                "height": bbox["height"] + 40,
            },
        )
        print("saved:", OUT)

    # Computed styles that affect text centering
    styles = cta.evaluate("""el => {
        const cs = getComputedStyle(el);
        return {
            tag: el.tagName,
            innerText: el.innerText,
            display: cs.display,
            textAlign: cs.textAlign,
            justifyContent: cs.justifyContent,
            alignItems: cs.alignItems,
            paddingTop: cs.paddingTop,
            paddingRight: cs.paddingRight,
            paddingBottom: cs.paddingBottom,
            paddingLeft: cs.paddingLeft,
            lineHeight: cs.lineHeight,
            fontSize: cs.fontSize,
            width: cs.width,
            height: cs.height,
        };
    }""")
    for k, v in styles.items():
        print(f"  {k}: {v}")

    browser.close()
