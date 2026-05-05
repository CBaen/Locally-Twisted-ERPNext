# Brand Style Guide Consolidation Workstream

Last updated: 2026-05-05 by Codex.

## Status

Source-of-truth consolidation is complete. The first rendered-site repair pass is complete and verified against the running Frappe site. Final photo/trust-count/content taste approval is still a GL/Jeff review item.

This lane exists so the next design agents do not reopen the retired light-blue/blush design system or the weak generic icon direction while they update the actual pages.

## Outcome

One implementation-grade visual contract for the Locally Twisted rebrand before any broad design swarm touches pages.

The approved target is:

- Civic Celebration for Utah civic/event authority, Americana posture, public-event scale, school/corporate/private-event context, and real installed-work imagery.
- Slate Blue and Berry for palette discipline: ink, deep navy/slate, warm white, brass, stone/sandstone, and berry/crimson action.
- Locally Twisted Brand Direction for the premium quality bar: large serif wordmark feel, disciplined spacing, crisp brass line icons, dark authority bands, and corporate-safe finish.

## Completed This Session

- `_resources/STYLE-GUIDE.md` is now version 4.2 and is the only current visual authority.
- Deleted `_resources/design-guide/` because it conflicted with the approved direction and kept reintroducing old light-blue/blush styling.
- Deleted stale tracked comparison/reference files that pointed future agents back at the retired design:
  - `_resources/shop-recon-2026-04-29.md`
  - `_resources/webshop-state-vs-spec-2026-04-30.md`
  - `_resources/webshop-state-vs-spec-2026-04-30/_scripts/`
  - `_resources/icon-comparison-2026-04-27/`
- Removed the untracked generated `_resources/webshop-state-vs-spec-2026-04-30/` screenshot folder after inventorying it as old generated comparison output.
- Added a custom brass-line SVG icon suite under `apps/locally_twisted/locally_twisted/public/icons/brand/`.
- Retired active app references to old font and pastel tokens: `DM Serif`, `Raleway`, `Montserrat`, `Playfair`, `lt-blush`, `lt-soft-blue`, old `soft-blue`/`light-blue`, UI `blush`, and unresolved `--lt-primary`.
- Updated active agent/workstream/planning docs to point to `_resources/STYLE-GUIDE.md` instead of the deleted design guide.
- Restored the deliberate premium two-level mega menu after GL chose that direction over the simple header.
- Added/served `lt-mega-menu.css`, `lt-page-containment.css`, `lt-product-polish.css`, and `lt-megamenu.js` through `hooks.py`.
- Bumped the theme CSS cache key in `hooks.py` to `20260505-authority-4`.
- Added `/event-balloons` and `/process` as lightweight authority pages so the current primary nav has no dead links.
- Reinstated `navbar_context.py` for menu data and kept `website_context.py` for shop/sidebar defaults.
- Fixed mobile hero spacing, reviews carousel clipping, dark-section heading contrast, portfolio chip wrapping, footer newsletter mobile stacking, product/shop panel spacing, and shop-card mobile density.

## Icon Suite

Use these assets for brand proof rows, service cards, local/event context, and balloon-specific page treatments:

- `balloon-pair.svg`
- `balloon-cluster.svg`
- `balloon-arch.svg`
- `organic-garland.svg`
- `balloon-column.svg`
- `balloon-bouquet.svg`
- `utah-rooted.svg`
- `civic-parade.svg`
- `corporate-entrance.svg`
- `school-spirit.svg`
- `premium-private-event.svg`
- `event-stage.svg`
- `delivery-install.svg`
- `design-driven.svg`
- `professional.svg`
- `trusted-partner.svg`

The first four-icon pass was not enough. Balloon pages should use balloon-form icons first, because this is a balloon company, not a generic event consultant.

## Next Work

- Review the generated post-fix screenshots with GL/Jeff for taste, photos, and proof hierarchy; layout/container regressions are currently green.
- Replace or edit photos toward the Image #3 quality bar: crisp, premium, high-contrast, real scale, civic/Utah/corporate/school/private-event authority.
- Verify exact review/trust claims before launch copy is treated as final.
- Keep catalog color names such as product `Blush` intact. The retired `blush` rule applies to UI styling and design references, not supplier/product data.
- Do not use deleted `_resources/design-guide/` screenshots, TSX files, or the old shop/spec comparison docs as current taste calibration.
- Do not remove or simplify the restored mega-menu unless GL explicitly changes the navigation decision again.

## Verification Receipts

- `python scripts/dev/clear_website_cache.py` passed.
- `python scripts/verify/nav_ia.py` passed.
- `python scripts/verify/smoke_shop.py` passed with the current mega-menu contract.
- `npm run test:layout-fit` passed 80/80 with `/checkout` and `/thank-you` included.
- Post-fix screenshot/interaction report passed with no failures: `output/playwright/full-site-fix-20260505-post/post-fix-report.json`.
- All 16 SVGs parsed as valid XML.
- `python -B -m py_compile` passed for the LT app Python files.
- LT CSS token scan found no missing `--lt-*` variables.
- Active app source search found no old font/pastel/UI-blush references listed above.

## Files To Read Next

- `_resources/STYLE-GUIDE.md`
- `workstreams/brand-audience-style-reset.md`
- `workstreams/website-launch.md`
- `locally-twisted-decisions.md`
- `lessons-learned.md`
