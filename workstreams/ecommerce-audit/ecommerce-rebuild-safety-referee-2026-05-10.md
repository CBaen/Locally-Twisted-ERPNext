D:2026-05-10 | Check:local artifacts/source 2026-05-10 | Confidence:[LOCAL-PROOF]

# Ecommerce Rebuild Safety Referee — 2026-05-10

## Scope and authority

This is a safety/decision gate artifact for the Locally Twisted ERPNext ecommerce rebuild research. It is not implementation approval, product import approval, purge approval, checkout approval, launch approval, or evidence that every product is verified.

Hard constraints applied:

- No code changes.
- No commits.
- No product delete, purge, import, or reimport.
- No private customer data inspection.
- No live payment, real customer email, or public/customer-facing action.

## Source map inspected

- `AGENTS.md` — project operating rules, current verified state, launch trust rules, catalog_data-as-source-witness framing.
- `ROLE.md` in the agent workspace — safety auditor operating contract.
- `capabilities/INDEX.md` — relevant LT capability index.
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md` — current ecommerce receiving contract, gates, red flags, verifier list.
- `capabilities/recipes/erpnext-checkout-commerce-rules.md` — checkout/tax/quote-required rules and payment/checkout verifier expectations.
- `capabilities/recipes/fail-loud-operating-law.md` — no fake success and verifier/evidence standard.
- `workstreams/ecommerce-audit/README.md` — current audit inventory and missing-lane warnings.
- `workstreams/ecommerce-audit/erpnext-receiving-parity-matrix-2026-05-10.md` — Lane B evidence and blockers.
- `workstreams/ecommerce-audit/cart-checkout-intent-preservation-audit-2026-05-10.md` — Lane C proof slice and blockers.
- `workstreams/ecommerce-audit/native-frappe-product-template-architecture-2026-05-10.md` — Lane D recommended native architecture and pending gates.
- `workstreams/ecommerce-audit/cart-checkout-verification-gates-2026-05-10.md` — cart/checkout evidence gates and banned claims.

Not inspected here: missing Lane A and Lane E artifacts because `README.md` says they do not exist in this evidence packet. This referee artifact therefore treats source-product findings and docs/source convergence as `[NO EVIDENCE]`, not as merely pending polish.

## Safety finding

ERPNext/Frappe can likely receive the intended ecommerce meaning through a native `locally_twisted` contract layer, but Lane F synthesis must not convert the current packet into launch confidence. The current evidence proves representative proof slices and architecture shape, not full source truth, not destructive import safety, not full catalog readiness, not public paid checkout readiness, and not product media/gallery approval.

The safest operating rule is:

> No product rebuild, purge/import, public ecommerce, or launch claim until every gate below has a dated artifact witness or is deliberately carried forward as `[NO EVIDENCE]` with a blocker.

## Missing evidence before any Lane F synthesis

Lane F must be blocked unless it either has these artifacts or explicitly marks them as `[NO EVIDENCE]` and lowers confidence.

1. **Lane A — catalog_data source commerce map**
   - Required artifact: `workstreams/ecommerce-audit/catalog_data-source-commerce-map-2026-05-10.md`.
   - Must enumerate current catalog_data/source product meaning: product classes, variant axes, valid combinations, add-ons, customizations, price sources/resolvers, media facts, quote behavior, unknowns, source version, and production/local mismatch.
   - Current status: missing / `[NO EVIDENCE]` per `README.md`.
   - Safety impact: no source-product claim should be cited as final.

2. **Lane E — catalog_data/docs/agent-action convergence**
   - Required artifact: `workstreams/ecommerce-audit/catalog_data-docs-agent-action-convergence-2026-05-10.md`.
   - Must reconcile catalog_data witness behavior, ERPNext/Frappe/Webshop docs/current behavior, project capabilities, and actual agent actions into one conflict map.
   - Current status: missing / `[NO EVIDENCE]` per `README.md`.
   - Safety impact: no docs/source convergence claim should be used as proof.

3. **Version reconciliation**
   - Lane B reports destination app versions `frappe 15.106.0`, `erpnext 15.105.0`, `payments 0.0.1`, `webshop 0.0.1`, `locally_twisted 0.0.1`, but the local image was `locally-twisted-erpnext:v15` instead of the dispatch anchor `frappe/erpnext:v15.105.0`.
   - Lane B also reports catalog_data local module `19.0.2.15.0` while older handoff warns production DB may be `19.0.2.14.0`.
   - Required artifact: dated version/source decision note naming which witness controls rebuild decisions.

4. **Clean aggregate readiness rerun**
   - Lane B says one aggregate readiness run had a MariaDB deadlock, even though the direct customer-delivery contract passed on rerun.
   - Required artifact: clean `product_page_architecture_readiness.py` report in the exact intended ecommerce mode, or a documented DB/concurrency fix with rerun.

5. **Full launch proof matrix**
   - Required artifact: one row per published Website Item with route, item group, source product, stored page type, commerce lane, variant axes, add-on families, price status, media status, checkout/quote decision, verifier/browser witness path, and blocker status.
   - Current Lane C blocker: all 53 published Website Items stored `lt_product_page_type=needs_review` and `lt_commerce_lane=needs_review` at inspection time.

6. **Media classification packet and browser proof**
   - Lane B reports 49 products / 95 unclassified extra images and no approved parent-gallery Website Slideshow records.
   - Required artifact: classified media packet and browser proof for representative product/media behavior before any media/gallery/photo-switching claim.

7. **Price and add-on business review packets**
   - Lane B reports source price/import blockers including `missing_resolver_prices: 49`, source price enrichment candidates, and review-only add-on families.
   - Required artifacts: price review packet and add-on approval packet with human decisions before broad checkout or import claims.

8. **Payment/email/finance launch evidence**
   - Current evidence intentionally avoids live payment and real email. Quote acceptance/delivery guards prove no side effects in test paths, not real production payment/email readiness.
   - Required artifact: explicit owner-approved payment/email launch scope and evidence, or public paid checkout remains blocked.

## Must block go-live

Go-live must be blocked if any of these are true:

- Lane A or Lane E is missing and not explicitly carried as `[NO EVIDENCE]` in a lower-confidence synthesis.
- Source version mismatch is unresolved or not owner-signed.
- Destination image/app-version mismatch is unresolved or not documented.
- Aggregate readiness does not cleanly pass in the intended ecommerce mode.
- Any published product lacks a launch-scope decision: checkout, quote-first, hidden/excluded, or blocked.
- Stored catalog classifications remain blanket `needs_review` without an explicit public-scope exclusion plan.
- Any checkout-capable product lacks approved price, variant/option behavior, add-on status, media status, and backend intent-preservation proof.
- Public route/browser proof is missing for representative desktop and mobile product/cart/checkout/quote-first paths.
- Payment/email/receipt claims are needed for launch but not separately verified and approved.
- Any customer-facing path can show false success after backend/order/quote/payment/email failure.

## Must block product purge/rebuild/import

Product purge/rebuild/import must be blocked if any of these are true:

- No Lane A source commerce map exists.
- `product_page_contract_source_audit.py` or equivalent says `blocked_for_destructive_import: true`.
- Source axes/add-ons/color/customization semantics are unknown, ambiguous, or still `needs_review`.
- The price review packet is missing or contains unresolved live-snapshot/business-review-required sale units.
- The media classification packet is missing for product media that would be imported or publicly claimed.
- There is no rollback anchor, dry-run report, and batch-by-batch proof plan.
- The importer would create fields/options that lack an ERPNext/custom destination, runtime owner, and verifier.
- The importer would turn quote-first/custom work into paid checkout by default.
- Human owner has not approved purge/rebuild scope and acceptable data loss/test-data assumptions.

## Must block checkout/public ecommerce

Checkout/public ecommerce must be blocked if any of these are true:

- The public ecommerce pause/reopen mode is not verified immediately before exposure.
- Any checkout product lacks a stored classification or explicit launch-scope inclusion.
- Any required option can be bypassed, flattened, silently dropped, or merged into another configured line.
- Same-SKU configured lines can merge without preserving distinct choices.
- Unsupported, review-only, or quote-first add-ons can enter checkout as free, hidden, or internal-only notes.
- Server-side pricing cannot prove base item + add-on totals; browser display alone is insufficient.
- Sales Order Item and Sales Invoice Item preservation is missing for the relevant path.
- Quote-first products can be forced into checkout by item code or route manipulation.
- Cart/checkout customer copy leaks internal errors or shows success after backend failure.
- Tax/delivery/service/deposit rules are not verified for the launch payment scope.
- Payment Request, Stripe session, receipt, invoice, or email claims are made without dedicated evidence.

## Must be reviewed by GL / Jeff / human owner

Human owner review is required for:

- Which catalog_data/source witness version controls the rebuild (`19.0.2.15.0` local vs possible `19.0.2.14.0` production DB).
- Whether any current ERPNext catalog/test data may be purged or rebuilt, and exact rollback expectation.
- Final product-family lane assignment: ready-to-order checkout vs custom quote-first vs hidden/excluded.
- Unknown or review-only axes, especially add-on families and customization/color semantics.
- Price review decisions, especially live-snapshot-derived prices and source resolver gaps.
- Media classification: parent gallery, variant image, category/reference, or hold.
- Public policy/legal/tax/payment copy and whether real paid checkout is in launch scope.
- Whether unresolved `[NO EVIDENCE]` lanes may be carried forward as blockers or require rerun before any synthesis.

## Required artifacts and judgment standard

Artifacts must be judged by dated, path-specific evidence, not prose confidence.

| Artifact | Required judgment |
|---|---|
| Lane A catalog_data source map | Complete enough to name source product meaning, unknowns, and version mismatch; otherwise `[NO EVIDENCE]` and blocks source claims. |
| Lane B parity matrix | Destination fields/services/verifiers mapped to each source concept; version mismatch called out; clean aggregate rerun required. |
| Lane C intent preservation audit | Representative browser + backend proof only; not full-catalog proof unless expanded with matrix coverage. |
| Lane D architecture artifact | Architecture recommendation only; cannot approve implementation/import by itself. |
| Lane E convergence artifact | Must reconcile official docs/source/project actions and conflicts; missing means no convergence claim. |
| Full launch proof matrix | One row per published product; unresolved rows block launch or must be excluded from public scope. |
| Price review packet | Human-approved price source/status per checkout sale unit; business-review-required rows block checkout. |
| Add-on approval packet | Explicit checkout-approved vs quote-only vs drop decisions; no second add-on family by ad hoc constants. |
| Media classification packet | Every extra/gallery/variant candidate classified or held; unclassified media cannot be publicly claimed. |
| Verifier output bundle | Dated command outputs/reports saved; nonzero, skipped, truncated, or deadlocked runs block the related claim. |
| Browser witness bundle | Desktop/mobile screenshots or JSON snapshots for product, cart, checkout, quote-first, and media behavior. |
| Rollback/dry-run packet | Required before any destructive import/rebuild; must name rollback anchor and cleanup/existence proof. |

Minimum artifact rules:

- First line must be `D:YYYY-MM-DD | Check:<source/date> | Confidence:<label>`.
- Each artifact must list sources inspected, commands/actions run, records created/cleaned, key findings, blockers, and confidence.
- Any truncated command output must be rerun with narrower capture or treated as incomplete.
- Missing artifact means `[NO EVIDENCE]`, not informal confidence.
- Representative proof must be labeled representative; it cannot be promoted to full-catalog proof.

## Preventing artifactless or truncated research from becoming false confidence

- Lane F may not cite a lane unless the lane has an artifact path and a status block.
- Lane F must include an evidence table with one row per claim and one witness path per row.
- Claims from missing Lane A/E must be marked `[NO EVIDENCE]` and excluded from readiness conclusions.
- Verifier output that is truncated, deadlocked, skipped, stale, or not saved must count as a blocker for that specific claim.
- Browser observations without backend record proof cannot prove fulfillment/order/quote preservation.
- Backend verifier proof without browser/customer-visible proof cannot prove launch readiness.
- Code inspection alone cannot prove checkout, payment, email, media, or full-catalog behavior.
- “Passed” language must name the exact verifier, product/payload, date, and artifact path.
- Banned generic claims remain banned: “checkout works,” “ERPNext ecommerce works,” “all products ready,” “payments work,” “backend has the details,” or “ready for launch.”

## Concise actionable next sequence

1. Rerun **Lane A** artifact-first; if not possible, create an explicit `[NO EVIDENCE]` blocker artifact rather than relying on older source claims.
2. Rerun **Lane E** artifact-first; reconcile catalog_data/source, ERPNext/Frappe docs/current behavior, project capabilities, and agent actions.
3. Resolve/sign the **version witness decision** for catalog_data source and ERPNext destination image/app versions.
4. Rerun **aggregate architecture readiness** cleanly in the intended ecommerce mode and save the report path.
5. Build the **53-product launch proof matrix** and mark every product checkout / quote-first / excluded / blocked.
6. Prepare human-review packets for **prices, add-ons, color/customization semantics, and media classification**.
7. Only after those artifacts exist, run **Lane F synthesis** with explicit claim-to-witness mapping and blockers.
8. After Lane F, choose one smallest safe proof batch; do not purge/import/rebuild until GL/Jeff approves destructive scope, rollback, and success criteria.
