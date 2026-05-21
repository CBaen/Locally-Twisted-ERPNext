# Lane 03 - Guest Commerce Contract

## Decision Question

What is the native Frappe/Webshop contract for anonymous product info, cart party/customer resolution, price-list choice, category/product cards, and variant selector calls, and are Locally Twisted's overrides supportable?

Decision: support the narrow hook-based overrides as a guarded bridge, but quarantine and replace the two process-global monkey patches before launch proof. The current behavior is explainable and testable; it is not clean enough to treat as native-safe.

## Primary Sources

- Webshop `WebsiteItem.set_shopping_cart_data()` calls `get_product_info_for_website(..., skip_quotation_creation=True)`: https://github.com/frappe/webshop/blob/version-15/webshop/webshop/doctype/website_item/website_item.py#L340-L346
- Webshop product info is guest-allowed, uses Webshop Settings, asks `_set_price_list()`, and still calls `get_party()` while serving prices: https://github.com/frappe/webshop/blob/version-15/webshop/webshop/shopping_cart/product_info.py#L17-L45
- Webshop `_set_price_list()` uses Customer default price list before the Webshop Settings price list; without a quotation it calls `get_party()`: https://github.com/frappe/webshop/blob/version-15/webshop/webshop/shopping_cart/cart.py#L485-L505
- Webshop `get_party()` resolves/creates Customer, Contact, Portal User, and Dynamic Link style customer plumbing for the current website user: https://github.com/frappe/webshop/blob/version-15/webshop/webshop/shopping_cart/cart.py#L537-L613
- Webshop variant selector calculates valid options and variant price info, and its price path calls `_set_price_list(cart_settings, None)`: https://github.com/frappe/webshop/blob/version-15/webshop/webshop/variant_selector/utils.py#L106-L247
- Webshop product listing API returns `items`, `filters`, `settings`, and immediate child item groups; listing display details call product info for each item: https://github.com/frappe/webshop/blob/version-15/webshop/webshop/api.py#L16-L82 and https://github.com/frappe/webshop/blob/version-15/webshop/webshop/product_data_engine/query.py#L223-L232
- ERPNext price lookup accepts optional party context and falls back to template prices for variants if no variant price exists: https://github.com/frappe/erpnext/blob/version-15/erpnext/utilities/product.py#L10-L81
- ERPNext default price-list logic uses Customer/default customer-group price lists: https://github.com/frappe/erpnext/blob/version-15/erpnext/accounts/party.py#L356-L381
- Frappe docs support `override_whitelisted_methods` and `override_doctype_class`, but warn class overrides replace core behavior and hook conflicts are last-installed-app wins: https://docs.frappe.io/framework/user/en/python-api/hooks
- ERPNext docs tie Webshop shopping cart to Company, Price List, Default Customer Group, and Enable Checkout; variants require choosing a concrete variant before carting: https://docs.frappe.io/erpnext/e_commerce_settings and https://docs.frappe.io/erpnext/shopping-cart
- Frappe docs define `Guest` as allocated to unauthenticated users: https://docs.frappe.io/framework/user/en/basics/users-and-permissions

## Local Evidence

- Installed local source matches this lane's version target enough to use upstream `version-15` as the primary code reference: Docker reported `frappe 15.106.0`, `erpnext 15.105.0`, `webshop 0.0.1`, and installed Webshop source contains the same probed methods.
- [apps/locally_twisted/locally_twisted/overrides/website_item.py](../../../apps/locally_twisted/locally_twisted/overrides/website_item.py) subclasses Webshop `WebsiteItem`, replaces only `set_shopping_cart_data()`, and uses a guest-safe product info function that avoids `get_party()` for `Guest` while still using `cart_settings.price_list`.
- [apps/locally_twisted/locally_twisted/hooks.py](../../../apps/locally_twisted/locally_twisted/hooks.py) wires supported Frappe hooks for `get_product_filter_data`, product info, variant selector, and `Website Item` class override at lines 159-167.
- [apps/locally_twisted/locally_twisted/api/product_listing.py](../../../apps/locally_twisted/locally_twisted/api/product_listing.py) uses a supported whitelisted-method wrapper, but also mutates `webshop.webshop.product_data_engine.query.get_product_info_for_website` at import time.
- [apps/locally_twisted/locally_twisted/api/variant_selector.py](../../../apps/locally_twisted/locally_twisted/api/variant_selector.py) uses a supported whitelisted-method wrapper, but mutates `variant_utils._set_price_list` at call time before delegating to upstream.
- [apps/locally_twisted/locally_twisted/api/cart.py](../../../apps/locally_twisted/locally_twisted/api/cart.py) is an LT-owned guest cart adapter, not native Webshop cart. It resolves variant Item rows through the parent Website Item, blocks templates, blocks quote-first products, uses `Standard Selling`, and returns loud `missing` reasons instead of pretending cart success.
- Guest infrastructure is now treated as platform plumbing, not fake customer data. Hooks protect `User`, `Customer`, `Contact`, `Has Role`, `Portal User`, `Dynamic Link`, `Contact Email`, and `Contact Phone` rows in [hooks.py](../../../apps/locally_twisted/locally_twisted/hooks.py) lines 434-473, and [apps/locally_twisted/locally_twisted/verify/webshop_guest_party_contract.py](../../../apps/locally_twisted/locally_twisted/verify/webshop_guest_party_contract.py) verifies that shape.
- Category-card shape has already shifted: `/shop-by-category` redirects to `/shop`, `/shop` uses direct Website Item / Item Price SQL, and Item Group pages still use Webshop's listing JS plus an LT template patch. See [apps/locally_twisted/locally_twisted/www/shop.py](../../../apps/locally_twisted/locally_twisted/www/shop.py), [apps/locally_twisted/locally_twisted/www/shop-by-category/index.py](../../../apps/locally_twisted/locally_twisted/www/shop-by-category/index.py), and [apps/locally_twisted/locally_twisted/templates/generators/item_group.html](../../../apps/locally_twisted/locally_twisted/templates/generators/item_group.html).

## Findings

1. Native Webshop is not read-only for anonymous commerce by default. Product, variant, and cart paths can reach `get_party()`, and `get_party()` can create or repair Customer/Contact/Portal User records. That explains the Guest cleanup regression and means "zero customers" is not a safe local Webshop state.
2. Public product info can safely use `cart_settings.price_list` for `Guest` if LT does not want Guest-specific pricing. ERPNext `get_price()` accepts `party=None`, and LT still passes customer group/company/price list.
3. The `Website Item` class override is supportable because it subclasses upstream and changes one method. The risk is hook resolution: if another app overrides `Website Item` later or `locally_twisted` is not last, LT loses the override.
4. `override_whitelisted_methods` is a supportable Frappe hook for the public RPC endpoints. It does not automatically change internal module imports, which is why the current code added monkey patches.
5. The two monkey patches are the weak part:
   - `product_listing.py` changes an upstream module global at import time.
   - `variant_selector.py` changes an upstream private helper at request time.
   Both are hard to reason about under workers, upgrades, and app reloads.
6. LT's custom localStorage cart is not native Webshop cart. That is acceptable only if tests keep proving the LT adapter resolves variants, quote-first products, line keys, add-ons, prices, and checkout failure states. Do not describe it as "Webshop owns cart" without the adapter caveat.
7. Retired category cards should stay eliminated. The supportable path is `/shop` plus Item Group category pages, with tests against product counts/cards and no revival of the thin `/shop-by-category` card index.

## Resolution Recommendation

- Support: keep `LocallyTwistedWebsiteItem` and `get_guest_safe_product_info_for_website` for v15, with an explicit hook-order guard and source-drift test.
- Support: keep the `override_whitelisted_methods` wrappers for product listing and variant selector as the public endpoint seam.
- Quarantine: keep the current monkey patches only as a short-term bridge. They need a named guard in launch verification and should not be expanded.
- Eliminate: remove import-time and call-time mutation of upstream Webshop module globals.
- Rebuild: replace the variant selector wrapper with an LT-owned implementation or adapter that calls upstream public helpers but computes price with LT's safe price-list function without touching `variant_utils._set_price_list`.
- Refresh: treat `/shop-by-category` as retired and verify `/shop` + Item Group pages instead of trying to repair old category-card counts.
- Required standing rule: preserve and verify the Guest party infrastructure even if product-info overrides no longer need it, because native cart/address/order/future Webshop paths still use `get_party()`.

## Required Tests

- Read-only/source contract: verify `locally_twisted` is installed last; verify Frappe hooks contain the expected method/class overrides; verify upstream Webshop source still has the methods/signatures this adapter depends on.
- Guest infrastructure guard: `python scripts/verify/webshop_guest_party_contract.py` after any cleanup or commerce change. This includes rollback probes, so run it only when destructive-probe testing is allowed for the environment.
- Guest product/listing/variant proof: anonymous product page and Item Group page must load without same-origin 400/500s; variant selection must return exact-match `product_info`; listing/card API must return prices/starting prices for representative simple and variant products.
- Cart/checkout adapter proof: `python scripts/verify/cart_checkout_contract.py`.
- Price proof: `python scripts/verify/product_variant_price_contract.py`, `python scripts/verify/product_price_modifier_contract.py`, and `npx playwright test scripts/verify/product_price_display.spec.js --workers=1`.
- Launch bundle proof: the website launch verifier already includes shop smoke, price, variant media, and checkout experience steps in [scripts/verify/website_launch_verify.py](../../../scripts/verify/website_launch_verify.py) lines 165-178. Before running in an unpaused state, confirm no step creates orders/quotes unless the lane explicitly allows that.

## Remaining Gaps

- I did not mutate the DB or run record-creating tests for this lane.
- I did not prove staging/live; this is local-source and primary-source research only.
- The exact replacement design for the monkey patches still needs an implementation plan and tests.
- `smoke_shop.py` needs a quick safety read before use as a "no record creation" proof in an unpaused commerce mode.
- Future Frappe v16 work should revisit `extend_doctype_class`; current v15 support is acceptable only with the hook-order guard.
