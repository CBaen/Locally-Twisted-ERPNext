#!/usr/bin/env python3
"""Build a static comparison HTML with all SVGs inlined.

No JS, no fetch — just direct DOM. Safer and renders deterministically.
"""
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
PACKS = ["lucide", "phosphor", "heroicons"]
ICONS = ["truck", "shopping-cart", "phone", "map-pin", "calendar"]


def load_svg(pack: str, name: str) -> str:
    p = HERE / pack / f"{name}.svg"
    return p.read_text(encoding="utf-8").strip()


def size_svg(svg: str, w: int, h: int) -> str:
    """Force width/height attrs on the root <svg>."""
    svg = re.sub(r'\s(width|height)="[^"]*"', "", svg, count=2)
    return svg.replace("<svg", f'<svg width="{w}" height="{h}"', 1)


def main():
    cells = {}  # (pack, icon) -> svg content
    for pack in PACKS:
        for icon in ICONS:
            cells[(pack, icon)] = load_svg(pack, icon)

    def grid_cell(pack: str, icon: str) -> str:
        svg = size_svg(cells[(pack, icon)], 36, 36)
        solid_class = " solid" if pack == "phosphor" else ""
        return f'<div class="cell"><div class="icon-display{solid_class}">{svg}</div></div>'

    def truck_row(pack: str, label: str) -> str:
        svg_default = size_svg(cells[(pack, "truck")], 32, 32)
        svg_flipped = size_svg(cells[(pack, "truck")], 32, 32).replace(
            "<svg", '<svg class="flipped"', 1
        )
        return f"""
  <div class="truck-row">
    <div class="pack-label">{label}</div>
    <div class="truck-cell">
      {svg_default}
      <span class="strip-text">Bringing celebration to the Wasatch Front since 1998</span>
      <span class="truck-orientation">DEFAULT</span>
    </div>
    <div class="truck-cell">
      {svg_flipped}
      <span class="strip-text">Bringing celebration to the Wasatch Front since 1998</span>
      <span class="truck-orientation">scaleX(-1)</span>
    </div>
  </div>"""

    def real_strip(pack: str, label: str) -> str:
        truck = size_svg(cells[(pack, "truck")], 18, 18)
        cart = size_svg(cells[(pack, "shopping-cart")], 18, 18)
        return f"""
  <div class="real-row">
    <div class="label">{label}</div>
    <div class="real-strip">{truck}<span>Bringing celebration to the Wasatch Front since 1998</span></div>
    <div class="real-strip" style="margin-left:auto;">{cart}<span>Cart</span></div>
  </div>"""

    grid_html = "\n  ".join(
        [
            '<div class="header-cell"></div>',
            *[f'<div class="header-cell">{i}</div>' for i in ICONS],
        ]
    )
    for pack, label, meta in [
        ("lucide", "Lucide", "Stroke 2 px<br>~1,500 icons<br>MIT &middot; Feather lineage"),
        ("phosphor", "Phosphor (regular)", "Stroke 1.5 px<br>~9,000 icons (6 weights)<br>MIT &middot; broadest set"),
        ("heroicons", "Heroicons (outline)", "Stroke 1.5 px<br>~300 icons<br>MIT &middot; Tailwind set"),
    ]:
        grid_html += (
            f'\n  <div class="pack-cell"><div class="pack-name">{label}</div>'
            f'<div class="pack-meta">{meta}</div></div>'
        )
        for icon in ICONS:
            grid_html += "\n  " + grid_cell(pack, icon)

    truck_html = (
        truck_row("lucide", "Lucide")
        + truck_row("phosphor", "Phosphor")
        + truck_row("heroicons", "Heroicons")
    )

    real_html = (
        real_strip("lucide", "Lucide")
        + real_strip("phosphor", "Phosphor")
        + real_strip("heroicons", "Heroicons")
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Icon Pack Comparison</title>
<style>
  :root {{
    --lt-near-black: #1A1A1A;
    --lt-soft-gray: #555;
    --lt-teal: #008080;
    --lt-blue-tint: #f0f6f8;
    --lt-white: #ffffff;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    font-family: 'Raleway', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--lt-white);
    color: var(--lt-near-black);
    padding: 32px 48px 64px;
  }}
  h1 {{
    font-family: Georgia, serif;
    font-weight: 400;
    font-size: 28px;
    margin: 0 0 4px 0;
  }}
  h2 {{
    font-family: Georgia, serif;
    font-weight: 400;
    font-size: 22px;
    margin: 0 0 4px 0;
  }}
  .subtitle {{
    color: var(--lt-soft-gray);
    margin-bottom: 28px;
    font-size: 14px;
  }}
  .grid {{
    display: grid;
    grid-template-columns: 180px repeat(5, 1fr);
    border-top: 1px solid #eee;
    border-left: 1px solid #eee;
  }}
  .cell, .header-cell, .pack-cell {{
    padding: 18px 12px;
    border-right: 1px solid #eee;
    border-bottom: 1px solid #eee;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background: var(--lt-white);
  }}
  .header-cell {{
    background: #fafafa;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--lt-soft-gray);
  }}
  .pack-cell {{
    background: #fafafa;
    align-items: flex-start;
    text-align: left;
    line-height: 1.4;
  }}
  .pack-name {{ font-weight: 600; font-size: 15px; }}
  .pack-meta {{ font-size: 11px; color: var(--lt-soft-gray); }}
  .icon-display {{
    color: var(--lt-near-black);
    width: 36px;
    height: 36px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }}
  .icon-display svg {{ width: 36px; height: 36px; stroke: currentColor; fill: none; stroke-width: 2; }}
  .icon-display.solid svg {{ fill: currentColor; stroke: none; }}

  .truck-section {{ margin-top: 56px; padding: 24px; background: var(--lt-blue-tint); border-radius: 4px; }}
  .truck-row {{ display: grid; grid-template-columns: 140px repeat(2, 1fr); gap: 12px; align-items: center; }}
  .truck-row + .truck-row {{ margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(0,0,0,0.06); }}
  .truck-row .pack-label {{ font-weight: 600; font-size: 14px; }}
  .truck-cell {{
    display: flex; align-items: center; gap: 12px;
    padding: 12px; background: var(--lt-white); border-radius: 4px;
  }}
  .truck-cell svg {{ stroke: currentColor; fill: none; stroke-width: 2; color: var(--lt-near-black); flex-shrink: 0; }}
  .truck-cell .strip-text {{ font-size: 14px; color: var(--lt-soft-gray); flex: 1; }}
  .truck-cell svg.flipped {{ transform: scaleX(-1); }}
  .truck-orientation {{ font-size: 10px; color: #999; font-family: ui-monospace, monospace; }}
  /* Phosphor is fill-based */
  .truck-row:nth-child(3) .truck-cell svg {{ fill: currentColor; stroke: none; }}

  .at-real-size {{ margin-top: 56px; padding: 24px; background: #fafafa; border-radius: 4px; }}
  .real-row {{ display: flex; align-items: center; gap: 16px; padding: 12px 0; border-bottom: 1px solid #eee; }}
  .real-row:last-child {{ border-bottom: none; }}
  .real-row .label {{
    width: 90px; font-size: 12px; font-weight: 600;
    color: var(--lt-soft-gray); text-transform: uppercase; letter-spacing: 0.05em;
  }}
  .real-strip {{
    display: inline-flex; align-items: center; gap: 8px;
    font-family: 'Raleway', sans-serif; font-size: 14px; font-weight: 500;
    color: var(--lt-soft-gray);
  }}
  .real-strip svg {{ stroke: currentColor; fill: none; stroke-width: 2; flex-shrink: 0; }}
  .real-row:nth-child(3) .real-strip svg {{ fill: currentColor; stroke: none; }}
</style>
</head>
<body>

<h1>Icon pack comparison &mdash; Locally Twisted</h1>
<p class="subtitle">5 representative icons rendered at 36 px against a white background. Color uses currentColor (near-black). Existing menu.svg is 2 px stroke for reference.</p>

<div class="grid">
  {grid_html}
</div>

<div class="truck-section">
  <h2>Truck direction &mdash; default and mirrored</h2>
  <p class="subtitle">"The truck should be heading towards the company." The brand logo sits to the right of the strip, so the cab needs to face right. Showing each pack's default plus a CSS-mirrored version (<code>transform: scaleX(-1)</code>).</p>
  {truck_html}
</div>

<div class="at-real-size">
  <h2>At real header size (18 px) &mdash; utility strip preview</h2>
  <p class="subtitle">Each pack's truck and cart paired with the actual delivery copy and "Cart" link, scaled to header size.</p>
  {real_html}
</div>

</body>
</html>
"""
    out = HERE / "compare.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote: {out}  ({len(html)} chars)")


if __name__ == "__main__":
    main()
