# Phase 16 Critical Review - Source-Only Pre-Mutation Release Packet Design

Date: 2026-07-01

Status: critical review artifact only. No script, app code, queue, handoff,
capability, coordination, runtime, provider, payment, DNS, cache, deploy,
customer-message, product-scope, variant, or live record change occurred.

## Findings

A release packet design is safe as the next source-only phase after Phase 15
only if it is a packet schema, verifier contract, and fail-loud acceptance gate.
It must not create an apply path, publish path, cache-clear path, deploy path, or
operator approval shortcut.

Phase 15 produced a catalog-wide blocker map over saved authority packet data,
not a publish queue. The source state still says 47 products blocked, zero ready
products, and all local/staging/live apply, mutation, cache clear, deploy, and
public-success approvals false. A Phase 16 packet can organize what a later
mutation would need, but it cannot change that readiness state.

The packet must keep proof modes separate. Source-only packet generation can
prove that required fields are present and that missing proof blocks release. It
cannot prove the target site changed, the target site is current, a cache action
worked, a public route/API/cart/checkout path passed, a payment/document path is
safe, or a rollback actually restores customer-facing behavior.

The main overclaim risk is naming the artifact a release packet and then letting
operators or agents treat packet existence as release approval. The packet must
carry explicit approval booleans and blocker codes that remain false/blocked
until target-environment proof is attached. `Approved For Live` must remain not
live; live means the target customer-facing site was updated and re-proved.

The design must also avoid collapsing product-scope decisions into engineering
fields. A target list, row-level diff, or replacement model is not approval to
delete, disable, rename, collapse, revive, retire, or broaden products. Any such
scope still needs owner/business approval and historical-reference handling.

## Required Acceptance Criteria

Before any future live/product mutation can proceed, a pre-mutation release
packet must include these fields and fail if any required field is missing,
stale, ambiguous, or unsupported for the requested change type:

- Packet identity: `schema_version`, generated timestamp, packet purpose,
  proof mode, requested action type, and explicit source-only/staging/live
  boundary.
- Environment identity: exact target environment, target site URL/host, ecommerce
  pause posture, payment/document proof mode, and whether checkout/payment is in
  scope.
- Source identity: branch name, commit/hash, dirty-overlap audit for touched
  files, app-mirror branch/commit when Frappe Cloud app release is involved, and
  old-live-to-target diff requirement.
- Actor and approvals: requester, technical preparer, reviewer, owner/business
  approval when required, approval timestamp, approval scope, and explicit stop
  condition.
- Target scope: products, routes, Website Items, Product Setup records, Item
  templates, variants, Item Prices, option/add-on rows, media/File/slideshow
  rows, and merchandising references affected by the planned change.
- Brand-lane proof: allowed brand lane, route namespace, copy surface, document
  identity, payment/customer-message identity, file/media ownership, portal and
  automation behavior, and failure behavior when lane proof is missing.
- Row-level planned diff: every old value, new value, doctype/table, record id,
  field name, resolver/source authority, modified timestamp when known, and
  whether the row is source, projection, public runtime, cart, document, payment,
  or rollback-only evidence.
- Product authority proof: Product Setup authority, Website Item authority, Item
  authority, price authority, media authority, option/add-on classification,
  visibility/quote/checkout lane, historical references, and unresolved blockers.
- Price proof requirements: Item Price rows by `item_code`, variant/option key,
  Price List, currency, UOM where relevant, validity/scope, public display,
  variant selector, cart, checkout, Sales Order, payment payload, invoice, and
  receipt proof mode where in scope.
- Media proof requirements: Product Setup primary image, Website Item image,
  Item image, File attachment and visibility, slideshow/gallery, metadata/social
  image, shop card, product page gallery, selected-option image, cart image,
  payment image, receipt image, and merchandising references where applicable.
- Option/add-on proof: classification, visible UI behavior, cart payload/order
  line behavior, checkout summary, Sales Order, invoice, payment, and receipt
  labels where in scope.
- Backup and rollback: pre-change row snapshot plan, exact fields touched,
  rollback command or manual maintenance procedure, cache rollback plan, public
  proof after rollback, and owner-visible status after rollback.
- Release containment: no-downtime/customer-impact section, fallback or pause
  posture, expected customer impact, release containment, and proof that product
  content changes do not accidentally expose checkout/payment.
- Verifier plan: exact commands, expected exit codes, required artifacts,
  blocker behavior, target-site checks required after mutation, and freshness
  rules for saved artifacts.

Verifier behavior that should block commit:

- Exit nonzero if a source-only packet sets local/staging/live apply, mutation,
  cache clear, deploy, public-success, provider, payment, document-send, or
  customer-message approval true.
- Exit nonzero if packet existence, owner approval, source commit, app-mirror
  commit, dashboard row, or saved artifact is treated as live proof.
- Exit nonzero if target environment, target products/routes, brand lane,
  row-level diff, backup/snapshot, rollback method, cache plan, verifier list,
  proof mode, no-downtime/customer-impact section, stop condition, or approval
  scope is missing.
- Exit nonzero if any target product still has unresolved authority, public
  route/API, price, media, option/add-on, cart/checkout, historical-reference,
  rollback, product-scope, or variant-shape blockers not explicitly marked as
  blocking mutation.
- Exit nonzero if stale saved artifacts are used without a freshness label and a
  required current-proof blocker.
- Exit nonzero if a packet for a checkout-looking product omits listing/cart
  eligibility proof or payment/document proof mode.
- Exit nonzero if a packet for Frappe Cloud release scope omits old live app
  hash, target app-mirror branch/commit, old-live-to-target diff, deploy pipeline
  status, dirty-overlap audit, site update result, or migrate result where
  applicable.
- Exit nonzero if rollback cannot be defined for every touched record family.
- Exit nonzero if the packet proposes delete, disable, rename, collapse, revive,
  retire, replace, or product-family rollout without owner/business approval,
  dependency proof, historical-reference handling, and rollback proof.
- Exit nonzero on any forbidden live/apply/cache/deploy/provider/customer-send
  call path in the source-only implementation.

Claims that must remain false until fresh target-site proof exists:

- The product is live, live-applied, publicly changed, customer-visible, or safe
  to sell.
- Target-site route/API/cart/checkout proof passed.
- Cache clear, deploy, site update, migration, provider, payment, document, or
  customer-message behavior is approved or complete.
- Source-declared brand is live brand-lane proof.
- Same-brand source uniqueness is live/global uniqueness proof.
- Dashboard counts, saved `/tmp` artifacts, or packet completeness prove current
  catalog truth.
- Owner/business approval alone proves technical release readiness.
- Technical verifier pass alone proves business/product-scope approval.
- Rollback is safe before rollback has a defined target and post-rollback public
  proof plan.

Commit acceptance for Phase 16 should require:

```bash
python /home/guidingl/codex-framework/tools/capability_context_gate.py --cwd "$PWD" --task "Phase 16 source-only critical review of LT pre-mutation release packet design after catalog readiness dashboarding" --loaded "capabilities/INDEX.md" --loaded "capabilities/failures/product-setup-projection-authority-drift.md" --loaded "workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md"
git diff --check
```

If the next phase adds a packet script or verifier, commit should also be blocked
unless `py_compile`, the new contract verifier, `product_blueprint_contract.py`,
`product_setup_publish_readiness_contract.py`, and
`product_setup_catalog_readiness_contract.py` pass, with the known blocked
catalog still exiting nonzero under a fail-on-blocker mode.

## Residual Risk

Even a perfect source-only packet verifier will not prove the live site. It will
prove only that the packet is complete enough to block or guide a later release
decision.

Saved artifacts can be stale. A packet built from Phase 4/15 saved data may
miss current target-site drift, provider state, cache behavior, product edits,
cart behavior, and owner Desk state that changed after the artifact was captured.

The largest risk remains false confidence from organized paperwork. A complete
packet can still describe an unsafe change if the underlying business approval,
product scope, brand-lane proof, row resolver, rollback target, or target-site
verification is wrong.

Release-provider risk remains outside this source-only review. Actual Frappe
Cloud, app mirror, Cloudflare, Stripe, DNS, payment, document, or customer-send
execution must load the release/provider capabilities and prove the target
environment at that time.

Owner usability remains unproven. A packet schema can be technically complete
while still too complex for Jeff or staff to understand without a Desk dashboard,
plain blocker wording, and acceptance testing with the intended operator role.

## Recommendation

Proceed with Phase 16 only as a source-only release-packet design and verifier
acceptance standard. The correct artifact should make future mutation harder to
overclaim by requiring environment, scope, diff, rollback, proof-mode,
brand-lane, approval, and verifier fields before any write path can even be
reviewed.

Do not implement live apply, publish, cache clear, deploy, provider, payment,
document, customer-message, or catalog mutation behavior in the release-packet
design phase. If a proposed packet design implies live writes or release
approval, stop and split it back into source-only packet generation plus a later
explicit staging/live release gate.

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`
