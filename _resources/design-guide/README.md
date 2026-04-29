# LT Design Guide — Reference, Not Gospel

**What this is:** the synthesis output from the Locally Twisted design competition (2026-04-26). Seven Opus instances ran in parallel against a brief, GL picked a hybrid synthesis (D3 + D5 + D7 grafted onto LT's existing visual language).

**How to use it:**

- Treat this as **design inspiration and taste calibration**, not as a contract to implement verbatim
- Read `synthesis/voice.md`, `synthesis/mood.md`, `synthesis/rationale.md` to absorb the design language
- View `screenshots/*.png` to see what the synthesis renders as (landing, lookbook, shop, balloon-twisting × desktop + mobile)
- Use `synthesis/*.tsx` and `synthesis/globals.css` as a structural reference for hierarchy, spacing, component shapes — not a literal copy target. (The synthesis was built in Next.js TSX; the LT site is Frappe Jinja.)
- The brand foundation in `_resources/STYLE-GUIDE.md` remains the source of truth for tokens (colors, fonts, spacing). The synthesis works *within* that foundation — it doesn't override it.

**What's here:**

| Path | What it is |
|---|---|
| `synthesis/SYNTHESIS-BRIEF.md` | The mandate the synthesis instance was given |
| `synthesis/SYNTHESIS-COMPLETE.md` | The synthesis instance's closing notes |
| `synthesis/rationale.md` | Why each design choice was made |
| `synthesis/mood.md` | Visual mood + atmosphere notes |
| `synthesis/voice.md` | Copy voice rules ("Quiet Confidence") |
| `synthesis/menu.md` | Top nav + IA decisions |
| `synthesis/landing/page.tsx` | Landing page synthesis (TSX reference) |
| `synthesis/lookbook/page.tsx` | Lookbook page synthesis |
| `synthesis/shop/page.tsx` | Shop page synthesis |
| `synthesis/balloon-twisting/page.tsx` | Balloon twisting service page synthesis |
| `synthesis/layout.tsx` | Shared layout (header/footer reference) |
| `synthesis/globals.css` | Global token + base styles reference |
| `screenshots/*.png` | 8 rendered shots GL approved (4 pages × 2 viewports) |
| `screenshots/RENDER-REPORT.md` | The synthesis instance's render notes |

**Provenance:** Originally produced at `C:\Users\baenb\projects\zoho-locally-twisted\gallery\` during the 2026-04-26 design competition. WINNER.md is preserved in this project's decisions log entry (2026-04-29 — design guide imported). The original `zoho-locally-twisted` directory will be deleted.

**Why this guide isn't gospel:** GL's directive 2026-04-29 — *"they should live in our directory as a design guide, not as gospel."* The synthesis is one well-considered take. When the synthesis and LT's existing voice / brand / accessibility constraints conflict, the constraints win. When the synthesis suggests a structural pattern (eyebrow-cap typography, generous whitespace, full-bleed bands, soft cards with rounded corners) and the LT pages don't have it, the synthesis is the right reference to reach for.
