# LT Image Set — Phase 1 Placeholders

Generated 2026-04-26 via Together AI's `FLUX.1-schnell`. Source-of-truth prompts are in `.scratch/generate-placeholder-images.py` (re-runnable).

These images are **placeholders for the Phase 1 demo**. Real LT event photography replaces them in a future iteration. Each file maps to a specific slot in the Phase 1 build.

## Map of slot → file → use

### Homepage (Phase 1 Slice 3)

| File | Use | Aspect |
|---|---|---|
| `home-hero.png` | Hero panel — primary visual on landing | 3:2 wide |
| `home-service-decor.png` | Services snapshot card — Balloon Decor | square |
| `home-service-twisting.png` | Services snapshot card — Balloon Twisting | square |
| `home-service-painting.png` | Services snapshot card — Face Painting | square |
| `home-social-proof.png` | "Trusted by Utah's Best Since 1998" panoramic | 2:1 wide |

### Balloon Twisting + Face Painting service page (Phase 1 Slice 4)

| File | Use | Aspect |
|---|---|---|
| `btfp-hero.png` | Hero panel | 3:2 wide |
| `btfp-twisting-detail.png` | "Balloon Twisting" section image | square |
| `btfp-painting-detail.png` | "Face Painting" section image | square |

### Contact page (Phase 1 Slice 5)

| File | Use | Aspect |
|---|---|---|
| `contact-hero.png` | Page hero / banner | 2:1 wide |

### Product detail pages (Phase 1 Slice 8 — 1 image per product per GL directive)

Product **listing** pages (Slice 7) use blank / icon placeholders for cards — only the product detail page gets a real image, per GL 2026-04-26.

| File | Product |
|---|---|
| `product-classic-organic-arch.png` | Classic Organic Arch |
| `product-balloon-garland.png` | Mini Balloon Garland |
| `product-balloon-column.png` | Balloon Column |
| `product-balloon-wall.png` | Balloon Wall |
| `product-helium-bouquet.png` | Helium Bouquet |
| `product-balloon-drop.png` | Balloon Drop |

## Pages with no images (intentional)

- Refund Policy — text-only legal page
- Accessibility statement — text-only legal page
- FAQ — text-only Q&A page
- Cart, checkout — UI-only flow

## Regenerating

The generator script and prompts are in `.scratch/generate-placeholder-images.py`. Re-run any time:

```
python C:/Users/baenb/projects/Built_by_Cameron/_CLIENTS/locally-twisted/.scratch/generate-placeholder-images.py
```

To regenerate ONE slot, pass a substring of its filename:

```
python ...generate-placeholder-images.py home-hero
```

## Replacing with real photography

When real LT event photos arrive, drop them in this folder using the **same filenames**. The site references images by these slot names; no template changes needed for the swap.

Recommended specs for replacements (per `_resources/STYLE-GUIDE.md` "Photography" section):
- Hero / wide images: 1536×1024 (3:2) or 1536×768 (2:1), WebP or JPEG, ≥1200px wide
- Square cards: 1024×1024, WebP or JPEG, ≥600px wide
- Natural, well-lit, real-setting photography (events, homes, venues)
- Utah locations when possible, no heavy filters or saturation

## Capability used

Built using the [`generate-client-image-set`](../../../../.claude/capabilities/recipes/generate-client-image-set.md) recipe and the [`together-image-gen`](../../../../.claude/capabilities/ingredients/together-image-gen.md) ingredient at the agency level.
