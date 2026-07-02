---
id: lt-brand-style-guide-consolidation
name: LT Brand Style Guide Consolidation
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe public-site brand and style-guide authority work
currently_true: true
verification_level: 2
last_verified: 2026-05-05
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
  - frappe-sitewide-visual-overhaul
  - responsive-container-audit
used_by: []
tags:
  - Locally Twisted
  - style guide
  - brand authority
  - stale reference cleanup
  - Frappe
  - Webshop
---

# LT Brand Style Guide Consolidation

Use this recipe when a Locally Twisted visual direction changes enough that old references, old style guides, or stale design artifacts would mislead the next agent.

## When To Use

- GL rejects the current visual system, typography, photo treatment, icons, or spacing.
- A new visual direction needs to become the repo authority before a multi-agent implementation pass.
- Old design artifacts are still in active reading paths and conflict with the current direction.
- The work is source-of-truth consolidation, not only page styling.

## Pattern

1. Identify the current approved visual authority and write it into `_resources/STYLE-GUIDE.md`.
2. Delete conflicting tracked visual references if they are not current source material. Git is the archive.
3. Keep true business/catalog evidence, even if it contains words that are banned as UI styling. Example: supplier color name `Blush` can remain in catalog evidence.
4. Update agent entry points and feature handoffs so future agents know what to read and what not to read.
5. Update active app code if old design tokens or old font names are still in source.
6. Add or update the feature-specific workstream handoff.
7. Update queue, decisions, lessons, and index docs in the same closeout.
8. Run searches that separate active UI/source files from historical catalog_data/catalog evidence.
9. Run syntax, token, cache, nav, layout, interactive layout, and shop smoke checks before claiming the consolidation is ready for implementation agents.

## Verification Checklist

- Deleted reference paths are absent on disk.
- Active app source search has no retired font/token/UI-style references.
- `_resources` search only keeps retired terms inside explicit "deleted/do not use" notes or business/catalog evidence.
- SVG icon assets parse.
- Python syntax compiles if controllers changed.
- CSS token scan has no missing project tokens.
- `python scripts/dev/clear_website_cache.py`
- `python scripts/verify/nav_ia.py`
- `npm run test:layout-fit`
- `npm run test:interactive-layout`
- `python scripts/verify/smoke_shop.py`
- `npm run test:public-verify` for broad public-site visual changes.

## LT Receipt

The 2026-05-05 consolidation deleted `_resources/design-guide/`, old shop/spec comparison references, and the old generic icon comparison. `_resources/STYLE-GUIDE.md` version 4.2 became the sole current visual authority. The active app moved to Cormorant Garamond + Lato and non-pastel LT token names. A 16-file custom brass-line icon suite was added under `apps/locally_twisted/locally_twisted/public/icons/brand/`.

The same day, the responsive/container requirement was added as a standing style-guide quality gate. Future page or component styling work must check breakpoint-edge containers and stateful UI, not only one mobile screenshot.
