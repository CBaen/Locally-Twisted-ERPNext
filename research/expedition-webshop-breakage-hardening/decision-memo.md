# Extended Expedition Decision Memo - Webshop Breakage Hardening

Date: 2026-05-21

## Decision

Do not treat the current storefront as launch-green. Treat it as locally recovered with five hardening lanes. The correct path is not a broad storefront rewrite; it is a targeted proof-system rebuild, a product-truth refresh, replacement of fragile Webshop monkey patches, and a clean recreate/deploy evidence run before any staging/live or open-checkout claims.

## Five-Lane Evidence

### 1. Static Assets And MIME

- Disposition: **Support + Refresh**
- Support the real Frappe/Webshop asset contract: Webshop bundle names are built by `bench build`, resolved through `assets.json`, and served from `/assets/webshop/dist/...`.
- Refresh the shared runtime manifest after local rebuild/recreate because the Docker `sites` volume owns `sites/assets/assets.json`.
- Quarantine `--runtime-only`; it is emergency diagnosis only.
- Fresh local proof from lane: `public_asset_integrity.py` passed `31` routes / `291` asset URLs; `npm run test:public-network` passed `31/31`.

### 2. Recreate And Deploy Durability

- Disposition: **Refresh + Quarantine**
- Current localhost asset/network proof is baseline health, not recreate, fresh-volume, Frappe Cloud, or Cloudflare proof.
- Support the image-baked Webshop asset direction.
- Eliminate `--runtime-only` as launch proof.
- Quarantine ready-to-order, product/category, cart, checkout, staging, and live claims until rebuild/recreate/cache/staging proof is retained.
- `scripts/deploy.py` is stale for this lane and should not be used as proof until refreshed.

### 3. Guest Commerce Contract

- Disposition: **Support Bridge + Rebuild Fragile Pieces**
- Support the narrow guest-safe product-info concept and the `Website Item` override as a guarded v15 bridge.
- Keep public whitelisted wrappers as the seam.
- Quarantine the current process-global monkey patches in product listing and variant selector.
- Rebuild those two paths as LT-owned adapters that do not mutate upstream Webshop module globals.
- Preserve Guest platform plumbing; native Webshop can still use `get_party()` in future cart/address/order paths.

### 4. Product Truth And Classification

- Disposition: **Refresh + Quarantine**
- Live DB truth is `51` Website Items, not `53`.
- The two-product gap from old source/export history is exactly `easter-arch` and `pride-arch`.
- `easter-arch` remains as a disabled, unpublished Item with no Website Item and no Item Prices.
- `pride-arch` is absent from current Item / Website Item / Item Price objects.
- Current code accepts `51`, but no clean business/source disposition was found for those two old products, so they stay quarantined until explicitly eliminated, rebuilt, or refreshed.
- Stale docs/tests still mention `53` and four simple purchasable products / `33` sale SKUs; those must not be release proof.

### 5. Verification Evidence System

- Disposition: **Refresh**
- Current verifiers can fail loudly, but they do not retain enough evidence to prevent overclaims.
- Refresh the proof system around route manifests, product manifests, desktop/mobile browser network checks, exact base URL, command output, DB counts, app versions, and rollback-safe checkout artifacts.
- Quarantine staging/live and open-checkout claims until evidence bundles exist.
- Eliminate stale hard-coded product counts from launch proof.

## What The Evidence Rewards

- Small, named gates with retained outputs beat one giant remembered terminal run.
- Frappe-native contracts matter: bundle names, `assets.json`, `/assets/[app]/dist/...`, hooks, and installed app order.
- Localhost, staging, and live are separate truth surfaces.
- Product catalog truth must combine source manifest, live DB, and business disposition.
- Guest commerce can be supported, but only if LT owns the adapter boundary and tests upstream drift.

## Disqualifying Evidence

These facts block any launch-green claim:

- Full launch verifier has not been retained/proven green after the recent changes.
- Clean rebuild/recreate/fresh-volume/staging durability has not been proven.
- `easter-arch` and `pride-arch` lack explicit business/source dispositions.
- Product-listing and variant-selector fixes still use monkey patches.
- Verification output is not yet saved as a complete evidence bundle.
- Some docs/tests still preserve stale `53`, `4 products`, or `33 sale SKUs` claims.

## Recommended Path

1. **Quarantine claims now.** Say: local asset/network proof passed; full launch, staging/live, recreate durability, and open checkout are not proven.
2. **Refresh product truth.** Create a manifest of all source slugs with current DB status and disposition. Put `easter-arch` and `pride-arch` in `quarantined` until GL/source approval says eliminate or rebuild.
3. **Rebuild verification evidence.** Add route/product manifests, mobile+desktop network checks, saved output directories, and base-url-specific summaries.
4. **Replace monkey patches.** Keep the guest-safe bridge, but rebuild product listing and variant selector as explicit LT adapters without mutating upstream globals.
5. **Run clean durability proof.** Durable rebuild, forced recreate, cache clear, manifest/HEAD/MIME checks, asset/network checks, then the refreshed launch gate. Repeat against staging with `LT_BASE_URL`.
6. **Only then reopen checkout proof.** Use rollback-safe local checkout gates; keep staging/live payment/checkout paused until the payment gate is explicitly reopened.

## Resolution Matrix

| Issue | Concrete Resolution | Current Disposition | Required Proof |
|---|---|---|---|
| Static asset/MIME break | Use real Webshop built bundles and manifest-resolved `/assets/webshop/dist/...` URLs | Support + refresh | Asset integrity, browser network, manifest CSS/JS MIME, retained output |
| Recreate/deploy durability | Prove image-baked bundles survive force recreate, cache clear, fresh volume/staging | Quarantine until proven | Durable rebuild, force recreate, cache clear, fresh/staging `LT_BASE_URL` evidence |
| Guest commerce crash | Keep guest-safe product info bridge; replace monkey-patch internals | Support bridge; rebuild patches | Hook-order guard, source-drift test, anonymous category/product/variant/cart checks |
| Product truth/count drift | Manifest source slugs and dispositions; quarantine missing two | Refresh + quarantine | Source-vs-DB verifier, explicit disposition for `easter-arch` and `pride-arch` |
| Verification overclaims | Evidence bundle system with route/product manifests and desktop/mobile gates | Refresh | Saved command outputs, base URL, app versions, DB counts, route/product manifests |

## What Not To Do

- Do not call the site launch-green from the current local proof.
- Do not run or cite `--runtime-only` as a durability fix.
- Do not keep expanding monkey patches.
- Do not use stale `53` product docs as current DB truth.
- Do not run record-creating checkout/payment tests on staging/live without explicit gate approval.
- Do not use `scripts/deploy.py` as asset/deploy proof until it is refreshed.

## Confidence And Gaps

Confidence is high for the local facts: current DB count, missing product identities, current asset/network local pass, and the specific fragile code seams. Confidence is medium for the final implementation path because clean recreate/fresh-volume/staging proof has not been run yet. The biggest remaining gap is not knowledge; it is retained evidence. The next work should build that evidence system first, then use it to prove or reject each concrete fix.
