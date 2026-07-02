"""One-shot: report computed styles for hero title + crop hero region.

Tells us WHICH font is actually rendering on the cycling hero title and
where every text-decoration: underline is firing on the homepage.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://localhost:8081/"
OUT = Path("output/playwright")
OUT.mkdir(parents=True, exist_ok=True)


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1366, "height": 900})
        page = ctx.new_page()
        page.goto(URL, wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(1500)

        # Hero title computed styles
        title = page.locator(".lt-hero__title").first
        if title.count() == 0:
            title = page.locator("h1, h2").first
        styles = title.evaluate("""el => {
          const cs = getComputedStyle(el);
          return {
            tag: el.tagName,
            text: el.innerText,
            font_family: cs.fontFamily,
            font_size: cs.fontSize,
            font_weight: cs.fontWeight,
            font_style: cs.fontStyle,
            color: cs.color,
            text_decoration: cs.textDecoration,
          };
        }""")
        print("HERO TITLE (.lt-hero__title):")
        for k, v in styles.items():
            print(f"  {k}: {v}")

        # Underlined elements visible on page
        decorations = page.evaluate("""() => {
          const out = [];
          document.querySelectorAll('a, p, span, h1, h2, h3, h4, h5, h6, li, button').forEach(el => {
            const cs = getComputedStyle(el);
            if (cs.textDecorationLine && cs.textDecorationLine.includes('underline')) {
              const rect = el.getBoundingClientRect();
              if (rect.width > 0 && rect.height > 0 && el.innerText.trim()) {
                out.push({
                  selector: el.tagName.toLowerCase() + (el.className ? '.' + el.className.split(' ').slice(0, 2).join('.') : ''),
                  text: el.innerText.trim().slice(0, 60),
                  decoration: cs.textDecoration,
                  font: cs.fontFamily.split(',')[0].replace(/['"]/g, ''),
                });
              }
            }
          });
          return out.slice(0, 20);
        }""")
        print("\nUNDERLINED elements (first 20):")
        for d in decorations:
            print(f"  {d['selector']:50s} → {d['decoration'][:40]:42s} | '{d['text'][:40]}'")

        # Crop just the hero region (top 700px)
        page.screenshot(path=str(OUT / "lt-hero-crop.png"), clip={"x": 0, "y": 0, "width": 1366, "height": 700})
        print(f"\nSaved hero crop: {OUT / 'lt-hero-crop.png'}")

        # Same crop on Hetzner
        page.goto("http://5.78.136.133/", wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(1000)
        page.screenshot(path=str(OUT / "hetzner-hero-crop.png"), clip={"x": 0, "y": 0, "width": 1366, "height": 700})
        print(f"Saved Hetzner hero crop: {OUT / 'hetzner-hero-crop.png'}")

        b.close()


if __name__ == "__main__":
    main()
