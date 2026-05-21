### 1. Want

Resolve five website-breaking risk lanes in the Locally Twisted ERPNext/Webshop storefront with evidence-backed decisions for each lane: quarantine, support, eliminate, refresh, rebuild, or accept with a named guard. Success means a future agent can point to current primary-source research, local code/DB evidence, and repeatable tests that prove product pages, category pages, static assets, variant pricing, cart/checkout, and launch verification are safe enough for the next release stage.

### 2. Have

Current local stack is a Docker-based ERPNext/Frappe site at `http://localhost:8081`, compose project `locally-twisted-erpnext-v15`, site `frontend`, running image `locally-twisted-erpnext:v15`. Verified on 2026-05-21: running apps are Frappe `15.106.0`, ERPNext `15.105.0`, Payments `0.0.1`, Webshop `0.0.1`, and Locally Twisted `0.0.1`; live DB counts are `51` Website Items and `10666` Item Prices. Current relevant files include `docker/Dockerfile`, `scripts/dev/build_webshop_assets.py`, `scripts/dev/clear_website_cache.py`, `scripts/verify/public_asset_integrity.py`, `scripts/verify/public_network_integrity.spec.js`, `scripts/verify/website_launch_verify.py`, `scripts/verify/smoke_shop.py`, `apps/locally_twisted/locally_twisted/overrides/website_item.py`, `apps/locally_twisted/locally_twisted/api/product_listing.py`, `apps/locally_twisted/locally_twisted/api/variant_selector.py`, and `apps/locally_twisted/locally_twisted/hooks.py`. Current claims from the prior session say the hidden contact honeypot layout gate passed after a template fix, but the full launch gate is not retained/proven green.

### 3. Won't Accept

- No solution that only works because the current container has mutated writable-layer files.
- No "green" claim without saved output, route list, base URL, date, and command.
- No stale hard-coded product counts; DB truth and business intent must both be identified.
- No fix that hides Webshop/Frappe upstream behavior behind untested monkey patches.
- No checkout/product proof that only tests one happy path while category, variant selector, quote-first, and direct-cart flows remain untested.
- No staging/live claim from localhost-only evidence.
- No broad rewrite unless research shows the current path is fundamentally brittle and cheaper guards cannot make it safe.
- No customer-visible success state when downstream product, price, cart, quote, or checkout behavior is unproven.

### 4. Open To

The investigation may recommend keeping the local Webshop overrides with stronger tests, replacing monkey patches with a more native Frappe/Webshop extension point, rebuilding the Webshop asset build/recreate process, quarantining fragile checkout paths, refreshing product source data/contracts, tightening route discovery, or splitting launch verification into smaller retained evidence gates. Researchers should prefer conservative repairs inside ERPNext/Frappe/Webshop, but may recommend eliminating or rebuilding a lane if primary-source research and local proof show the current lane is structurally unsafe.

### 5. Questions

1. Static asset/MIME lane: according to current Frappe/Webshop primary sources and local Docker evidence, what is the correct durable path for Webshop compiled assets, asset manifests, cache clearing, and recreate/deploy survival?
2. Asset durability lane: what exact test sequence proves the asset fix survives clean rebuild, forced container recreate, cache clearing, and staging/live deployment, and what must be quarantined if it fails?
3. Commerce crash lane: what is the native Frappe/Webshop contract for guest product info, guest cart party/customer resolution, price list selection, category cards, and variant selector calls, and are the current Locally Twisted overrides supportable or should they be replaced?
4. Product truth lane: why is the live DB at `51` Website Items when project instructions still mention `53`, which products were intentionally deleted or changed, and what source-of-truth contract should prevent stale product counts or wrong checkout/quote classification?
5. Verification lane: what proof system is needed so future agents cannot overclaim, including route discovery, mobile/desktop network gates, dynamic product sampling, retained artifacts, staging/live base URLs, and rollback-safe checkout tests?
6. For each lane, what is the concrete disposition: support as-is with tests, refresh data, quarantine flow, eliminate stale path, rebuild implementation, or defer with a named blocker?
