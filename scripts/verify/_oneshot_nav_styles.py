"""Diagnose: exact computed styles for nav links — default + hover state."""
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://localhost:8081/"


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1366, "height": 900})
        page = ctx.new_page()
        page.goto(URL, wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(1000)

        # Find candidate nav link selectors
        candidates = [
            ".navbar a",
            "header a",
            ".lt-nav a",
            ".lt-header a",
            ".navbar-nav .nav-link",
            "nav a",
        ]
        for sel in candidates:
            count = page.locator(sel).count()
            if count > 0:
                print(f"✓ {sel}: {count} matches")

        # Pick the most-likely nav link element by looking for visible top-of-page links
        nav_links = page.evaluate("""() => {
          const out = [];
          document.querySelectorAll('a').forEach(el => {
            const r = el.getBoundingClientRect();
            const txt = el.innerText.trim();
            if (r.top < 200 && r.width > 30 && r.height > 0 && txt.length > 1 && txt.length < 60) {
              const cs = getComputedStyle(el);
              out.push({
                text: txt,
                tag_path: el.tagName + (el.className ? '.' + el.className.split(' ').slice(0,3).join('.') : ''),
                parent_path: el.parentElement.tagName + (el.parentElement.className ? '.' + el.parentElement.className.split(' ').slice(0,2).join('.') : ''),
                top: Math.round(r.top),
                left: Math.round(r.left),
                font_family: cs.fontFamily,
                font_size: cs.fontSize,
                font_weight: cs.fontWeight,
                text_transform: cs.textTransform,
                letter_spacing: cs.letterSpacing,
                color: cs.color,
                text_decoration: cs.textDecoration,
              });
            }
          });
          return out;
        }""")
        print("\n=== TOP-OF-PAGE LINKS (default state) ===")
        for ln in nav_links:
            print(f"  [{ln['top']:>3},{ln['left']:>4}] '{ln['text'][:35]:35s}' "
                  f"font={ln['font_family'].split(',')[0]:25s} sz={ln['font_size']:6s} "
                  f"wt={ln['font_weight']:3s} tt={ln['text_transform']:10s} "
                  f"color={ln['color']:18s} dec={ln['text_decoration'][:25]}")

        # Hover state for the first menu-style link
        first_menu_link = None
        for ln in nav_links:
            if ln['text'].strip() and ln['top'] > 50 and ln['top'] < 150 and ln['text'] not in ('Sign In', 'Cart'):
                first_menu_link = ln
                break

        if first_menu_link:
            print(f"\n=== HOVER STATE on '{first_menu_link['text']}' ===")
            link = page.locator(f"a:has-text('{first_menu_link['text']}')").first
            link.hover()
            page.wait_for_timeout(400)
            hover_styles = link.evaluate("""el => {
              const cs = getComputedStyle(el);
              return {
                color: cs.color,
                text_decoration: cs.textDecoration,
                text_decoration_color: cs.textDecorationColor,
                text_decoration_thickness: cs.textDecorationThickness,
                background: cs.backgroundColor,
                border_bottom: cs.borderBottom,
              };
            }""")
            for k, v in hover_styles.items():
                print(f"  {k}: {v}")

            # Crop the nav with hover state captured
            page.screenshot(path="C:/Users/baenb/.claude/lt-nav-hover.png",
                          clip={"x": 0, "y": 0, "width": 1366, "height": 200})
            print(f"\n  Saved hover screenshot: C:/Users/baenb/.claude/lt-nav-hover.png")

        b.close()


if __name__ == "__main__":
    main()
