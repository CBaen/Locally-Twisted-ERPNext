---
id: erpnext-webshop-guest-party-contract
name: ERPNext Webshop Guest Party Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Webshop anonymous shopping, public pricing, and local fake-data cleanup
currently_true: unknown
verification_level: 2
last_verified: 2026-05-21
evidence_quality: direct
successful_uses: 2
failed_uses: 1
regressions: 1
depends_on:
  - fail-loud-operating-law
  - frappe-public-storefront-security
  - erpnext-ecommerce-receiving-architecture
used_by:
  - fake-data-cleanup
  - shop
  - public-network-verification
tags:
  - Locally Twisted
  - ERPNext
  - Frappe
  - Webshop
  - Guest
  - cleanup
  - pricing
watch_status: probation
---

# ERPNext Webshop Guest Party Contract

Use this before deleting local data, changing Webshop Settings, changing public
product pages, or giving another agent a cleanup task that touches `Customer`,
`Contact`, `Portal User`, or public ecommerce records.

## Plain-English Model

`Guest` is not a normal client record and not a marketing login. It is the
anonymous public visitor identity that Frappe and Webshop use when someone is
not logged in.

Frappe's role docs say `Guest` is automatically allocated to unauthenticated
users. ERPNext's E Commerce Settings docs say Webshop uses settings such as
`Show Price`, `Price List`, `Default Customer Group`, checkout, and guest price
visibility for public shopping. In LT's local ERPNext install, those framework
ideas connect through data-backed records:

- `User: Guest`
- `Customer: Guest`
- `Portal User: Guest -> Customer Guest`
- `Contact: Guest-Guest`
- `Dynamic Link: Guest-Guest -> Customer Guest`

That data gives Webshop a safe anonymous customer context for public product
pricing. It does not mean the public has Desk/admin power.

## Why This Matters

Stock Webshop code calls `get_party()` for anonymous price and cart work. In
the installed Webshop app:

- `shopping_cart/cart.py` `_set_price_list()` calls `get_party().get("name")`
  when there is no cart quotation.
- `shopping_cart/product_info.py` calls `_set_price_list(cart_settings, None)`
  for guest product info when no quotation exists.
- `variant_selector/utils.py` calls `_set_price_list()` when an exact variant
  match needs product price info.
- `product_data_engine/query.py` asks for product info while building listing
  display details.

When the Guest party chain is missing, public product pages, category/listing
pages, and Webshop AJAX calls can return 400/500 instead of prices/options.

LT now also has a guest-safe overlay:

- `locally_twisted.overrides.website_item.get_guest_safe_product_info_for_website`
- `locally_twisted.api.variant_selector.get_next_attribute_and_values`
- `LocallyTwistedWebsiteItem`

That overlay reduces reliance on stock Webshop behavior for product info and
variant selection. It is a mitigation, not permission to delete Guest party
records. Cart, checkout, address, order, and future native Webshop paths can
still use `get_party()`.

## Required Preserved Records

During fake-data cleanup, preserve these as infrastructure:

| Doctype | Required record | Why |
|---|---|---|
| `User` | `Guest` | Frappe anonymous session user; must stay `Website User` with only `Guest` role |
| `Customer` | `Guest` | Anonymous customer context for Webshop price/customer-group lookup |
| `Portal User` | `Guest -> Customer Guest` | Lets Webshop resolve `Guest` to the anonymous Customer |
| `Contact` | `Guest-Guest` | Anonymous Contact shell paired to the Guest customer |
| `Dynamic Link` | `Guest-Guest -> Customer Guest` | Connects the anonymous Contact to the anonymous Customer |

Do not attach real customer details, real email addresses, real orders, invoices,
payment records, or staff roles to these records.

## Runtime Protection

The Guest party chain is protected in source, not only in notes:

- `apps/locally_twisted/locally_twisted/webshop_guest_party_guard.py`
  validates the required `Guest` User, Customer, Portal User, Contact, and
  Dynamic Link shape.
- `apps/locally_twisted/locally_twisted/hooks.py` registers that guard through
  Frappe `doc_events` on save/change/delete hooks for the parent and child
  records.
- The verifier intentionally tries to delete, disable, or mutate the protected
  records inside rollback-safe probes and requires every probe to be blocked.

This protects normal Frappe/ERPNext Desk actions, API saves, and
`frappe.delete_doc()` paths. It does not protect direct SQL run outside Frappe's
document lifecycle, so backup/cleanup scripts must still run the verifier before
and after broad database work.

## What Can Be Deleted

Local fake/demo/smoke data can still be deleted when scoped and backed up:

- `Lead`, `Opportunity`, `Quotation`, `Sales Order`, `Sales Invoice`, `Payment Request`
- verifier/demo `User` accounts
- fake `Customer` and `Contact` records other than the Guest infrastructure
- `Communication`, `Email Queue`, `Activity Log`, `Error Log`, route/history rows
- marker-owned custom LT demo records

The safe summary is: delete fake operational data, not platform identity
plumbing.

## Blast Radius

If the Guest party chain is deleted or partly broken:

- public product detail pages can fail when variant pricing is requested;
- category and product listing pages can fail while adding display prices;
- `POST /` Webshop method calls can return 400/500;
- the browser console can show `website.js` POST failures even on pages that
  otherwise look like static content;
- cart, checkout, quote, order, address, and payment-prep paths can hit
  unexpected anonymous party behavior;
- cleanup reports can falsely say all customer/contact data is zero unless they
  distinguish infrastructure records from client data;
- site and asset caches may keep noisy broken behavior until the Frappe website
  cache is cleared after repair.

What this does not prove by itself:

- It does not prove public visitors have Desk access.
- It does not prove marketing reviewers or customers can see private backend
  records.
- It does not prove staging or live is affected unless that environment is
  checked directly.

## Required Guard

Run this after any cleanup, Webshop Settings change, guest checkout change,
product page override change, or broad public-route verification:

```powershell
python scripts/verify/webshop_guest_party_contract.py
npm run test:public-network -- --workers=1
```

The verifier must report `runtime_guard_probes` with every probe blocked. A
plain record-exists check is not enough.

If public product pages or Webshop AJAX broke first, also clear website cache
after repair:

```powershell
python scripts/dev/clear_website_cache.py
```

## Recovery Recipe

1. Stop any broad fake-data cleanup.
2. Confirm the environment is local, staging, or live before touching records.
3. Check `Customer:Guest`, `Portal User:Guest`, `Contact:Guest-Guest`, and the
   Dynamic Link.
4. Restore only the missing Guest infrastructure records.
5. Clear the Frappe website cache.
6. Run `python scripts/verify/webshop_guest_party_contract.py`.
7. Run `npm run test:public-network -- --workers=1`.
8. Update the cleanup workstream so future zero-data reports exclude Guest
   infrastructure from client-data counts.

## Sources

- Official ERPNext E Commerce Settings docs: `Show Price`, `Price List`,
  `Default Customer Group`, checkout, and guest display settings:
  https://docs.frappe.io/erpnext/e_commerce_settings
- Official ERPNext Shopping Cart docs: variants and checkout use E Commerce
  Settings:
  https://docs.frappe.io/erpnext/shopping-cart
- Official ERPNext Price Lists docs: price lists drive Item Prices:
  https://docs.frappe.io/erpnext/price-lists
- Official Frappe Users and Permissions docs: `Guest` is the unauthenticated
  automatic role:
  https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- Official Frappe hook/controller docs: `doc_events` and document lifecycle
  methods such as `validate`, `before_save`, and `on_trash` are the supported
  framework layer for this guard:
  https://docs.frappe.io/framework/v15/user/en/python-api/hooks
  https://docs.frappe.io/framework/user/en/basics/doctypes/controllers

## Evidence

Verified locally on 2026-05-21:

- `User:Guest` exists as enabled `Website User` with only `Guest` role.
- `Customer:Guest`, `Portal User:Guest -> Customer Guest`,
  `Contact:Guest-Guest`, and `Dynamic Link:Guest-Guest -> Customer Guest`
  exist.
- `Webshop Settings` are enabled for public product viewing and public price
  display with `Standard Selling` / `Individual`.
- Guest product-info and variant-selector probes pass for `unicorn-bouquet`.
- Runtime guard probes blocked deletion, disablement, role/Portal User/Dynamic
  Link removal, rename, and fake email attachment attempts against the
  protected Guest records.
- The earlier cleanup failure broke local public pages until Guest
  infrastructure was restored and website cache was cleared.

Staging/live were not changed or verified by this local recipe.
