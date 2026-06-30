# Phase 0 Public Evidence - Large head Missionary

Date: 2026-06-30

Status: Worker C read-only helper and evidence note. This is not a release approval, not database proof, not cache clearing, and not a product-data mutation.

## Scope

Product route:

- `https://locallytwisted.com/shop-items/bouquets/large-head-missionary`

Assigned helper:

- `scripts/dev/lt_readonly_product_audit.py`
- `scripts/dev/lt_readonly_product_db_snapshot.py` for a later approved local/authenticated row snapshot

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/public-runtime-flow-map.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/broken-connections-register.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/README.md`

## Safe Run

Public route only:

```bash
python scripts/dev/lt_readonly_product_audit.py \
  --output /tmp/lt-large-head-missionary-public.json
```

Optional public API GET reads, only when a local or target site base URL is explicitly provided through non-secret environment variables:

```bash
LT_READONLY_PRODUCT_AUDIT_ENABLE_API_GETS=1 \
LT_READONLY_PRODUCT_AUDIT_API_BASE_URL=http://localhost:8081 \
python scripts/dev/lt_readonly_product_audit.py \
  --base-url http://localhost:8081 \
  --output /tmp/lt-large-head-missionary-local-public-api.json
```

Do not pass credentials. The helper has no token, password, cookie, or secret arguments.

## What The Helper Can Prove

- Public product route HTTP status, selected response headers, body size, and body hash.
- Whether the rendered public HTML contains `Large head Missionary`.
- Public HTML title, first H1, visible dollar strings, and LT product runtime script blocks when present.
- Embedded Product Setup schema as rendered into the public page, when present.
- Optional public GET responses from the Product Setup schema and variant media APIs when `LT_READONLY_PRODUCT_AUDIT_ENABLE_API_GETS=1` and `LT_READONLY_PRODUCT_AUDIT_API_BASE_URL` are set.

## What The Helper Cannot Prove

- Authenticated Desk row values or who changed them.
- Complete Website Item, Item, Item Price, Product Setup, File, or slideshow database truth.
- Variant selector price behavior, because that public endpoint is POST-only and this helper is GET-only.
- Cart, checkout, Sales Order, payment, invoice, or receipt behavior.
- Cache health beyond response headers visible on the GET response.
- Release readiness or live data correctness.

## Fail-Loud Boundaries

The helper blocks:

- `POST`, `PUT`, `PATCH`, and `DELETE`.
- Cache clearing.
- ERPNext writes.
- Any request to allow mutating API behavior.
- URL-like output paths and non-JSON output names.

The output JSON is written only to the caller-provided local file path from `--output`.

## Evidence Meaning

This helper is a Phase 0 evidence collector for the public-render side of B002 and B012. A passing run can show what the public route rendered at the time of the GET. It cannot close B012 by itself, because B012 still needs authenticated read-only row comparison for the exact product authorities named in the register.

## Observed Worker C Runs

Public route run:

```bash
python scripts/dev/lt_readonly_product_audit.py \
  --output /tmp/lt-large-head-missionary-public.json
```

Result:

- Status: pass.
- Public route HTTP status: `200`.
- `x-from-cache`: `False`.
- `content-type`: `text/html; charset=utf-8`.
- Public H1: `Large head Missionary`.
- Expected title text present: yes.
- Embedded Product Setup schema present: yes.
- Embedded Product Setup source: `lt_product_setup`.
- Embedded Product Setup `commerce.base_price`: `125.0`.
- Static HTML dollar strings extracted by the helper after normalized `$ 175.00` spacing support: `$15`, `$50`, `$175.00`.
- Failures: none.

Optional public API GET run:

```bash
LT_READONLY_PRODUCT_AUDIT_ENABLE_API_GETS=1 \
LT_READONLY_PRODUCT_AUDIT_API_BASE_URL=https://locallytwisted.com \
python scripts/dev/lt_readonly_product_audit.py \
  --output /tmp/lt-large-head-missionary-public-api.json
```

Result:

- Status: pass.
- Product Setup schema API GET: `200`, `application/json`, `commerce.base_price` = `125.0`.
- Variant media API GET: `200`, `application/json`.
- Failures: none.

The static HTML extraction did not prove the selected sellable variant price. That remains intentionally outside this helper because the public variant selector price path is POST-only.
