---
id: external-design-reference-translation
name: External Design Reference Translation
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted visual work that starts from Claude, designer, prototype, or other external reference code
currently_true: unknown
verification_level: 2
last_verified: 2026-05-06
evidence_quality: direct
successful_uses: 1
failed_uses: 1
regressions: 0
depends_on:
  - frappe-public-container-contract
  - responsive-container-audit
used_by:
  - frappe-portfolio-proof-reel
tags:
  - Locally Twisted
  - design translation
  - Claude handoff
  - Frappe
  - visual QA
---

# External Design Reference Translation

Use this when GL brings in code, screenshots, mockups, or prototypes from Claude,
a designer, another agent, or a research folder and asks Codex to make it work in
the LT Frappe site.

## Rule

External design code is a visual contract and critique surface. It is not
automatically production ownership.

Codex owns the Frappe translation: route/controller/template shape, asset paths,
optimized images, tests, cache clearing, and proof that the running site matches
the approved visual behavior.

## Translation Steps

1. Name the source artifact path and keep it separate from production code.
2. Extract the visual contract before editing:
   - what behavior, spacing, motion, sizing, and image treatment must survive;
   - what should be ignored, such as wrong header, footer, copy, placeholders, or fake data;
   - what data/assets must be replaced with real LT source.
   Be explicit when GL approves only one part of a reference. "Use the collage
   and movement" does not mean "copy the entire page shell."
3. State any deliberate deviations before implementation. Do not silently add
   local "improvements" such as cards, filters, modals, captions, boxed grids, or
   Frappe containment if they fight the approved design.
4. Translate into platform-owned files:
   - `www/<route>.html` for Jinja structure;
   - `www/<route>.py` for data, metadata, and JSON payloads;
   - `public/css/` and `public/js/` for page assets;
   - optimized public images when real photos are large.
5. Preserve the Frappe/Webshop lifecycle. Header/footer changes still belong in
   shared Jinja partials, not in copied designer page shells.
6. Leave a review receipt for the designer and GL:
   - source artifact path;
   - production file paths;
   - intentional deviations;
   - verification commands;
   - screenshot paths if generated.
7. Keep the source artifact in `research/` while external critique is active.
   Delete or archive it only after GL explicitly says the production translation
   is accepted and the reference is no longer needed.

## Failure Mode This Prevents

The bad path is treating a design reference like a suggestion, then "helpfully"
merging it into older local UI patterns. In the portfolio case, that produced a
hybrid surface: some reference motion, but also old filters, modal behavior,
Frappe boxing assumptions, and stale claims that the reference folder had been
deleted. That made the production code harder for the designer to critique.

## Verification

For visual route work, verify the actual running site:

```powershell
python scripts/dev/clear_website_cache.py --restart
npm run test:layout-fit -- --grep <route-name>
npm run test:interactive-layout -- --grep <route-or-state-name>
```

Add or update a route-specific verifier when the design has unique motion,
photo, canvas, carousel, scroll, or interaction behavior.

Also capture desktop and mobile screenshots when the task is design-sensitive.
