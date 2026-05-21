# Ecommerce Break Lab - 2026-05-21

Status: local-only break lab completed, restored, and guarded through first
expected-mode verifier additions.

Safe return:

- Git safe return commit: `e0ec264`
- Git safe return tag: `safe/ecommerce-prebreak-2026-05-21-e0ec264`
- Local bench backup with files:
  `./frontend/private/backups/20260521_122152-frontend-database.sql.gz`
- Site: local Docker ERPNext/Frappe site `frontend` at
  `http://localhost:8081`
- No staging, live, DNS, Frappe Cloud, Stripe live, provider, or indexing work
  was touched.

## Current Restored State

After the break probes, the local site was restored to the intended open local
testing mode:

- `lt_ecommerce_paused = 0`
- `Customer:Guest`, `Portal User:Guest -> Customer Guest`,
  `Contact:Guest-Guest`, and the Dynamic Link are present.
- `Webshop Settings.hide_price_for_guest = 0`
- `Standard Selling` remains the public price list.
- `npm run test:webshop-guest-party` passes with `11/11` runtime guard probes
  blocked.
- `npm run test:ecommerce-open-mode` passes.

## Final Restore Verification

Verified after all break probes were restored:

```powershell
python -B -m py_compile apps\locally_twisted\locally_twisted\verify\ecommerce_break_lab.py scripts\verify\ecommerce_expected_mode.py
npm run test:ecommerce-open-mode
npm run test:webshop-guest-party
npm run test:owner-catalog-guard
python scripts\verify\cart_checkout_contract.py
python scripts\verify\stripe_amount_parity_contract.py
npm run test:human-access
npm run test:product-prices
npm run test:product-price-display -- --workers=1 --grep "variant size"
npm run test:public-assets
npm run test:public-network -- --workers=1
npm run test:seo-contract -- --workers=1
```

Result:

- expected local ecommerce open mode passed;
- Guest party contract passed with `11/11` runtime guard probes blocked;
- owner catalog guard passed, blocking owner-like direct edits while allowing
  guarded Product Blueprint context;
- cart/checkout contract passed;
- Stripe amount parity contract passed;
- human access silo matrix passed, with external marketing access parked;
- product price and modifier contracts passed for `49` products /
  `10,186` active variants;
- product visible price update passed for variant size selection;
- public asset integrity passed for `31` routes / `291` unique local assets;
- public network integrity passed `31/31`;
- SEO contract passed `12/12`.

## Triad Witnesses

Witness A, public storefront/assets/SEO/network, stayed read-only. It ranked
these release blockers and footguns:

- ecommerce pause exposed or hidden in the wrong stage;
- SEO host/canonical/sitemap drift before Search Console work;
- asset wiring/cache-bust drift that keeps routes at `200` while JS/CSS breaks;
- route/nav/search regressions that leave customer paths dead;
- mobile/container/Webshop structure breakage that desktop checks miss.

Witness B, cart/checkout/payment/order blast radius, stayed read-only. It
ranked these owner-important failures:

- Guest party cleanup breaks Webshop pricing, variant, cart, and POST paths;
- ecommerce pause opened before owner approval;
- quote-first or custom products become purchasable;
- options/add-ons/notes collapse between cart, checkout, Sales Order, invoice,
  and operator evidence;
- Stripe/payment reconciliation drifts from ERPNext totals or metadata.

Witness C, permissions/data/cleanup, stayed read-only. It ranked these access
and data failures:

- broad cleanup deletes Guest plumbing;
- marketing reviewer gets helpful extra roles or DocPerm rows;
- customer portal settings drift into public signup or stock ERPNext routes;
- public Guest write endpoints expand without an allowlist;
- destructive import or fake-data cleanup uses a broad target.

## Breaks Actually Run

### Break 1 - Wrong Ecommerce Mode

Trigger:

```powershell
bench --site frontend set-config lt_ecommerce_paused 1
python scripts/dev/clear_website_cache.py
```

Observed:

- `python scripts/verify/ecommerce_pause_contract.py` still passed because it
  verifies whichever mode is currently configured.
- `python scripts/verify/ecommerce_expected_mode.py --expect open` failed:
  expected local ecommerce open, but the site was paused.

Blast radius:

- A developer can accidentally hide the owner-review shop while still getting a
  green pause contract.
- The inverse is also dangerous for staging/live: a site could be open when the
  release gate expects it paused.

Seriousness: Release blocker.

Recovery:

```powershell
bench --site frontend set-config lt_ecommerce_paused 0
python scripts/dev/clear_website_cache.py
npm run test:ecommerce-open-mode
```

Prevention added:

- `scripts/verify/ecommerce_expected_mode.py`
- `npm run test:ecommerce-open-mode`
- `npm run test:ecommerce-paused-mode`

Rule:

- Use expected-mode checks when the stage matters.
- Use `ecommerce_pause_contract.py` to prove the configured mode behaves
  internally, not to prove the configured mode is the right stage.

### Break 2 - Direct SQL Deletes Guest Portal User

Trigger:

```powershell
bench --site frontend execute locally_twisted.verify.ecommerce_break_lab.break_guest_portal_link
```

Observed:

- `python scripts/verify/webshop_guest_party_contract.py` failed because the
  Portal User link was missing.
- Public network checks against shop/product/cart/checkout still passed in the
  current code because LT guest-safe overrides masked the old visible crash.

Blast radius:

- Direct SQL can bypass the Frappe `doc_events` guard.
- Native Webshop paths, future cart/address/order paths, cleanup reports, and
  future agents can still be poisoned even if the public route does not explode
  immediately.

Seriousness: Critical hidden infrastructure drift.

Recovery:

```powershell
bench --site frontend execute locally_twisted.verify.ecommerce_break_lab.restore_guest_portal_link
python scripts/dev/clear_website_cache.py
npm run test:webshop-guest-party
```

Prevention:

- Runtime `doc_events` guard already protects normal Frappe saves/deletes.
- Direct SQL still requires cleanup/import wrappers with backup, protected-record
  denylist, dry-run, and post-run `npm run test:webshop-guest-party`.

### Break 3 - Hide Prices For Guest

Trigger:

```powershell
bench --site frontend execute locally_twisted.verify.ecommerce_break_lab.break_guest_price_visibility
```

Observed:

- `python scripts/verify/webshop_guest_party_contract.py` failed:
  `Webshop Settings.hide_price_for_guest expected 0, found 1`.
- Guest variant product info no longer returned product info.
- `npm run test:product-price-display -- --workers=1 --grep "variant size"`
  failed because visible price did not update to the selected variant price.
- Public network checks still passed.

Blast radius:

- Route health can be green while product pricing is wrong.
- Customer sees stale/from/base price behavior instead of actual selected
  variant price.
- Checkout and display can drift.

Seriousness: High / release blocker for open checkout.

Recovery:

```powershell
bench --site frontend execute locally_twisted.verify.ecommerce_break_lab.restore_webshop_settings
python scripts/dev/clear_website_cache.py
npm run test:webshop-guest-party
npm run test:product-price-display -- --workers=1 --grep "variant size"
```

Prevention:

- Keep `npm run test:webshop-guest-party` in any Webshop Settings gate.
- Keep visible price display tests in the release loop.
- Add the future owner catalog guard for `Webshop Settings`.

## Owner Product Operations Break Probes

Additional local owner/product probes are documented in:

- `research/owner-product-operations-break-lab/lanes/02-breakage-probes.md`
- `research/owner-product-operations-break-lab/lanes/03-guard-automation-design.md`

The most important findings from that lane:

- A `Website Item` can be created for a missing `Item`; route can return `200`
  while cart resolution fails.
- A published product without `Standard Selling` price can render but fail cart
  resolution as `unpriced`.
- A disabled `Item` can remain visible through a published `Website Item`; route
  and listing can render while cart returns `unavailable`.
- Route edits immediately create dead old URLs unless a redirect/alias decision
  exists.
- Duplicate active variant attribute combinations can make selector price and
  cart price disagree.

These are developer bite risks because they are normal owner/catalog actions,
not exotic attacks.

## Required Guard Stack Before Ecommerce Release

Minimum local proof for the owner-important ecommerce slice:

```powershell
npm run test:ecommerce-open-mode
npm run test:webshop-guest-party
python scripts/verify/cart_checkout_contract.py
npm run test:product-prices
npm run test:product-price-display
python scripts/verify/stripe_amount_parity_contract.py
npm run test:public-assets
npm run test:public-network -- --workers=1
npm run test:seo-contract -- --workers=1
npm run test:human-access
```

For a paused staging/live gate, replace the open-mode check with:

```powershell
npm run test:ecommerce-paused-mode
python scripts/verify/ecommerce_pause_contract.py
```

## Next Guard Work

1. Expand the owner catalog guard from the current core protected-record proof
   into broader probes for Item Group, Item Attribute, Item Attribute Value,
   Item Variant Attribute, delete/rename paths, and public product media.
2. Add a public internal-link crawler for rendered anchors.
3. Add class/selector-preservation lint for required Webshop hooks.
4. Add a cleanup/import wrapper that refuses broad destructive work unless it
   has a current backup, dry-run, protected-record denylist, and post-run proof.
5. Retain release evidence by base URL, route manifest, product sample, command,
   timestamp, DB counts, and app versions.
