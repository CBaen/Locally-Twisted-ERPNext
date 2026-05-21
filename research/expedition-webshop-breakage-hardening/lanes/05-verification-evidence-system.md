# Lane 05 - Verification Evidence System

## Decision Question

What proof system prevents future agents from claiming the Locally Twisted Webshop launch is safe without saved evidence for route discovery, desktop/mobile browser health, dynamic product coverage, staging/live base URLs, and rollback-safe checkout behavior?

## Primary Sources

- Research brief: `research/expedition-webshop-breakage-hardening/research-brief.md:3`, `:11-18`, `:30`.
- Playwright: [configuration](https://playwright.dev/docs/test-configuration), [use options](https://playwright.dev/docs/test-use-options), [projects](https://playwright.dev/docs/test-projects), [reporters](https://playwright.dev/docs/test-reporters).
- Frappe: [Portal Pages](https://docs.frappe.io/framework/user/en/portal-pages), [Hooks / Website Route Rules / Portal Assets](https://docs.frappe.io/framework/user/en/python-api/hooks).
- Local verifier entrypoints: `scripts/verify/website_launch_verify.py`, `scripts/verify/public_asset_integrity.py`, `scripts/verify/public_network_integrity.spec.js`, `scripts/verify/smoke_shop.py`, `scripts/verify/layout_helpers.js`, `scripts/README.md`, `package.json`.

## Local Evidence

- The brief explicitly rejects green claims without saved output, route list, base URL, date, and command, rejects stale product counts, and rejects localhost-only staging/live claims (`research-brief.md:11-18`).
- `website_launch_verify.py` is a useful serial gate with `--base-url` / `LT_BASE_URL`, readiness probing, and named steps (`scripts/verify/website_launch_verify.py:131-180`, `:273-315`), but it mostly prints stdout and deletes `test-results` before each Playwright step (`:66-68`, `:210-216`).
- `public_asset_integrity.py` discovers routes by regexing `layout_helpers.js` plus a fixed `EXTRA_ROUTES` list, then checks same-origin assets, MIME, CSS dependencies, and raw spaces (`scripts/verify/public_asset_integrity.py:20-30`, `:88-94`, `:202-259`). It does not retain a route manifest or artifact.
- `public_network_integrity.spec.js` checks console warnings/errors, page errors, same-origin failed requests, asset HTTP status, and MIME (`scripts/verify/public_network_integrity.spec.js:38-83`), but it forces one desktop viewport only (`:79`).
- `layout_helpers.js` has richer route and viewport contracts (`scripts/verify/layout_helpers.js:6-47`, `:152-363`) and container/layout checks (`:365-870`), but product route samples are still handpicked (`:25-29`, `:306-329`).
- `smoke_shop.py` covers public nav, categories, quote-first pages, retail variant controls, add-to-cart, and mobile drawer, but it hard-codes categories/products and skips open-commerce checks when ecommerce is paused (`scripts/verify/smoke_shop.py:56-94`, `:803-980`, `:1081-1136`).
- `playwright.config.js` currently has one Chromium profile, line reporter, no Playwright `baseURL`, no desktop/mobile projects, and no screenshot/trace/video artifact policy (`playwright.config.js:23-35`).
- Checkout proof exists in layers: `checkout_experience.spec.js` only proves cart/checkout follow the configured lane at mobile width (`scripts/verify/checkout_experience.spec.js:23-61`); `cart_checkout_contract.py` proves backend cart/checkout rejection and line preservation (`scripts/verify/cart_checkout_contract.py:630-666`); `post_import_checkout_proof.js` writes JSON and covers desktop/mobile, cart, checkout, and preview totals (`scripts/verify/post_import_checkout_proof.js:46-49`, `:453-543`) but still defaults to a `53` product count (`:43-55`), which conflicts with the brief's current `51` Website Items.
- The strongest rollback-safe local checkout wrappers are `simple_purchasable_browser_proof.py` and `multi_color_purchasable_browser_proof.py`; both temporarily open ecommerce, run browser proof, restore Website Item contracts, restore `lt_ecommerce_paused`, and clear cache in `finally` (`scripts/verify/simple_purchasable_browser_proof.py:121-162`, `scripts/verify/multi_color_purchasable_browser_proof.py:165-208`).
- Staging/live has a separate public HTTP guard in `cloudflare_launch_readiness.py` with required `--base-url`, HTTPS enforcement unless local `--allow-http`, dynamic route/cache/challenge checks, and a Stripe webhook reachability probe (`scripts/verify/cloudflare_launch_readiness.py:1-10`, `:24-35`, `:101-112`, `:192-245`).

## Findings

1. The current launch proof is a gate, not an evidence system. It can fail loudly, but a pass is not retained with route source, base URL, product sample source, app versions, command transcript, or artifacts.
2. Route authority is fragmented across Frappe `www` pages, `website_route_rules`, LT route aliases, Webshop generated routes, `Website Item` records, `layout_helpers.js`, and hard-coded verifier samples. Frappe's docs support this split: `www` files map to URLs, controllers share names with page files, and route rules map clean/dynamic URLs to controllers.
3. Browser network proof is underpowered for launch claims. It is desktop-only today, while Playwright officially supports projects for mobile/desktop devices, per-project environments, `baseURL`, reporters, and retained screenshots/traces/videos.
4. Product proof is too static. Any proof that still assumes `53` products is already suspect against this brief's `51` Website Items. Product sampling must come from live `Website Item` rows and classify samples by commerce lane, route, item group, variant/single SKU, quote-first, color/add-on complexity, and checkout eligibility.
5. Checkout safety is the best-developed piece, but it is split across local-only wrappers, backend contracts, browser proofs, and paused public-route tests. Future agents need one command packet that says which checkout paths are safe to run on local, staging, and live.
6. Staging/live claims must be quarantined unless the base URL is explicit and saved. `LT_BASE_URL` support exists, and Cloudflare readiness exists, but the main Playwright config does not make environment/base URL an auditable project dimension.

## Resolution Recommendation

**Refresh.** Support the existing verifier components, but refresh them into one retained evidence system before accepting any launch/pass claim.

Quarantine staging/live readiness and open-checkout claims until the refreshed system saves artifacts for the exact base URL tested. Eliminate stale hard-coded product counts from launch proof. Rebuild only the evidence harness and route/product manifest layer; do not rebuild the storefront or discard the existing verifiers.

## Required Tests

- Route manifest gate: generate and save `route-manifest.json` from Frappe `www` pages, `website_route_rules`, `Website Item` routes, item-group/category routes, required dynamic routes, and expected removed/redirect routes. Include base URL, date, git commit, app versions, DB counts, route source, and sample reason.
- Public asset gate: run `public_asset_integrity.py` against the manifest and save JSON/Markdown output, not only stdout.
- Desktop/mobile network gate: run the same route manifest through Playwright desktop and mobile projects; fail on console warning/error, page error, same-origin request failure, asset `>=400`, wrong MIME, unexpected redirects, and uncaptured route.
- Layout/container gate: keep `npm run test:layout-fit`, `npm run test:container-contract`, and `npm run test:interactive-layout`, but bind them to the same route manifest or record why a route is excluded.
- Dynamic product sampling gate: sample from live `Website Item` records by lane and type, then run product price, visible price display, variant media, quote-first, cart, and category checks against that sample. Static products may remain as named regressions, not as full coverage.
- Rollback-safe checkout gate: local open-commerce proof must use wrappers that snapshot, mutate, run browser proof, restore Website Item contracts, restore `lt_ecommerce_paused`, clear cache, and save proof JSON. Staging/live checkout must remain paused or use no-payment/non-mutating preview tests unless the payment gate is explicitly reopened.
- Staging/live URL gate: run `cloudflare_launch_readiness.py --base-url <https-url> --json` for staging/live and save output. A localhost pass cannot satisfy this gate.
- Evidence bundle gate: `website_launch_verify.py` should create one timestamped evidence directory with command packet, stdout/stderr per step, exit codes, route/product manifests, Playwright HTML/blob/json/JUnit output, traces/screenshots/videos on failure, and a final summary that lists skipped/not-run gates.

## Remaining Gaps

- This lane is design only; no verifier was executed.
- No current single source of truth exists for route discovery or product sampling.
- No mobile network gate exists today.
- No retained launch-evidence directory exists today.
- No staging/live base URL was provided in this lane.
- The post-import checkout proof still carries a `53` default product count and must be refreshed against current DB truth before it can be launch evidence.
