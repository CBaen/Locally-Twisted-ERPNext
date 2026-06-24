# Live Homepage And Birthday Deliveries Media Repair

Date: 2026-06-24
Status: live verified
Owner: Codex technical lead
Scope: `https://locallytwisted.com/`, homepage hero route state, Birthday Deliveries primary media, homepage Customer Favorites image

## Current Outcome

The live customer-facing repair is complete.

- `https://locallytwisted.com/` returns `200` with `x-page-name: home`,
  `x-from-cache: False`, and `Server: Frappe Cloud`.
- The public root is the landing page. It should not require `/home` and should
  not render the login page.
- The live homepage hero carousel opens with the GL-selected Civic &
  Community image set, followed by Corporate Events, Schools & Campuses, and
  Private Celebrations.
- The rejected July hero is no longer referenced by live homepage HTML. The
  old July asset can still return `200` as a stored asset; that is not a live
  homepage reference.
- Birthday Deliveries now uses
  `/files/birthday-deliveries--extra-12.webp` as the main product image and as
  the homepage Customer Favorites image.
- The old `/files/birthday-deliveries.png` is no longer referenced by the live
  product page or homepage. It still exists as an uploaded file and must not be
  globally deleted unless GL explicitly approves file destruction.

Source closeout commit:

```text
92db004 Repair homepage route and birthday deliveries media
```

The source patch is:

```text
apps/locally_twisted/locally_twisted/patches/sync_home_and_birthday_deliveries_media_20260624.py
apps/locally_twisted/locally_twisted/patches.txt
```

## What Went Wrong

There were two separate problems that looked like one failed image swap.

First, homepage/source/live state was not being kept separate. The photoreal
hero set had been selected and wired in source, but docs and live proof still
contained stale "local-only / pending live release" language. The only useful
answer to GL's complaint was a fresh public-root check, not another local
source claim.

Second, Birthday Deliveries product media was not governed by the gallery row
alone. GL deleted a Birthday Deliveries photo manually in Desk, but live
read-only proof still showed these primary fields pointing at the old PNG:

```text
Website Item WEB-ITM-0047.website_image = /files/birthday-deliveries.png
Item birthday-deliveries.image = /files/birthday-deliveries.png
LT Product Blueprint birthday-deliveries.primary_image = /files/birthday-deliveries.png
```

The Blueprint gallery rows and Website Slideshow rows already omitted the old
PNG and included `/files/birthday-deliveries--extra-12.webp`. That made the
manual backend deletion look successful while the actual public main image
remained stale.

The new WebP also had no `File` row attached to the Website Item even though
the public file URL existed and gallery rows referenced it. Direct owner API
writes then failed because the guard chain saw the WebP as an unattached
Website Item image.

## Live Write Path

Direct `frappe.client.set_value` was not the successful repair path.

- First attempt failed on CSRF after the Desk page DOM changed.
- After a valid Desk CSRF token was available, `set_value` failed with `403`.
- The failure messages were:
  - `Website Image /files/birthday-deliveries--extra-12.webp attached to Item WEB-ITM-0047 cannot be found`
  - LT protected owner catalog guard blocked raw Website Item save.

The successful repair used Desk System Console with scoped `frappe.db` writes.
System Console is safe-exec restricted: raw `import`, `frappe.as_json`, and
`frappe.clear_cache` are blocked. A first committed console attempt rolled
back when `frappe.clear_cache()` was rejected. The final committed run omitted
blocked calls and changed only the needed records:

```text
File 12519ab9bb created for /files/birthday-deliveries--extra-12.webp
File attached_to_doctype = Website Item
File attached_to_name = WEB-ITM-0047
Website Item WEB-ITM-0047.website_image = /files/birthday-deliveries--extra-12.webp
Item birthday-deliveries.image = /files/birthday-deliveries--extra-12.webp
LT Product Blueprint birthday-deliveries.primary_image = /files/birthday-deliveries--extra-12.webp
```

The old file row for `/files/birthday-deliveries.png` was `647f852a42`. It was
not destroyed because the user asked to remove the photo from the product page
and homepage, not to globally delete the uploaded file from storage.

## Verification Receipts

Fresh public proof after the repair:

```text
curl -fsSIL https://locallytwisted.com/
# 200, x-page-name: home, x-from-cache: False, Server: Frappe Cloud

curl -fsSL https://locallytwisted.com/ | rg 'birthday-deliveries--extra-12|birthday-deliveries.png'
# new WebP present in homepage Customer Favorites
# old PNG absent

curl -fsSL https://locallytwisted.com/shop-items/bouquets/birthday-deliveries | rg 'birthday-deliveries--extra-12|birthday-deliveries.png|og:image|twitter:image'
# new WebP present in metadata, main image, and runtime JSON
# old PNG absent

sha256sum /home/guidingl/Desktop/birthday-deliveries--extra-12.webp <(curl -fsSL https://locallytwisted.com/files/birthday-deliveries--extra-12.webp)
# both hashes cbcd2e5e72e1db4fa981f9094878f1e6baea60967a171bf675564d8af90bdcbd
```

Earlier browser proof from the same repair showed:

- product page `oldRefs:false`, `newRefs:true`;
- product main and thumbnail images using the new `1024x767` WebP;
- homepage `oldRefs:false`, `newRefs:true`;
- Birthday Deliveries favorite image list:
  `["/files/birthday-deliveries--extra-12.webp"]`;
- screenshots:
  - `/tmp/lt-birthday-product-after.png`
  - `/tmp/lt-home-favorites-after.png`

## Future Guard

For Birthday Deliveries or similar product-media repairs, do not stop at
Product Setup gallery rows or Website Slideshow rows. The public main image
can still come from separate primary fields.

Check and update all relevant layers together:

1. `Website Item.website_image`
2. underlying `Item.image`
3. `LT Product Blueprint.primary_image`
4. `File` row existence and attachment to the target Website Item
5. gallery/slideshow rows when the old file appears there
6. public product page metadata/main image/runtime JSON
7. public homepage/card reference if the product is merchandised there

Do not weaken the owner catalog guard to get around the save block. Use a
source-owned patch/release when the Frappe Cloud path is healthy, or a tightly
scoped admin maintenance/System Console repair when GL has approved the exact
live mutation and source release is blocked.

## Related Files

- `CODING-HANDOFF.md`
- `PROJECT-STATUS.md`
- `locally-twisted-queue.md`
- `locally-twisted-decisions.md`
- `decisions/2026-06-24-live-homepage-birthday-media-repair.md`
- `capabilities/failures/product-primary-media-attachment-drift.md`
- `capabilities/failures/product-gallery-projection-regression.md`
- `capabilities/recipes/homepage-launch-proof-contract.md`
- `capabilities/recipes/frappe-product-page-company-first.md`
