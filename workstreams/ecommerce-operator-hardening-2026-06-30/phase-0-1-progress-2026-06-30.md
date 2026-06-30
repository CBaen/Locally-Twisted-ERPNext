# Phase 0/1 Progress - Read-Only Incident And Authority Packet

Date: 2026-06-30

Status: meaningful non-deploy progress completed. Later same-day local and live read-only proof superseded the "still unproved" section below. This is not repair approval and not a live mutation.

## Completed

- Created the Phase 0/1 build brief:
  - [phase-0-1-build-brief-2026-06-30.md](phase-0-1-build-brief-2026-06-30.md)
- Created the reusable product authority matrix template:
  - [authority-matrix-template.md](authority-matrix-template.md)
- Created the first partial product authority packet:
  - [authority-packet-large-head-missionary.md](authority-packet-large-head-missionary.md)
- Created the public GET-only audit helper:
  - `scripts/dev/lt_readonly_product_audit.py`
- Created the local-container read-only DB snapshot helper:
  - `scripts/dev/lt_readonly_product_db_snapshot.py`
- Created the public evidence note:
  - [phase-0-public-evidence-large-head-missionary.md](phase-0-public-evidence-large-head-missionary.md)
- Created the partial Phase 0 incident audit:
  - [phase-0-incident-audit-large-head-missionary-2026-06-30.md](phase-0-incident-audit-large-head-missionary-2026-06-30.md)

## Current Proof

Public GET-only evidence for `https://locallytwisted.com/shop-items/bouquets/large-head-missionary` proves:

- route returns HTTP `200`;
- server is `Frappe Cloud`;
- `x-page-name` is `shop-items/bouquets/large-head-missionary`;
- `x-from-cache` is `False`;
- public H1 is `Large head Missionary`;
- extracted price strings include `$175.00`;
- embedded Product Setup schema is present;
- embedded Product Setup source is `lt_product_setup`;
- embedded Product Setup status is `Local Preview Ready`;
- embedded Product Setup base price is `125.0`;
- runtime commerce lane is `checkout`;
- runtime checkout allowed is `true`;
- runtime has 3 SKU-defining groups and 30 variant combinations.

Conclusion: public split authority is proved. Product Setup/base-price data and customer-facing sellable price data can diverge on the same product route.

## Historical Gap - Later Closed Or Narrowed

At the time of this first progress note, authenticated read-only DB/Desk proof
was still needed. Later same-day work produced local snapshot proof and live
read-only API proof. Current state:

- exact owner-saved Product Setup row, modified time, modified_by, Website
  Item, template Item, 30 variants, and 30 Standard Selling Item Price rows are
  proved live in
  `live-readonly-api-audit-large-head-missionary-2026-06-30.md`;
- Product Setup active uniqueness, brand-lane row proof, detailed variant
  attribute rows, media/File/slideshow rows, historical references, cart proof,
  checkout proof, payment/document proof, and rollback target remain needed
  before mutation or repair.

## Verification Run

Commands run:

```bash
python -m py_compile scripts/dev/lt_readonly_product_audit.py
python scripts/dev/lt_readonly_product_audit.py --dry-run --output /tmp/lt-audit-dry-run.json
python scripts/dev/lt_readonly_product_audit.py --output /tmp/lt-large-head-missionary-public-main-v2.json
LT_READONLY_PRODUCT_AUDIT_ENABLE_API_GETS=1 \
LT_READONLY_PRODUCT_AUDIT_API_BASE_URL=https://locallytwisted.com \
python scripts/dev/lt_readonly_product_audit.py --output /tmp/lt-large-head-missionary-public-api-main-v2.json
python scripts/dev/lt_readonly_product_audit.py --http-method POST --output /tmp/lt-should-not-write.json
python scripts/dev/lt_readonly_product_audit.py --clear-cache --output /tmp/lt-should-not-write-cache.json
python -m py_compile scripts/dev/lt_readonly_product_db_snapshot.py
python scripts/dev/lt_readonly_product_db_snapshot.py --dry-run
python scripts/dev/lt_readonly_product_db_snapshot.py --output /tmp/lt-large-head-missionary-db-snapshot.json
python scripts/dev/lt_readonly_product_db_snapshot.py --clear-cache --output /tmp/lt-db-should-not-write.json
git diff --check -- scripts/dev/lt_readonly_product_audit.py scripts/dev/lt_readonly_product_db_snapshot.py workstreams/ecommerce-operator-hardening-2026-06-30
```

Results:

- public audit helper compile: pass;
- public audit dry-run: pass;
- public GET-only run: pass;
- optional public API GET run: pass;
- mutating method guard: blocked with no output file;
- cache-clear guard: blocked with no output file;
- DB snapshot helper compile: pass;
- DB snapshot dry-run: pass;
- DB snapshot actual run: safely blocked because local LT backend container is not running;
- DB snapshot cache-clear guard: blocked with no output file;
- diff whitespace check: pass.

## Not Done

- No deploy.
- No live write.
- No local ERPNext write.
- No cache clear.
- No payment/provider/DNS/Frappe Cloud change.
- No customer message.
- No product repair.
- No catalog migration.

## Next Safe Action - Superseded

This original next action is superseded. The local snapshot and live read-only
API proof have already been run. The current next safe action is no-write
projection preview and parity-verifier design.

Historical local helper command:

```bash
python scripts/dev/lt_readonly_product_db_snapshot.py \
  --output /tmp/lt-large-head-missionary-db-snapshot.json
```

If this historical local snapshot command is rerun, label it local proof only.
Current live root-cause proof is now
`live-readonly-api-audit-large-head-missionary-2026-06-30.md`; the remaining
blockers are projection design, parity verification, and rollback capture
before mutation.
