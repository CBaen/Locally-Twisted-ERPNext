# Inquiry Form Live Release - 2026-05-16

## Scope

This handoff owns the 2026-05-16 release of the public inquiry form hardening,
photo storage, owner email attachments, and source-owned contact intake schema
sync to Frappe Cloud live.

It does not own ecommerce product setup, checkout opening, Stripe live payment,
legacy_source catalog edits, marketing-review access design, or broader Paperclip dirty
worktree review.

## Release Receipt

| Surface | Evidence |
|---|---|
| Full repo source | `631f9a8 Run contact intake schema sync on install` |
| Frappe app mirror | `b4b3bf8 Run contact intake schema sync on install` |
| Live site update | `b48j584nua`, `Success` |
| Update job | `b48oge6unq`, `Success` |
| Source bench | `bench-39776-000013-f94-virginia` |
| Destination bench | `bench-39776-000015-f94v` |
| Deploy type | `Migrate` |
| Backup type | logical |
| Update started | `2026-05-16 06:30:37` |
| Update ended | `2026-05-16 06:33:20` |
| Post-update site state | Active on `bench-39776-000015-f94v`, no update available |
| Cache clear | `26es8svcaq`, `Success` |

Live route checks after update:

- `https://locallytwisted.v.frappe.cloud/` returned HTTP 200 with homepage title
  `Locally Twisted - Utah Balloon Event Decor & Installations`.
- `https://locallytwisted.v.frappe.cloud/#login` returned HTTP 200 with the
  homepage title, not the login page.
- `https://locallytwisted.v.frappe.cloud/contact` returned HTTP 200 with title
  `Free Event Quote - Locally Twisted`.
- `https://locallytwisted.v.frappe.cloud/login` returned HTTP 200 with title
  `Sign In | Locally Twisted`.

## Live Smoke Receipt

GL accepted the live smoke after seeing the site. The smoke intentionally sent
to the company email address and used contact name `smoke test from cameron`,
which put the required phrase into the owner subject line:
`New website inquiry from smoke test from cameron`.

Backend evidence:

- Lead: `CRM-LEAD-2026-00013`.
- Five private Lead `File` rows were attached.
- Five `custom_inspiration_photos` child rows existed on the Lead.
- Owner Email Queue: `683s86r04b`, status `Sent`, recipient
  `locallytwisted@gmail.com`, attachment refs `5`.
- Customer Email Queue: `683suhfaa9`, status `Sent`, attachment refs `0`.
- Uploaded filenames:
  - `img-9111.jpeg`
  - `baby-shower-garland.png`
  - `birthday-deliveries--extra-02.webp`
  - `basketball-arch.png`
  - `contact-hero.png`

This proves the reported business-owner failure is fixed on live: customer
photos are no longer only generic private Files; they cascade into CRM photo
rows and owner-only queued email attachment refs.

## Staging Repair Receipt

GL reported `https://locallytwisted-staging.frappe.cloud/#login` as "live
broken." That URL was staging, not live.

Verified staging state before repair:

- staging `/` and `/#login` rendered the Frappe Sign In surface;
- staging `/home` and `/contact` were public;
- `Website Settings.home_page` was `null`;
- `app_name`, `app_logo`, `brand_html`, and `favicon` were blank/default.

Repair applied to staging Website Settings only:

- `home_page = home`
- `app_name = Locally Twisted`
- `app_logo = /assets/locally_twisted/icons/lt-logo.png`
- `brand_html = <img src="/assets/locally_twisted/icons/lt-logo.png?v=20260429-2" alt="Locally Twisted" class="lt-logo">`
- `favicon = /assets/locally_twisted/icons/lt-favicon.png?v=20260508-red-dog-1`
- `website_theme = Standard`

Frappe Cloud staging cache clear job `fb85o6ncdh` succeeded. After repair,
staging `/`, `/#login`, and `/contact` returned the expected public surfaces.

## Dirty Scope Audit

No current uncommitted dirty working-tree files were mixed into the deployed
release commits.

Release-scope warning: the target app mirror commit still included already
committed app-mirror changes beyond the final two-file source commit. That is
not dirty-file contamination, but it is release-scope drift if the controller
only reviews `git show HEAD`.

Specific local dirty overlaps that were not deployed by `631f9a8` / `b4b3bf8`:

- `apps/locally_twisted/locally_twisted/hooks.py` local dirty cache-busted
  `lt-product-setup-runtime.js?v=20260515-generic-1`.
- `apps/locally_twisted/locally_twisted/patches.txt` local dirty added
  `rename_reflex_champagne_color_20260515`.

Future release review must compare the previous live app hash to the target app
mirror commit, not only the last commit or current dirty status. Capability
receipt:
`capabilities/failures/frappe-cloud-app-mirror-release-scope-drift.md`.

## Verification Boundaries

Verified on live:

- site update/migrate succeeded;
- route surfaces rendered expected public pages;
- form happy path created a Lead;
- photo upload path stored private Files and CRM photo rows;
- owner email queued with attachment refs;
- customer confirmation queued without photo attachments.

Not verified by the 2026-05-16 live smoke:

- dedicated live bot-token rejection fixtures;
- dedicated live sales-solicitation suppression fixture;
- checkout, Stripe, cart, product setup, or ecommerce exposure;
- Cloudflare DNS/cache changes, because this smoke targeted the Frappe Cloud
  host.

## Next Safe Step

Do not reopen checkout from this release. Ecommerce and Stripe remain separate
gates. If another public form release is needed, rerun the dedicated live form
fixtures and document whether the run used cleanup verifier mode or an
intentional real business-email smoke.

## Cross-links

- `workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`
- `workstreams/inquiry-form-spam-sales-filter-2026-05-15.md`
- `workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`
- `LT-LAUNCH-RUNBOOK.md`
- `CODING-HANDOFF.md`
- `capabilities/recipes/erpnext-inquiry-photo-delivery-contract.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/failures/frappe-cloud-app-mirror-release-scope-drift.md`
- `capabilities/failures/frappe-cloud-staging-website-settings-drift.md`
