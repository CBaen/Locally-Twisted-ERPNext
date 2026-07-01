# Phase 10 - Dependency And Rollback Capture For Birthday Deliveries

Date: 2026-06-30

Status: source-only/offline dependency and rollback target capture exists from
the saved Birthday Deliveries artifact. It is accepted only as no-write planning
evidence. Live dependency proof, historical reference proof, File/slideshow
reference proof, add-on/runtime proof, release approval, and owner-scope
approval are still missing. No deploy, cache clear, ERPNext/live mutation,
provider or payment action, DNS change, customer message, secret read, variant
collapse, record disablement, record deletion, route change, or product-scope
decision occurred.

## Purpose

Phase 9 mapped Birthday Deliveries from the saved artifact as a blocked
candidate model: `2,430` current variants and `2,430` Item Prices, with
`Delivery Size` as the only candidate SKU-defining axis, `Delivery themes` as a
configuration payload candidate, and `Add Foil Number` plus `Add Bouquet` as
paid add-on candidates.

Phase 10 captures the saved-artifact dependency and rollback targets before any
replacement model, publish/apply design, variant collapse, add-on runtime
design, or record mutation is allowed. Birthday Deliveries remains blocked until
the remaining live/historical dependency proof and release packet exist and pass
review.

## Route Record

```markdown
Mode: solo structured triad plus witnessed-work receipt
Decision needed: what must be captured before Birthday Deliveries can move from blocked planning evidence to a reviewed no-write replacement model
Scope owner: Locally Twisted ecommerce operator hardening lane
System/project/runtime classification: single project source documentation; client ecommerce surface risk; no runtime mutation
Allowed actions: repo reads, capability reads, source-only documentation in this file
Forbidden actions: deploy, cache clear, ERPNext/live mutation, provider/payment/DNS/customer action, secret read, variant collapse, product-scope decision, edits outside this file
Evidence bar: current Phase 9 source artifact, ecommerce hardening workstream files, loaded failure recipes, and future row-level read-only capture before mutation
Stop condition: stop before any write to records, cache, providers, customer paths, or existing docs/code
```

## Triad / Witness Support

Review type: solo structured triad with witnessed-work framing. The current
runtime did not expose a separate subagent tool, so this is not claimed as a
real multi-agent triad for the original draft. Follow-up implementation used
write-capable triad/witness lanes:

- Technical builder `019f1896-f9d8-7d41-a450-1b1c9ac734fd` implemented the
  offline dependency/rollback report and verifier.
- Documentation builder `019f1897-1775-7f70-a3c7-7c52e78ce64d` drafted this
  Phase 10 receipt/plan.
- Critical verifier `019f1897-2d07-7be0-9e77-ea346934901a` wrote the Phase 10
  overclaim and blocker review.

Intent lens:

- Keep Phase 10 source-only.
- Do not imply Birthday Deliveries is repaired, ready to collapse, or approved
  for mutation.
- Make the next safe work concrete enough that a later agent cannot skip
  dependency proof.

Technical lens:

- Capture dependency targets before designing replacement rows.
- Treat Product Setup, Website Item, Item, Item Price, media, route, cart, and
  historical references as separate authorities.
- Do not accept Product Setup classification or a public route check as rollback
  proof by itself.

Recovery lens:

- Require row-level rollback targets for every record family that could be
  changed, disabled, renamed, deleted, repointed, hidden, or superseded.
- Preserve historical identity and public links until a reviewed migration plan
  says otherwise.
- Keep old/current records restorable without relying on memory, stale handoffs,
  or a cache state.

## Target Dependency Categories

The Phase 10 capture packet must cover at least these categories:

- Variants: all current Birthday Deliveries variant Items, enabled/disabled
  state, item codes, variant-of/template link, attribute values, item group,
  stock/UOM/tax-relevant fields where applicable, and any field used by product
  page, cart, checkout, documents, or verifiers.
- Item Prices: every current Birthday Deliveries sellable `Item Price` row,
  including item code, price list, currency, UOM, rate, validity dates, disabled
  state, modified timestamp, and modified_by.
- Website Item: the Birthday Deliveries Website Item record, route/slug,
  published state, item link, operating-brand fields, public copy fields,
  commerce lane, image fields, slideshow link, modified timestamp, and
  modified_by.
- Template Item: the Birthday Deliveries template/root Item, variant attributes,
  item group, image, naming/identity fields, enabled state, and any runtime
  resolver fields.
- Product Setup rows: the LT Product Blueprint row plus child rows for option
  groups, options, exact prices, media rules, gallery rows, add-ons, runtime
  status, target Item, target Website Item, operating brand, and authority
  state.
- Option rows: every current axis/value row, including `Delivery Size`,
  `Delivery themes`, `Add Foil Number`, and `Add Bouquet`, with sequence,
  labels, current classification, price signal, future payload target, and
  blocker status.
- Media/gallery: Product Setup primary image, Website Item image, Item image,
  File rows/attachments, Website Slideshow rows, gallery media, selected-option
  media behavior, metadata image, shop/card image, cart image, and any homepage
  or merchandising references.
- Public route/cart identity: product route, product-page runtime JSON, item
  identity passed to selectors, cart API item identity, checkout lane identity,
  Guest/customer dependency where relevant, and customer-facing labels that
  must not silently change.
- Historical references: Sales Orders, Sales Invoices, Quotations, Payment
  Entries, Stripe/payment payload references where in scope, Email Queue or
  Communication rows, customer documents, public links, verifier fixtures,
  saved artifacts, reports, analytics/ad references, and any workstream or
  decision file that names current Birthday Deliveries identifiers.

## Required Rollback Packet Shape

Before any Birthday Deliveries mutation, the packet must include:

- Environment and proof mode: local saved artifact, local DB, staging, or live.
- Exact source artifact path and capture timestamp.
- Read-only command or API path used for capture.
- Row-level before snapshot for every target category above.
- Proposed change class for each row: keep, supersede, disable, rename, delete,
  repoint, regenerate, or unknown.
- Restore action for every changed row family, including order of operations.
- Cache plan only if a later approved mutation path needs one; no cache clear is
  allowed during capture.
- Public route/cart/checkout/document proof required after restore or apply.
- Owner/business approval gate for any product-scope or customer-facing identity
  change.
- Explicit non-goals: no current variants are deleted, disabled, renamed,
  repurposed, collapsed, or hidden by the packet itself.

## Acceptance Criteria

Phase 10 is not accepted until all of the following are true:

- The capture packet names the exact Birthday Deliveries product identity and
  source artifact used.
- Every target dependency category above is either captured or marked blocked
  with a specific reason.
- Every proposed future mutation target has a corresponding rollback target.
- Current 2,430 variants and 2,430 Item Prices are preserved as rollback-aware
  current state, not treated as disposable implementation debris.
- `Delivery Size`, `Delivery themes`, `Add Foil Number`, and `Add Bouquet` keep
  their Phase 9 classifications as planning evidence only until add-on/runtime
  pricing, cart, order, document, and customer-label proof exists.
- Media rollback distinguishes gallery/slideshow proof from primary-image,
  File-attachment, metadata, cart, receipt, and merchandising proof.
- Public route/cart identity is captured before any SKU or payload model is
  designed.
- Historical references are searched before any row identity changes are
  proposed.
- The packet exits or reports blocked if it cannot prove dependencies without
  mutation.
- Birthday Deliveries remains blocked for mutation until this proof exists and
  is reviewed.

## Captured Saved-Artifact Output

Tooling:

- `scripts/dev/lt_product_setup_dependency_rollback_report.py`
- `scripts/verify/product_setup_dependency_rollback_contract.py`

Saved Birthday Deliveries run:

```bash
python scripts/dev/lt_product_setup_dependency_rollback_report.py --input /tmp/lt-catalog-authority-full-20260630/044-birthday-deliveries.json --output /tmp/lt-birthday-deliveries-dependency-rollback-report.json --pretty --fail-on-blocker
```

Result: expected exit `1`.

Captured rows from saved artifacts:

- Variant Items: `2,430` row-level rollback rows.
- Item Prices: `2,430` row-level rollback rows.
- Product Setup option rows: `4` row-level rollback rows.
- Media/gallery/pointer rows: `9` row-level rollback rows.
- Blocked products: `1`.
- Blocker count: `20`.

The generated `/tmp` report is local and ephemeral. Regenerate it from the
saved artifact or a fresh read-only capture before relying on it in another
session.

## Still Blocked

Birthday Deliveries is not fixed, not collapsed, not approved for a 3-SKU model,
and not ready for publish/apply work. The next safe step is no-write replacement
model design using Phase 9 classification and this Phase 10 blocked rollback
packet. Mutation remains blocked.

## Verification

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/failures/ecommerce-variant-price-source-drift.md`
- `capabilities/failures/product-gallery-projection-regression.md`
- `capabilities/failures/product-primary-media-attachment-drift.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-9-variant-axis-classification-birthday-deliveries-2026-06-30.md`

Checks for this documentation/tooling slice:

```bash
python /home/guidingl/codex-framework/tools/capability_context_gate.py \
  --cwd "$PWD" \
  --task "Draft Phase 10 source-only dependency and rollback target capture receipt/plan for Birthday Deliveries after Phase 9, with no mutation and blocked status until proof exists" \
  --loaded "capabilities/INDEX.md" \
  --loaded "capabilities/failures/product-setup-projection-authority-drift.md" \
  --loaded "capabilities/failures/ecommerce-variant-price-source-drift.md" \
  --loaded "capabilities/failures/product-gallery-projection-regression.md" \
  --loaded "capabilities/failures/product-primary-media-attachment-drift.md" \
  --loaded "workstreams/ecommerce-operator-hardening-2026-06-30/phase-9-variant-axis-classification-birthday-deliveries-2026-06-30.md"
```

No runtime, browser, ERPNext, provider, payment, DNS, cache, deploy, or customer
checks were run because this slice is source-only/offline.

Additional verification:

```bash
python -m py_compile scripts/dev/lt_product_setup_dependency_rollback_report.py scripts/verify/product_setup_dependency_rollback_contract.py
python scripts/verify/product_setup_dependency_rollback_contract.py
python scripts/dev/lt_product_setup_dependency_rollback_report.py --input /tmp/lt-catalog-authority-full-20260630/044-birthday-deliveries.json --output /tmp/lt-birthday-deliveries-dependency-rollback-report.json --pretty --fail-on-blocker
```

Results:

- `py_compile`: pass.
- `product_setup_dependency_rollback_contract.py`: pass, 3 tests.
- Saved Birthday Deliveries report: expected exit `1`, 1 blocked product, 20
  blockers, row-level saved-artifact rollback rows included for the captured
  target categories.
