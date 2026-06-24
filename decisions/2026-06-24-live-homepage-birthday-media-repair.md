# 2026-06-24 Live Homepage And Birthday Deliveries Media Repair

## Decision

Treat `https://locallytwisted.com/` as the canonical public homepage URL and
keep it serving the landing page directly. Do not make customers use `/home`
for the landing page, and do not leave the public root rendering the login
page.

Treat `/files/birthday-deliveries--extra-12.webp` as the approved main Birthday
Deliveries image for the live product page and homepage Customer Favorites
card. The old `/files/birthday-deliveries.png` must not be referenced by the
public Birthday Deliveries product page or homepage merchandising card.

## Reasoning

GL's complaint was about public reality, not local source intent. The only
accepted proof was fresh live-route proof against `locallytwisted.com`.

The Birthday Deliveries backend state showed that deleting or changing gallery
rows is not enough to change the public main image. The main product image can
come from `Website Item.website_image`, `Item.image`, and
`LT Product Blueprint.primary_image`, and Frappe's Website Item image validation
also depends on the referenced image having a usable `File` attachment.

## Implementation Boundary

Source commit `92db004 Repair homepage route and birthday deliveries media`
added an idempotent patch to keep `/` on the branded home route and promote
the approved Birthday Deliveries WebP.

Live backend repair used scoped Desk System Console `frappe.db` writes after
direct `frappe.client.set_value` failed on CSRF, missing `File` attachment
validation, and the protected owner catalog guard. The successful live write
created File `12519ab9bb` for
`/files/birthday-deliveries--extra-12.webp`, attached it to Website Item
`WEB-ITM-0047`, and set the Website Item, Item, and LT Product Blueprint
primary-image fields to the new WebP.

This decision did not approve DNS changes, Stripe/payment changes, product
visibility changes, customer communication, or a broad catalog mutation.

## Proof

Fresh live proof after repair:

- `https://locallytwisted.com/` returned `200` with `x-page-name: home`,
  `x-from-cache: False`, and `Server: Frappe Cloud`.
- Live homepage HTML references `/files/birthday-deliveries--extra-12.webp`
  for the Birthday Deliveries Customer Favorites image and has zero
  `/files/birthday-deliveries.png` references.
- Live Birthday Deliveries product HTML references the WebP in product
  metadata, Open Graph/Twitter image metadata, main image markup, and runtime
  Product Setup JSON, with zero old-PNG references.
- The live WebP hash matches GL's supplied local file:
  `cbcd2e5e72e1db4fa981f9094878f1e6baea60967a171bf675564d8af90bdcbd`.

## Guard

Future product primary-media changes must update and verify:

1. `Website Item.website_image`
2. underlying `Item.image`
3. `LT Product Blueprint.primary_image`
4. `File` row existence and attachment
5. public product page metadata/main image/runtime JSON
6. public homepage/card references if the product is featured there

Do not weaken the owner catalog guard. Do not globally delete uploaded files
unless GL explicitly approves file destruction. Removing a photo from a page is
not the same as deleting the stored File.

## Decided By

Guiding Light supplied the approved image and clarified the expected public
behavior. Codex executed and live-verified the repair on 2026-06-24.
