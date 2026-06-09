---
id: erpnext-category-media-approval
name: ERPNext Category Media Approval
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe Item Group category image selection and assignment
currently_true: unknown
verification_level: 2
last_verified: 2026-05-06
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
  - frappe-public-container-contract
used_by: []
tags:
  - Locally Twisted
  - ERPNext
  - Frappe
  - category media
  - approval gate
---

# ERPNext Category Media Approval

Use this recipe when selecting representative images for customer-facing Item
Groups under `Shop Items`.

This is separate from CSS route hero art. The 2026-05-22 generated hero pass
updated `/shop-items/<group>` compact hero assets only; it did not approve or
mutate ERPNext Item Group `image` fields.

## Contract

Category browse images are not product truth. They are visual wayfinding, so do
not assign them by agent judgment alone.

The safe pattern is:

1. Generate a no-mutation candidate packet from existing approved source pools.
2. Review quick picks with GL/Jeff.
3. Mark only explicit approvals in the selection template.
4. Dry-run the Frappe-backed update path.
5. Apply only approved rows.
6. Recheck the live DB before claiming Item Group images changed.

## Source Pools

Current candidate inputs are:

- `_resources/catalog-source/slug_to_group.json`
- `_resources/catalog-source/catalog.json`
- `_resources/catalog-source/images/`
- `apps/locally_twisted/locally_twisted/www/portfolio.py`
- `apps/locally_twisted/locally_twisted/public/images/portfolio/optimized/`

Product-source images are safer for exact shop category representation.
Portfolio-proof images can be stronger visually, but use them only when the
category surface should show installed proof rather than a literal product photo.

## Commands

```powershell
python scripts/verify/category_media_candidates.py
python -m json.tool output/category-media-candidates.json
python scripts/setup/sync_category_media.py --write-template
python scripts/setup/sync_category_media.py --selection output/category-media-selection.template.json
```

After GL/Jeff approval, copy or edit the template into an approved selection
file and set `approved: true` only on approved rows:

```powershell
python scripts/setup/sync_category_media.py --selection output/category-media-selection.approved.json --apply
```

## Guardrails

- Never revive `/shop-by-category` as a shortcut for missing Item Group media.
- Never bulk-assign category images from generic gallery photos without approval.
- Keep generated reports and selection files under ignored `output/` unless GL
  explicitly wants a reviewed packet committed.
- `--apply` is not approval. The selection JSON is the approval record.
- Recheck the live DB after apply because Frappe file attachment and Item Group
  image state are separate records.

## LT Receipt

On 2026-05-06, the live DB still had empty `image` fields for the then-current
direct customer-facing Item Groups under `Shop Items`.
`scripts/verify/category_media_candidates.py` generated quick picks without
changing ERPNext data. `scripts/setup/sync_category_media.py` wrote a
selection template, dry-ran candidate updates, and an unapproved apply safety
check made 0 live updates.

On 2026-05-24, the approved shop taxonomy superseded the 11 direct-category
model with 8 visible primary groups under `Shop Items` and hidden secondary
occasion groups under `Shop Occasions`. Category media approval now applies to
the 8 visible primary groups unless GL explicitly opens a secondary image
treatment.

On 2026-05-22, route-level category hero art was repaired through generated
WebP crops and CSS mapping, then refreshed for the 8-category taxonomy on
2026-05-24. That work is tracked in
`workstreams/ecommerce-audit/shop-category-hero-imagery-2026-05-22.md` and
`capabilities/recipes/lt-balloon-color-generated-hero-contract.md`; it leaves
this ERPNext Item Group approval lane parked until GL/Jeff approve DB images.
