---
id: lt-balloon-color-generated-hero-contract
name: LT Balloon Color Generated Hero Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted generated balloon/category hero imagery and color-matching source docs
currently_true: local_only
verification_level: 2
last_verified: 2026-05-22
evidence_quality: direct
successful_uses: 1
failed_uses: 1
regressions: 0
depends_on:
  - compact-hero-contract
  - frappe-sitewide-visual-overhaul
used_by:
  - shop-category-hero-imagery-2026-05-22
tags:
  - Locally Twisted
  - balloon colors
  - generated images
  - category heroes
  - style guide
---

# LT Balloon Color Generated Hero Contract

Use this recipe when generating, replacing, or auditing LT balloon/category
hero images, especially `/shop-items/<group>` compact heroes or future color
chart visuals.

## Contract

Balloon colors are product truth. For generated images, the authority order is:

1. owner-approved swatch image and exact source balloon color name.
2. Supplier-style balloon color naming in the prompt.
3. Best web-match hex only as a screen/document approximation.

Hex values must not be the only generation brief. If a generated image does
not look like the source swatches or invents signs/text, reject or regenerate
it before route proof.

## Source Files

- `_resources/STYLE-GUIDE-BALLOON-COLOR-ADDENDUM.md`
- `_resources/generated-hero-sources/2026-05-22/shop-category-generated-hero-manifest.json`
- `apps/locally_twisted/locally_twisted/catalog_contract/color_swatch_map.json`
- `apps/locally_twisted/locally_twisted/public/images/color-swatches/catalog/`
- `scripts/setup/generate_shop_category_heroes.py`
- `scripts/verify/shop_category_hero_images.spec.js`

## Procedure

1. Write or refresh a research brief before generation.
2. Pick category shape and palette names from the color addendum.
3. Include owner-approved swatch refs in the generation manifest/prompt. Do not
   print or commit API keys.
4. Generate wide source art and breakpoint crops with
   `scripts/setup/generate_shop_category_heroes.py`.
5. Review the source contact sheet for category shape, palette match, blank
   backgrounds, no fake text, no signage, and no customer/proof-photo claims.
6. Map only approved crops into the route CSS, then bump the Frappe CSS
   cache-bust.
7. Clear website cache and run the verifiers below before saying the route
   hero is fixed.

## Commands

```powershell
python scripts\verify\color_swatch_contract.py
python -m py_compile scripts\setup\generate_shop_category_heroes.py
python scripts\dev\clear_website_cache.py
scripts\verify\run_playwright.cmd test scripts/verify/shop_category_hero_images.spec.js --reporter=line --workers=1
npm run test:public-assets
npm run test:container-contract -- --grep "seasonal-category|shop"
npm run test:layout-fit -- --grep "seasonal-category|shop"
```

## Guardrails

- This recipe does not approve ERPNext Item Group `image` fields. Use
  `erpnext-category-media-approval` for DB category images.
- Do not use proof/portfolio photos as generic hero art unless the route is
  explicitly a proof surface.
- Do not leave generated fake words, labels, logos, signage, posters, or
  watermark-like marks in a hero.
- Do not reuse one generic shop lifestyle image across all category routes.
- Do not treat generated art as a literal installed-work photo.
- Do not stage or deploy live from this recipe; it produces local source and
  verification evidence for GL review.

## LT Receipt

On 2026-05-22, category route heroes were mapped to generated WebP crops. On
2026-05-24, the route set was refreshed to the 8 active primary categories,
including a dedicated generated Photo Ops & Backdrops asset and source-manifest
entry. The generation manifest records category shape, owner-approved color
names, swatch refs, and the "not hex authority" rule. The focused Playwright
verifier checks rendered route image assignments and hero heights for the
active route set; it does not parse the generation manifest.
