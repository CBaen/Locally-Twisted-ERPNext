D:2026-05-12 | Check:local ProductPatternContract + scaffold verifier | Confidence:[LOCAL-PROOF]
# Complex Checkout Scaffold Handoff

Use this handoff for GPT-5.5 Codex/OpenClaw peers continuing ERPNext ecommerce
infrastructure without updating the live site. This slice is source/local only.
It does not change Frappe Cloud, Cloudflare, Stripe, DNS, or the public
`locallytwisted.com` behavior.

## What Changed

- Added pure source classifier:
  `apps/locally_twisted/locally_twisted/catalog_contract/complex_checkout_scaffold.py`
- Added local report generator:
  `scripts/verify/complex_checkout_scaffold.py`
- Added pure fake-data regression contract:
  `scripts/verify/complex_checkout_scaffold_contract.py`
- Updated `scripts/README.md` with the new verifier entries.

The scaffold consumes the existing local `ProductPatternContract` report and
maps every product into an implementation lane before any future lane flip:

- direct-checkout regression guard
- simple-axis lane-flip candidate
- multi-color recipe UI required
- add-on or conditional-pricing blocked
- needs-review or missing

## Verification Receipt

Commands run locally on Wardenclyffe:

```powershell
python -m py_compile apps\locally_twisted\locally_twisted\catalog_contract\complex_checkout_scaffold.py scripts\verify\complex_checkout_scaffold.py scripts\verify\complex_checkout_scaffold_contract.py
python scripts\verify\complex_checkout_scaffold_contract.py
python scripts\verify\complex_checkout_scaffold.py
```

Latest scaffold result:

- Products checked: 53
- Scaffold ok: true
- Direct checkout regression guards: 18
- Simple-axis lane-flip candidates: 4
- Multi-color recipe UI required: 6
- Add-on or conditional-pricing blocked: 20
- Needs-review or missing: 5
- Explicit checkout architecture gaps: 0

Generated artifacts are ignored runtime evidence and can be regenerated:

- `output/complex-checkout-scaffold.json`
- `output/complex-checkout-scaffold.md`
- `output/product-pattern-contract.json`
- `output/product-pattern-contract.md`

## Current Stage Map

Simple-axis lane-flip candidates:

- `large-head-missionary`
- `mothers-day-front-yard-7-column`
- `easter-arch`
- `pride-arch`

Multi-color recipe UI required before checkout:

- `baby-shower-combination-photo-opt`
- `number-balloon-columns`
- `7-epic-column`
- `sleepy-baby-column`
- `baby-table-decor`
- `classic-organic-for-easel`

Add-on or conditional-pricing blocked before checkout:

- `classic-organic-balloon-garland`
- `basketball-arch`
- `easter-balloon-arch-bunny-ear`
- `halloween-arch`
- `premium-organic-garland`
- `premium-organic-arch`
- `pemium-organic-column`
- `pride-progress-rainbow-balloon-arch`
- `classic-arch`
- `classic-column`
- `classic-organic-columns`
- `baby-shower-garland`
- `balloon-drop`
- `classic-organic-arch`
- `organic-grab-n-go`
- `star-column`
- `logo-3-layered-bouquet`
- `6-color-rainbow-arch`
- `large-garland`
- `large-organic-column`

Needs review or missing before checkout planning:

- `birthday-deliveries`
- `marble-table-decor`
- `butterfly-get-well-bouquet-latex-free`
- `bandage-get-well-bouquet-latex-free`
- `shooting-star-get-well-bouquet-latex-free`

## Important Correction To Older Handoff Lists

Older storefront notes listed some products as "likely to pass" from rendered
front-end heuristics. The new scaffold is source-contract backed and supersedes
those heuristic lists for checkout planning. Examples:

- `6-color-rainbow-arch` is now blocked by conditional pricing work.
- `baby-table-decor` is a multi-color UI case, not a simple lane flip.
- `baby-shower-garland` and `balloon-drop` need add-on/conditional/freeform
  mapping before they are first multi-color proof candidates.

Use `output/complex-checkout-scaffold.json` or rerun the scaffold verifier
when product grouping matters. Do not use stale heuristic lists to flip lanes.

## Next Safe Source-Only Slice

1. Keep the 18 existing direct-checkout products green as regression coverage.
2. Rehearse one simple-axis candidate locally without touching live.
3. Build the reusable multi-slot color recipe UI against one of the six
   multi-color-only products, not Classic Arch.
4. Build add-on and conditional-pricing mapping only after the approval packet
   and price provenance are explicit.
5. Keep Classic Arch last. Its scaffold carries design-dependent color limits:
   Swirl up to 4 colors and Layered up to 8 colors.

## Non-Goals

- No Frappe Cloud app update.
- No DNS or Cloudflare change.
- No Stripe/live payment change.
- No live Website Item lane flip.
- No final catalog approval.
