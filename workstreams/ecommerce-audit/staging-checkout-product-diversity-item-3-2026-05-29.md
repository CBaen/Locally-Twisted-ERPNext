# Staging Checkout Product Diversity - Item 3 Scope And Proof - 2026-05-29

Status: execution proof is ready for Guiding Light review on 2026-05-29. No
staging/provider/live change has been authorized by this item.

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

## Human Approval

Guiding Light approved this item 3 scope on 2026-05-29. Approval means the
product-diversity matrix below is the next checkout audit slice. It does not
mean item 3 is complete, and it does not authorize deployment or provider
changes.

Guiding Light later confirmed the item-3 order email did show up, but not in
the main Gmail folder. The proof below therefore treats email delivery as
working and mailbox placement as a Gmail organization/filtering concern, not a
checkout or receipt-generation failure.

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

## Execution Evidence - 2026-05-29

### Hosted staging checkout proof

- Hosted staging browser smoke passed: `npm run test:checkout-experience`
  against `https://locallytwisted-staging.frappe.cloud` passed `4/4`.
- Delivery-only product pages returned `200` and stayed quote/delivery-only
  coherent for Classic Organic Arch, Balloon Drop, and 7' Butterfly Column.
- Quote-first bypass was blocked for `7-butterfly-column-REF`; the cart API
  returned no item and reported `quote_required`.
- Pickup single-SKU preview passed for `mothers-day-bouquet`: subtotal `$65.00`,
  delivery fee `$0.00`, tax `$4.84`, total `$69.84`.
- Mixed pickup plus delivery-only preview passed for `mothers-day-bouquet` plus
  `graduation-grab-n-go-BYU`: subtotal `$150.00`, delivery fee `$15.00`, tax
  `$11.18`, total `$176.18`.
- Standalone delivery-only preview passed for `graduation-grab-n-go-BYU`:
  subtotal `$85.00`, delivery fee `$15.00`, tax `$6.33`, total `$106.33`.

### Paid staging order proof

- Existing mixed-cart order `SAL-ORD-2026-00030` still rendered a valid
  thank-you page for `$176.18` with Mother's Day Bouquet, Graduation Grab n
  Go-BYU, and Standard Delivery.
- Existing foil-number add-on order `SAL-ORD-2026-00031` still rendered a valid
  thank-you page for `$116.00` with Unicorn Bouquet-MED, Foil number: 12, and
  Standard Delivery.
- New order `SAL-ORD-2026-00033` proved payment and thank-you rendering for a
  standalone delivery-only cart at `$106.33`, but the checkout email used
  `example.invalid`; do not count it as customer receipt delivery proof.
- Corrected new order `SAL-ORD-2026-00034` proved standalone delivery-only paid
  checkout with Stripe test mode, thank-you page, customer receipt, welcome
  email, and internal notification at `$106.33`.

### Gmail proof

- Search used `in:anywhere`, not only the main inbox, because some staging
  purchase messages had been moved or labeled.
- `SAL-ORD-2026-00034` was found in Gmail with both the internal paid-order
  notice and the customer receipt. The customer receipt was addressed to
  `locallytwisted+item3-delivery-1780037320165@gmail.com`; the internal notice
  was addressed to `locallytwisted@gmail.com`.
- Searching the corrected item-3 customer email also found the first-order
  welcome email.
- Earlier moved proofs `SAL-ORD-2026-00030` and `SAL-ORD-2026-00031` were found
  by all-mail search. They are under `_NEW_WEBSITE/Duplicate Inquiry Request`
  and `SENT`, not the main inbox.
- The email contents agree with the paid order totals and line items:
  `SAL-ORD-2026-00030` `$176.18`, `SAL-ORD-2026-00031` `$116.00`, and
  `SAL-ORD-2026-00034` `$106.33`.

## Current Decision

Item 3 is agent-approved for Guiding Light review after staging test-mode
proof. It is not live approval, not staging deployment approval, and not
permission to push the app mirror or run a new Frappe Cloud update. Guiding
Light approval is still needed before this item is marked complete and the next
checkout-review item starts.
