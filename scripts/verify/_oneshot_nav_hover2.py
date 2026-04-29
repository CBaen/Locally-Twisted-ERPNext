"""Confirm hover state has no border/underline after the lt-theme.css update."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_context(viewport={"width": 1366, "height": 900}).new_page()
    page.goto("http://localhost:8081/", wait_until="networkidle", timeout=15000)
    page.wait_for_timeout(800)

    link = page.locator(".lt-header__nav-link").first
    pre = link.evaluate("""el => {
      const cs = getComputedStyle(el);
      return {color: cs.color, decoration: cs.textDecoration, border_bottom: cs.borderBottom};
    }""")
    print("DEFAULT:")
    for k, v in pre.items():
        print(f"  {k}: {v}")

    link.hover()
    page.wait_for_timeout(400)

    post = link.evaluate("""el => {
      const cs = getComputedStyle(el);
      return {color: cs.color, decoration: cs.textDecoration, border_bottom: cs.borderBottom};
    }""")
    print("\nHOVER:")
    for k, v in post.items():
        print(f"  {k}: {v}")

    page.screenshot(path="C:/Users/baenb/.claude/lt-nav-hover-after.png",
                  clip={"x": 0, "y": 100, "width": 1366, "height": 150})
    print("\nSaved hover screenshot: C:/Users/baenb/.claude/lt-nav-hover-after.png")

    b.close()
