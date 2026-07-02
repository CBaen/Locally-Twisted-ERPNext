# Phase 3 product-family proof build brief — 2026-05-10

## Scope

Build a narrow, rollback-safe verifier proving the first direct-checkout product family without opening public ecommerce:

- Bouquet family: all approved character/sports/theme bouquet Website Items classified `simple_product` / `checkout` expose the confirmed foil-number add-on and preserve selected size + add-on meaning into backend order lines.
- Mother's Day Bouquet: simple single-SKU checkout path resolves without add-ons/customization and preserves line metadata into backend order lines.
- Easter Balloon Cups: do not claim launch approval from this verifier. Seasonal visibility/orderability remains a separate GL/business approval; if inspected, report it as deferred/pending approval.

## Guardrails

- No catalog_data mutation.
- No catalog purge/delete/reimport/publish/opening.
- No public ecommerce opening; test-mode pause bypass may only exist inside verifier execution and must roll back/restore.
- No live payment or customer messaging.
- No checkout/payment success claim without backend record evidence.
- Preserve unrelated git changes.

## Implementation ownership

Primary files expected:

- `apps/locally_twisted/locally_twisted/verify/checkout_product_family_contract.py`
- `scripts/verify/checkout_product_family_contract.py`
- Phase 3 result artifact after gates pass/block.

## Verification gates

Minimum verifier evidence:

1. All expected bouquet Website Items exist, are published, and stored as `simple_product` / `checkout`.
2. All expected bouquet templates expose `foil_number` add-on at `$12` from server-side add-on contracts.
3. A real variant from every expected bouquet family resolves through server-side cart/checkout helpers with versioned configuration.
4. A rollback-only Sales Order containing all bouquet base + foil add-on lines, plus Mother's Day simple line, is inserted/submitted and proves custom LT line fields are stored.
5. A rollback-only Sales Invoice made from that Sales Order preserves the same custom LT line fields.
6. Quote/review add-on boundaries remain intact through the existing product add-on dependency contract.

## Review lenses

- Architecture: verifier should prove the reusable runtime contract, not hard-code a UI-only path.
- Security/operations: no public unpause, live payment, PII/token/session exposure, customer email, or persistent generated records.
- Edge cases: no free/unpriced add-on, no dropped variant options, no family silently missing from expected list, no stale localStorage/direct cart bypass for quote/review products.
