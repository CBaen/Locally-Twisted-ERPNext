# Odoo Reference Boundary Blocker

Date: 2026-05-23
Site: locallytwisted-staging.frappe.cloud
Source commit: e87a6b1039e3c096a1e6c656a989a1d425633363
App mirror hash: 2ec290621e044dcaa9d2c322675ce074ae489f7a

## Plain State

Staging source deployment succeeded, but staging is not owner-review ready.
The shop catalog is still empty on staging.

The bootstrap failed because deploy/runtime catalog seeding depends on local
Odoo reference scrape paths:

- `apps/locally_twisted/locally_twisted/seed/seed_catalog.py`
- expected path: `_resources/odoo-live`
- hosted failure: `_resources/odoo-live not found inside container`

This is a release-blocking architecture problem, not an account-switching
problem. Frappe Cloud has the app code, but it does not have the local reference
folder that the bootstrap assumed would exist.

## Boundary

Guiding Light clarified the governing rule during this attempt:

Anything Odoo is reference-only unless it has been consciously transformed into
Locally Twisted / ERPNext-owned deployable data.

Do not fix staging by force-adding `_resources/odoo-live`, app-side Odoo-named
seed folders, or other Odoo-named reference paths into the Frappe Cloud app
mirror. That would make the historical source system part of the deployable
product surface.

## Verified App-Tree Odoo Coupling

Scoped checks after a truncated broad search found tracked Odoo-named paths in
the deployable app tree:

- 1 catalog contract map:
  `apps/locally_twisted/locally_twisted/catalog_contract/odoo_color_swatch_map.json`
- 53 public color swatch assets under:
  `apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/`
- 2 seed repair scripts:
  `apps/locally_twisted/locally_twisted/seed/repair_variant_prices_from_odoo.py`
  and
  `apps/locally_twisted/locally_twisted/seed/repair_variant_price_modifiers_from_odoo.py`

Also verified: app-side `seed/_data` and `seed/_guard` exist locally but are not
tracked by git. They were not present on Frappe Cloud, which is why source
deployment alone could not populate the staging shop.

## Bad Route

Do not treat the local Odoo scrape as deployable app data.
Do not add an `_staging_guard` or `_data` shortcut that preserves Odoo-named
deploy coupling just to get the link out faster.

An untracked `_staging_guard` attempt created during this investigation was
removed immediately after the boundary was clarified.

## Good Routes

Safe route A:
Create a neutral LT-owned staging seed artifact from the reference scrape, with
lineage documented separately. Deploy code reads from `lt_catalog_seed` or a
similarly neutral path, not `_resources/odoo-live`.

Safe route B:
Upload a neutral LT-owned private staging seed artifact to the site and make the
bootstrap read that explicit staging artifact. This avoids shipping reference
data in the app, but needs a stronger repeatability record.

Safe route C:
Treat the currently tracked app-tree Odoo names as cleanup debt and schedule a
separate rename/migration pass. Do not combine that broader cleanup with the
emergency staging-owner link unless the release controller explicitly accepts
the larger blast radius.

## Release Gate Consequence

No Jeff/owner link may be sent yet.

## Local Hardening Added After Blocker

The local repo now has an executable boundary guard:

- `scripts/verify/odoo_reference_boundary_contract.py`
- package script: `npm run test:odoo-reference-boundary`
- included in: `npm run test:release-prevention`

Local runtime cleanup also moved seed discovery to `lt_catalog_seed`, renamed
color swatch runtime paths/maps to LT-owned names, and moved old reference-site
price repair helpers out of deployable app runtime. This is not staging proof.
It only prevents future agents from treating Odoo/reference paths as deployable
runtime seed data.

The next release attempt must prove all of these, in order:

1. App hash installed on staging.
2. Catalog seed source exists on staging under an LT-owned, non-Odoo deploy path.
3. Bootstrap/RQ job completed successfully, not just enqueued.
4. Staging counts meet owner-review minimums.
5. `/shop` and product routes render on the Frappe Cloud staging host.
6. Checkout remains paused unless a separate payment gate is reopened.
