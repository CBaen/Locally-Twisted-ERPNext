# LT Ecommerce Live Readiness Research Brief

### 1. Want

Locally Twisted needs a clear, evidence-backed path from local ecommerce proof to a safe live shop. Success means a customer can browse approved ready-to-order products, choose valid options, check out as a guest, pay through the correct live Stripe setup, receive honest confirmation, and leave matching ERPNext records behind without unfinished product pages, stale SEO surfaces, or hidden backend failures becoming public business risk.

### 2. Have

The project is an ERPNext/Frappe v15 custom app at `/home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted`, with local Docker site `frontend` at `http://localhost:8081` and public pages/forms already served through Frappe Cloud at `https://locallytwisted.com`. Current handoffs to verify first are `CODING-HANDOFF.md`, `locally-twisted-queue.md`, `ECOMMERCE-SHOP-HANDOFF.md`, `LT-LAUNCH-RUNBOOK.md`, `workstreams/shop.md`, `workstreams/website-launch.md`, `workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`, `workstreams/ecommerce-system-safety-guard-plan-2026-05-19.md`, `workstreams/selective-indexing-gate-2026-05-21.md`, and `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`. Fresh controller probes before this brief found local ecommerce open mode passing, local payment readiness passing only in Stripe test mode, local SEO contract passing, live sitemap/canonical still using the Frappe Cloud vanity host, and current local catalog counts differing from older handoffs: 51 Website Items, 10,685 Items, 10,666 Item Prices, 49 templates, 10,629 variants, 10,186 active variants, 443 disabled variants, 32,049 Item Variant Attribute rows, and 30 Item Attributes.

### 3. Won't Accept

- No live checkout claim from docs, memory, or local-only tests.
- No Search Console submission while live sitemap, canonical, robots, or `og:url` still advertise the wrong host or expose unfinished ecommerce discovery.
- No provider mutation, Frappe Cloud deploy, DNS change, Stripe live payment, destructive import, or Search Console action without an explicit release gate.
- No broad staging from the dirty shared checkout; isolate or scope work so unrelated product/catalog/access changes do not ride along.
- No weakening backend-owned product truth to make frontend, smoke, or payment tests pass.
- No forced account creation for customer checkout.
- No exposing products whose price, media, add-ons, selected options, cart payload, Sales Order, invoice, receipt, and owner/operator evidence are not tied together.
- No treating `lt_ecommerce_paused=1` as an implementation blocker; it is a public exposure safety lock.
- No inventing legal/policy/payment copy or business promises.

### 4. Open To

Research may recommend splitting the go-live path into multiple release packets: repo/coordination cleanup, catalog-count reconciliation, SEO/Frappe Cloud release, local checkout proof refresh, staging checkout proof, live Stripe configuration, and final narrow product-scope launch. It may also recommend retiring or updating older verifiers when they conflict with newer source-owned decisions, but only with file-level evidence and replacement proof.

### 5. Questions

1. What is the exact current reason local ERPNext has 51 Website Items while several handoffs still say 53, and is that a legitimate post-cleanup state or a launch blocker?
2. Which dirty/shared files and active coordination claims overlap a live ecommerce release, and what isolation plan prevents unrelated work from shipping?
3. Which verifier expectations are stale or conflicting, especially around `ecommerce_pause_contract.py` versus the newer selective-indexing/noindex rule?
4. What minimum local proof packet must be green before a staging ecommerce release packet is allowed?
5. What Frappe Cloud release steps are required to ship sitemap/canonical/robots/selective-indexing fixes without bundling unrelated product changes?
6. What exact live Stripe configuration, webhook configuration, policy URL wiring, merchant-account confirmation, and low-risk payment test are required before checkout can open?
7. Which product scope should be considered eligible for first live checkout, and which products/media/add-ons must remain quote-first or hidden until later approval?
8. What final go/no-go checklist should separate local proof, GitHub archive, staging gate, live release gate, Search Console/reindex work, and provider cleanup?
