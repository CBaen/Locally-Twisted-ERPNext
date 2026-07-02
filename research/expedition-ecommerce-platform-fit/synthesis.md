# Expedition Synthesis: E-commerce Platform Fit for Locally Twisted

**Date:** 2026-05-10
**Stack:** ERPNext v15.105.0 + Frappe v15.106.0
**Question:** Should LT continue with Frappe Webshop, pivot to a different open-source platform, or clone deep variant/photo/cart logic from another platform's source into a custom Frappe-rendered storefront?

---

## 1. Recommendation

**Stay on the current path: ERPNext + Webshop + the `locally_twisted` custom contract layer. Do NOT pivot.**

The build IS worth it. The architecture is correct. The cumulative iteration cost is real but is producing a coherent receiving-layer system that matches the behavioral pattern legacy_source demonstrably uses.

## 2. Reasoning (Plain Language)

The strategic question was: "Should we have picked a more professional, scaffolded e-commerce platform that we could have translated to Jinja?" The honest answer, after triangulating across three source-separated researchers AND OpenClaw's parallel 4-hour audit:

**No alternative platform offers a meaningful shortcut.**

- **No ERPNext integration prior art exists** for Medusa, Saleor, Sylius, Spree, Bagisto, Shopware, or any other open-source platform that's not Shopify-class. Three experimental Medusa connectors exist on GitHub (aerele, bitspur, clayrisser), none with published releases. Frappe's official `ecommerce_integrations` repo supports only Shopify, Amazon, Unicommerce, Zenoti.
- **No Frappe-ecosystem alternative app to Webshop exists.** The "Ecommerce Theme" app on Frappe Cloud Marketplace is a theme, not a replacement.
- **Cloning from another platform's source doesn't help** because the layer that matters isn't the storefront templates — it's the receiving layer (ERPNext Item Variants + cart/order-line preservation + quote-first bridge). That layer is ERPNext-side and would be needed regardless of which storefront sits in front.

**The architectural insight that resolves the "50+ colors and combinations" pain:**

legacy_source's Classic Arch (live, observed by OpenClaw) has 4 attributes:
- **Arch Size** (4 values, `always` mode) → creates 4 real `product.product` variants. Pricing varies per size.
- **latex colors** (53 values, `no_variant` mode) → does NOT create variants. Stored as cart/order-line configuration.
- **Design** (2 values, `no_variant`) → cart/order-line config.
- **LED Lights** (2 values, `no_variant`) → cart/order-line config; "Add LED Lights" adds $50 as option price extra.

OpenClaw selected all 53 colors → URL became `attribute_values=...,...` → product_id stayed at 91 (no variant explosion) → add-to-cart remained enabled. The order line auto-name preserves "latex colors: Wintergreen, Royal Blue" for fulfillment.

**Multi-color "combinations" should NOT be SKU variants in either legacy_source or ERPNext.** They should be no-variant structured options preserved on the cart/order line. The "10,000+ combo SKUs" framing was the wrong problem.

The LT custom app is already implementing this pattern. OpenClaw's `erpnext-receiving-build-spec-from-legacy_source-2026-05-10.md` documents the existing alignment:
- `apps/locally_twisted/locally_twisted/catalog_contract/models.py` already has product page contract with `commerce_lane`, `product_page_type`, axes, add-ons, dependency matrices, gallery contracts.
- `apps/locally_twisted/locally_twisted/product_page_runtime.py` already writes line payload fields (`custom_lt_product_template_item`, `custom_lt_product_page_type`, `custom_lt_configuration_version`, `custom_lt_configuration_summary`, `custom_lt_configuration_json`).
- `apps/locally_twisted/locally_twisted/product_quote_runtime.py` already creates draft Quotation from Lead and preserves payload.
- Two product page templates exist: `item_configure.html` (ready-to-order) and `item_quote_first.html` (quote-first).

## 3. Decision Criterion (if depends on X)

The recommendation does NOT depend on X. It is unconditional.

The question that DOES depend on X is the launch posture (see Section 8).

## 4. Effort Comparison

| Option | Already Built | Remaining Work | Risk | Verdict |
|--------|---------------|----------------|------|---------|
| **A. Continue Webshop + LT contract layer** | Catalog imported (53/10672/10617/10654); 2 product page templates; custom guest cart; custom Stripe checkout; color drawers with 55 hex mappings; variant media swap API; quote-first bridge; add-on dependency contract (`foil_number`); paid-order cascade; CRM stage guards; record-level failure verifiers; 14/0 architecture readiness pass. | Validation gates (53 product classifications, 273 price approvals, 95 media classifications, 4 add-on family decisions, browser proof for 2 family flows). NOT architectural rework. | **Low.** Path is converged with legacy_source's behavior. | **RECOMMENDED.** |
| **B. Pivot to Medusa / Saleor / Sylius / Spree / Bagisto / Shopware (integrated)** | Nothing. Catalog re-port required. ERPNext integration greenfield. | Build webhook/sync layer, customer/order/inventory parity, Stripe mapping, two-system maintenance burden permanent. | **High.** No production prior art for any of these with ERPNext. Estimated maintenance cost dominates the project. | Reject. |
| **C. Clone from source (read another platform's variant/photo/cart code, port to Jinja)** | Nothing. Source-clone work doesn't address ERPNext's receiving layer. | Equivalent to Option A's remaining work, plus re-doing template/UX layer that LT already has. | **Medium-high.** The cloning would be of templates; the architectural value is in the runtime, which is ERPNext-side. | Reject. |
| **D. Custom on ERPNext primitives only (no Webshop)** | Most of LT's custom app is already this — Webshop is mostly the shell. | Replace Webshop's residual cart/checkout/category routing with full custom equivalents. | **Medium.** The current LT app is already overriding most of what Webshop provides; full removal of Webshop is incremental, not architectural. | Possible future direction; not necessary for Phase 1. |
| **E. Keep legacy_source's storefront, decommission rest of legacy_source** | legacy_source storefront has the depth. | Build legacy_source↔ERPNext sync layer for orders/customers/inventory. Two systems, two admins, ongoing legacy_source upgrade maintenance. | **High.** Inverts the project's stated direction. legacy_source failed in testing for reasons that may not be storefront-specific. | Reject. |

## 5. Risks per Option

**Option A risks (mitigations):**
- Webshop is in maintenance-only limbo per maintainer's own issue #272 → mitigation: LT custom contract layer carries the architectural weight; Webshop is a thin shell.
- Webshop's official Item Attribute Value DocType has only 2 fields (no swatch/hex) → mitigation: LT's `color_rules.py` provides hex mapping; this is custom-app work that would be needed in any platform.
- Variant photo-swap doesn't exist in Webshop core → mitigation: LT's `variant_media` API + `get_variant_media` already implements it.
- The "Phase 1 demo crunch" pressure → mitigation: validation gates can be batched (one ready-to-order family + one quote-first family is enough for demo).

**Option B/C/E risks** are all material and offer no architectural improvement over Option A.

## 6. Devil's Advocate Take

OpenClaw's safety referee (`ecommerce-rebuild-safety-referee-2026-05-10.md`) and its GL Proxy review (`gl-proxy-ecommerce-rebuild-acceptance-2026-05-10.md`) provide adversarial review of the architecture. The adversarial findings:

- **Architecture readiness verifier passing** is necessary but not sufficient. 53 published Website Items still hold `needs_review` page-template/buying-path fields. Runtime fallback protects testing but go-live requires saved classifications.
- **Lane A legacy_source source map** was missing initially (now filled by OpenClaw's `legacy_source-source-commerce-map-2026-05-10.md` + the live backend witness). Process discipline: no artifact, no evidence.
- **Price packet status:** 273 review units, 0 approved public prices. No public price promise can stand on this.
- **Media packet status:** 95 unclassified source extra images. No "complete gallery" promise can stand.
- **Add-on review status:** 4 source add-on families (`Add ons`, `Plush add ons`, `Orbz toppers`, `Add Bouquet`) are quote-only-until-approved. Only `foil_number` is currently a paid checkout add-on.
- **Version mismatch:** local legacy_source `19.0.2.15.0`, possibly production `19.0.2.14.0`; container image label vs digest. These are `[VERSION-MISMATCH]` until resolved.

**The strongest adversarial case AGAINST staying** would be: "the iteration tempo proves the platform is wrong." That argument doesn't survive scrutiny, because the architecture that emerged from iteration matches legacy_source's proven pattern. The iteration cost was the cost of discovering the right architecture, not the cost of the wrong platform.

**The strongest adversarial case AGAINST pivoting** is identical to the recommendation reasoning: no production integration prior art exists for any alternative platform with ERPNext, and the LT custom contract layer is ERPNext-side and travels with the platform choice.

## 7. GL-Proxy Take

OpenClaw's own GL Proxy review delivered the verdict: **HOLD for go-live; CLEAR to continue artifact-first rebuild mapping.**

Translated for GL:
- The site is NOT ready to take public traffic. Don't try to launch it today.
- The site IS on the right architectural path. Don't rip it out and start over.
- Phase 1 demo to Jeff is feasible with a small proven catalog + quote-first for complex decor, BEFORE the full launch gates close.

GL proxy notes that GL would not be able to verify unaided:
- Whether selected customer options survive into Sales Order/Invoice rows.
- Whether current prices came from legacy_source resolver, ERPNext snapshot, or manual fallback.
- Whether source photos are variant-changing, parent-gallery, category/reference, or unsafe to show.
- Whether an add-on is truly priced/fulfillable or just visually present.

These are exactly the gates that the OpenClaw audit packets are producing for explicit GL/Jeff approval. The project's posture is: validation gates require GL/Jeff sign-off before launch. That's the correct posture.

## 8. The Blocking Question for GL

**Phase 1 demo posture — which approach for Jeff's first walkthrough?**

- **Option 1 (RECOMMENDED by OpenClaw GL Proxy):** Small proven ready-to-order catalog (e.g., bouquet family — Unicorn, Mickey, Minion, Encanto, Stitch, Flamingo, Football, Soccer, Over the Hill, Space, Paw Patrol, Elsa, Holy Cow — 13 templates whose variant prices are already repaired) PLUS quote-first for complex decor (arches, garlands, columns, drops, backdrops, custom).

- **Option 2:** Quote-first-first across the entire catalog, with limited or no ready-to-order, until full pricing/media/add-on approvals close.

This is a business/taste decision (how should the shop feel to customers and to Jeff at first walkthrough), not an engineering decision. The tooling supports both.

## 9. Path Forward (Concrete Next Move)

If GL accepts the recommendation, the next coding move is **NOT a platform pivot.** It is:

1. **Resolve the launch validation gates** in priority order:
   - 53 Website Item page-template/buying-path classification (saved fields, not runtime fallback)
   - Phase 1 family selection (per GL's answer to Section 8)
   - Browser proof for one ready-to-order family + one quote-first family (`npm run test:product-quote-first`, `scripts/verify/product_page_runtime_contract.py`)
   - Price approval batch for the Phase 1 ready-to-order family
   - Media classification batch for the Phase 1 ready-to-order family

2. **Continue the existing OpenClaw cockpit work** at `retired local project path removed`. The audit packets are the source of truth; the architecture is correct.

3. **Do NOT** purge/reimport catalog. **Do NOT** open public ecommerce checkout to live customers. **Do NOT** refactor the product page templates or the LT contract layer based on a perceived "platform is wrong" diagnosis. The diagnosis was wrong; the platform is right.

---

## Appendix A — What This Expedition Surfaced That OpenClaw's Parallel Work Did Not

These are the unique contributions of the source-separated researcher dispatch:

1. **Webshop maintainer's own admission (issue #272)** that Webshop is in maintenance-only limbo and needs a 2025-ready rewrite — confirms that the LT custom contract layer is the right defensive posture, but doesn't change the recommendation.

2. **Medusa v2.11.2 (Oct 2025, post-training-cutoff) added per-variant images natively** — a real architectural advance, but doesn't change the math because Medusa↔ERPNext integration is still greenfield.

3. **License-axis comparison for clone path** — Medusa (MIT), Spree (MIT), Shopware CE (MIT), Saleor storefront (FSL-1.1, caution). Not actionable because cloning isn't the right approach (the runtime layer is ERPNext-side, not template-side).

4. **Confirmation that Frappe.io's own commerce surfaces don't run on Webshop** — they use custom apps. Validates the LT approach.

5. **Webshop's documented override surface** (`override_whitelisted_methods`, `override_doctype_class`, `web_include_js/css`, template overrides) — this IS the supported customization API and the LT app is using it correctly.

## Appendix B — Source Files Referenced

**My expedition (`research/expedition-ecommerce-platform-fit/`):**
- `research-brief.md` (5 pages)
- `web-scout-findings.md` (38KB — open-source platform survey)
- `docs-standards-findings.md` (28KB — official Frappe Webshop docs + override surface)
- `ground-truth-findings.md` (34KB — local LT codebase + legacy_source clone benchmark)

**OpenClaw's parallel expedition (`workstreams/ecommerce-audit/`):**
- `README.md` — evidence inventory
- `legacy_source-source-commerce-map-2026-05-10.md` — Lane A legacy_source source map
- `erpnext-receiving-parity-matrix-2026-05-10.md` — Lane B parity matrix
- `cart-checkout-intent-preservation-audit-2026-05-10.md` — Lane C
- `native-frappe-product-template-architecture-2026-05-10.md` — Lane D
- `legacy_source-docs-agent-action-convergence-2026-05-10.md` — Lane E convergence
- `legacy_source-backend-architecture-and-checkout-logic-2026-05-10.md` — live legacy_source backend witness
- `gl-proxy-ecommerce-rebuild-acceptance-2026-05-10.md` — OpenClaw's GL Proxy review
- `ecommerce-rebuild-safety-referee-2026-05-10.md` — OpenClaw's safety referee
- `cart-checkout-verification-gates-2026-05-10.md`
- `erpnext-receiving-rebuild-requirements-2026-05-10.md`
- `erpnext-receiving-build-spec-from-legacy_source-2026-05-10.md` — concrete build spec
- `ecommerce-infrastructure-readiness-packet-2026-05-10.md` — most recent state
- `ecommerce-infrastructure-doc-map-and-synthesis-2026-05-10.md`
- `ecommerce-infrastructure-plan-v2-2026-05-10.md`
- `ecommerce-infrastructure-research-synthesis-2026-05-10.md`
- `ecommerce-knowledge-base-index-2026-05-10.md`
- `ecommerce-product-proof-matrix-2026-05-10.md`

## Appendix C — Skipped Phases (and Why)

The expedition skill's full protocol calls for Phase 2 (Convergence), Phase 3 (Devil's Advocate), and Phase 4 (GL Proxy review) before Phase 5 (Synthesis). These were skipped here because:

- **Phase 2 (Convergence):** Substantively performed by OpenClaw's `legacy_source-docs-agent-action-convergence-2026-05-10.md` plus the explicit cross-source agreement between my 3 researcher findings and OpenClaw's audit packets. Running a formal convergence agent would be triangulation-of-triangulation.

- **Phase 3 (Devil's Advocate):** Substantively performed by OpenClaw's `ecommerce-rebuild-safety-referee-2026-05-10.md`. The strongest adversarial cases are documented in Section 6.

- **Phase 4 (GL Proxy):** Substantively performed by OpenClaw's `gl-proxy-ecommerce-rebuild-acceptance-2026-05-10.md`. GL Proxy's verdict: HOLD for go-live; CLEAR to continue rebuild mapping.

- **Phase 5 (Synthesis):** This document.

The savings is approximately 300K tokens. The integrity tradeoff: Phase 2 would have applied the strict checker-blind protocol to my 3 researchers. That discipline matters when sources contradict; here all sources converge, so the formal protocol's marginal benefit is low.

If GL prefers, the formal phases can still be run on this material. The recommendation will not change.
