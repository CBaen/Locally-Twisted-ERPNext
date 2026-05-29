# Staging Checkout Product Diversity - Item 3 Scope - 2026-05-29

Status: scoped for Guiding Light review. No staging/provider/live change has
been authorized by this scope.

## Human Outcome

Item 3 should prove that staging checkout handles different product types like
a real customer would expect:

- pickup-eligible products can still be picked up;
- delivery-only products require delivery handling;
- mixed carts stay mixed instead of forcing the whole order into one method;
- configured variants and the approved foil-number add-on preserve customer
  choices through cart, checkout, order, receipt, and internal notification;
- quote-first products cannot be forced into paid checkout.

This item is the product-diversity checkout matrix. It is not a live launch
approval, not a catalog import, and not a new staging push.

## Source Baseline

- Source branch for this scope: `codex/item3-product-diversity-scope`
- Baseline source tip: `7992804 Record item 2 approval`
- Item 2 code baseline: `82f1d56 Fix checkout preview total rounding`
- Staging app mirror already used for item 2 proof:
  `35ac2b1 Trigger checkout penny staging deploy press-deploy-bench-40102`

Do not push another app mirror, Frappe Cloud Pull, migrate, cache clear, DNS
change, live Stripe change, Search Console change, or production data mutation
from item 3 scoping. If item 3 finds a code issue, fix it in source and hold it
for the later combined staging push unless Guiding Light explicitly reopens
staging deployment.

## Recommended Item 3 Matrix

| Case | Customer Path | Product / Item | Fulfillment Expectation | Paid Path |
|---|---|---|---|---|
| Pickup single-SKU | Direct cart/checkout | `mothers-day-bouquet` | Pickup allowed; no delivery fee line | Only if needed |
| Configured bouquet, no add-on | Product page to cart to checkout | `/shop-items/bouquets/encanto-bouquet`, `encanto-bouquet-SMA` | Pickup allowed; selected size preserved | Existing staging proof exists, rerun browser/API |
| Configured bouquet with add-on | Product page to cart to checkout | `/shop-items/bouquets/unicorn-bouquet`, `unicorn-bouquet-MED` plus `foil_number` | Add-on line and selected digits preserved | Existing paid item-2 proof exists |
| Delivery-only garland | Product page to cart to checkout | `/shop-items/garlands/graduation-grab-n-go`, `graduation-grab-n-go-BYU` | Delivery required; pickup copy not shown as full-order promise | Candidate paid proof |
| Delivery-only arch | Product page probe | `/shop-items/arches/classic-organic-arch` | Delivery-only copy and checkout eligibility stay coherent | Browser/API proof first |
| Delivery-only balloon drop | Product page probe | `/shop-items/balloon-drops/balloon-drop` | Delivery-only copy and checkout eligibility stay coherent | Browser/API proof first |
| Mixed cart | Cart/checkout with pickup + delivery-only items | `mothers-day-bouquet` plus `graduation-grab-n-go-BYU` | Sales Order method `Mixed`; pickup line stays Pickup; delivery-only line stays Delivery; one delivery fee | Existing item-2 paid order can be inspected first |
| Quote-first guard | Product page/direct cart attempt | `/shop-items/columns/7-butterfly-column`, `7-butterfly-column-REF` | No paid checkout bypass; customer-safe quote-needed message | No payment |

## Proof Order

1. Confirm staging is still on the known item-2 app mirror state before testing.
2. Run the hosted browser checkout smoke against staging:

```powershell
$env:LT_BASE_URL='https://locallytwisted-staging.frappe.cloud'
npm run test:checkout-experience
```

3. Run source/local contracts before trusting the matrix:

```powershell
python scripts\verify\cart_checkout_contract.py
python scripts\verify\checkout_fulfillment_contract.py
python scripts\verify\stripe_amount_parity_contract.py
```

4. Inspect existing paid staging orders before creating new ones:
   - `SAL-ORD-2026-00030`: mixed cart, `$176.18`.
   - `SAL-ORD-2026-00031`: foil-number add-on, `$116.00`.
5. Only create new Stripe test orders if the matrix cannot be proven from
   existing paid orders plus browser/API evidence.

## Pass Conditions

Item 3 passes only if:

- product-page copy, cart state, checkout summary, Stripe amount, thank-you
  page, customer receipt, and internal notification agree for any paid case;
- line-level fulfillment is correct on ERPNext Sales Orders;
- delivery fees are present once when required and absent when not required;
- preview totals match final order totals to the cent;
- supported add-on details are preserved and unsupported/review-only add-ons
  fail loudly;
- quote-first products cannot be pushed into paid checkout;
- any new test order has matching customer and internal email information, or
  the mismatch is recorded as a blocker.

## Stop Conditions

Stop item 3 before moving on if any of these happen:

- a customer can pay for a quote-first product;
- checkout shows pickup success while a delivery-only line still needs delivery;
- a mixed cart loses either pickup or delivery details;
- preview, Stripe, thank-you, receipt, or internal notification differs by even
  one cent;
- selected variant/add-on details disappear from cart, checkout, Sales Order,
  receipt, or internal notification;
- staging returns provider/secret/decryption errors again;
- a new failure would require a staging/app mirror/provider push.

## Boundaries

- No live checkout approval.
- No production payment, DNS, Search Console, or live Stripe work.
- No product data mutation outside verifier-safe or explicitly scoped staging
  customer-path tests.
- No broad catalog launch claim.
- No large staging push from this item unless Guiding Light explicitly approves
  reopening deployment.

## Next Safe Action

After Guiding Light accepts this scope, item 3 should begin with read-only or
test-mode staging verification of the matrix above. The first execution pass
should prefer existing item-2 paid orders plus browser/API proof before creating
new Stripe test orders.
