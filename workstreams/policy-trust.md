# Policy And Trust Workstream

Last updated: 2026-05-06 by Codex.

## Outcome

Make the launch policy/trust surface accurate enough to support customer trust and Stripe readiness without inventing legal or business terms.

Business source of truth: `C:\Users\baenb\projects\locally-twisted-odoo\4-20-25-jeff-cameron\`.

Do not treat current ERPNext policy pages as authoritative until each claim is traced to the Odoo business source, current GL approval, or legal approval.

## Current Stage

Source-trace pass started. Routes load, and GL has supplied business-proxy answers for the main policy-copy blockers. Legal/accounting approval is still separate from business approval.

Checkout now has a verified local commerce-rule contract. Current local behavior: goods are taxable by fulfillment ZIP/city rate; services, face painting, balloon twisting, deposits for those services, and delivery charges are non-taxable; local delivery is `$15`, Park City delivery is `$50`, and out-of-area delivery is available for quote.

Customer-facing documents now use anchored policy lanes. `/terms-of-service` and `/refund-policy` expose event balloon decor, ready-to-order pickup/delivery, face painting/balloon twisting, and corporate invoicing anchors. `locally_twisted.policy_documents` renders reusable code-owned email blocks. Do not add ERPNext Terms and Conditions or Email Template records unless a verified customer-facing invoice path truly requires them; GL wants the build kept as whitelabel/code-owned as possible.

2026-05-06 GL business-proxy answers now captured in copy/source docs:

- Delivery policy stays in Terms/FAQ, not a standalone route.
- Pickup/delivery windows are requested until confirmed.
- If LT cannot deliver/setup because the customer cannot be contacted or access info is wrong, the customer remains responsible.
- Delivered product damage must be reported the same day.
- Ready-to-order products have no returns once prepared, delivered, or picked up.
- Launch expects analytics/ads/tracking plus cart/session storage.
- Privacy contact remains `hi@locallytwisted.com`.
- The children/minors privacy rule is narrow online-data language: adults submit forms/orders; LT does not knowingly collect directly from children under 13.
- Inspiration photos are for event planning.
- Event photos use an opt-out release model for photos/video taken by LT staff/representatives and public social/review photos LT can access.
- Invoice payment counts as acceptance of booking terms for now.
- Terms should cover temporary balloon/service limits including weather, heat, cold, wind, sunlight, altitude, venue conditions, handling, intended use, guest interaction, interference, third-party movement, and changes after setup.
- Personal balloon decor cancellations less than 7 days before the event receive no cash refund; any funds paid transfer to another event date or product.
- A sitewide cookie/tracking notice now stores `lt_cookie_consent` as `accepted` or `declined` and exposes `window.LT_COOKIE_CONSENT` for future analytics/ads wiring.

Verified route status from controller baseline:

- `/privacy` - 200
- `/terms-of-service` - 200
- `/refund-policy` - 200
- `/accessibility` - 200

Stripe Dashboard policy URLs should not be wired until policy content is source-traced and approved.

## Owner

Unassigned next agent/session.

## Source Map

Primary Odoo business-source files:

- `4-20-25-jeff-cameron/00-README.md` - states the folder is the single source of truth for that meeting.
- `4-20-25-jeff-cameron/05-legal-async-questionnaire-for-jeff.md` - lists launch-needed website legal docs and recommended defaults.
- `4-20-25-jeff-cameron/live-interview-answers.md` - completed Jeff answers for contract/payment/cancellation topics.
- `4-20-25-jeff-cameron/04-legal-live-interview.md` - interview prompt file; use carefully because unchecked items are prompts, not Jeff answers.
- `_resources/policies/legal-accounting-review-packet-2026-05-06.md` - current review packet for Jeff, legal counsel, and accounting/CPA.

Current ERPNext page files:

- `apps/locally_twisted/locally_twisted/www/privacy.html`
- `apps/locally_twisted/locally_twisted/www/terms_of_service.html`
- `apps/locally_twisted/locally_twisted/www/refund_policy.html`
- `apps/locally_twisted/locally_twisted/www/accessibility.html`
- `apps/locally_twisted/locally_twisted/policy_documents.py`
- `apps/locally_twisted/locally_twisted/verify/customer_documents_contract.py`

## Source Trace Matrix

| Page | Current route/file state | Traced source | Launch status |
|---|---|---|---|
| Privacy | Route exists. Page claims data collection, uses, sharing, analytics/advertising/tracking cookies, security, choices, children-under-13 online-data language, and `hi@locallytwisted.com` contact. | Questionnaire says Privacy Policy is launch-blocking and provides defaults/questions for data collected, tracking, selling, sharing, retention, privacy contact, marketing consent, children. GL business-proxy answers chose `hi@locallytwisted.com`, analytics/ads/tracking plus cart/session, and narrow children-under-13 language. | Business-approved for current copy; legal review still recommended. |
| Terms of Service | Route exists. Page claims booking confirmation rules, payment terms, cancellation reference, service area, weather, client responsibilities, website-use rules, and `hi@locallytwisted.com`. | Payment of invoice as signature, contract scope, deposits, Net 30, and 10% simple late fee trace to completed `live-interview-answers.md`. Broader ToS topics such as minimum age, customer uploads, dispute venue, class action, liability cap, warranty disclaimer, and change notices are in the unanswered questionnaire. | Partially sourced. Payment terms are strong; broader ToS legal terms need GL/legal approval or intentionally narrower launch language. |
| Refund / Cancellation | Route exists. Page claims deposits, personal decor refund windows, reschedule window, weather/no partial refund, LT cancellation goodwill, corporate late payments, ready-to-order no-return rule, and same-day damage report window. | Most payment/deposit/cancellation/weather/reschedule/corporate late-fee content traces to completed `live-interview-answers.md`. The less-than-7-days decor transfer/no-refund rule traces to GL business-proxy clarification on 2026-05-06. | Business-approved for current copy; legal review still recommended. |
| Accessibility | Route exists. Page says LT works to keep the site usable and uses `accessibility@locallytwisted.com`. | Questionnaire says Accessibility Statement exists and should be verified; default target is WCAG 2.1 AA and default contact is `accessibility@locallytwisted.com`. The answer appears not completed. | Low-risk but not final. Needs GL/legal approval on accessibility contact email and whether to state WCAG target/features. |
| Cookie policy/banner | No separate route found. Privacy page has a cookies/tools section and now discloses analytics, advertising, tracking, cart, and session storage. Sitewide `lt-site-preferences.js` shows an accept/decline notice and stores `lt_cookie_consent`; `lt-guest-cart.js` writes a `cart_count` cookie. The script filename is intentionally neutral because browser privacy extensions can block asset URLs containing `cookie-consent`. | GL business-proxy answer says launch expects analytics/ads/tracking plus cart/session storage. | Basic consent surface implemented; legal review and future analytics/ads wiring still need to honor the stored choice. |
| Shipping / Delivery | No separate route by design. Terms/FAQ carry delivery policy. Local checkout contract supports `$15` standard delivery, `$50` Park City delivery, non-taxable delivery lines, and out-of-area quote behavior. | GL business-proxy answer says delivery policy belongs in Terms/FAQ; windows are requested until confirmed; no-access/no-contact remains customer responsibility; damage report window is same day; out-of-area delivery is available for quote. | Business-approved for current copy; legal review still recommended. |
| Tax / service deposits | Checkout code treats goods as taxable and services, BTFP, service deposits, and delivery charges as non-taxable. Contact Lead records store artist-service deposit/payment guidance without creating money records. | GL clarified the non-taxable service/deposit/delivery rule in the 2026-05-06 commerce-rules session. Customer-facing copy should not add service tax language. Accountant/legal approval is still appropriate before final live tax-policy claims. | Code verified locally; copy corrected away from service-tax claims. |
| Customer documents and emails | Inquiry auto-ack emails, paid-order receipts, and checkout notices now use the anchored policy lanes without adding ERPNext setup records. | GL approved separating the standard terms/refund pages by event decor, ready-to-order pickup/delivery, face painting/balloon twisting, and corporate invoicing. The implementation keeps exact links instead of generic policy links and preserves whitelabel/code-owned control. | Locally verified by `customer_documents_contract.py` and `payment_cascade_contract.py`; legal/accounting review still recommended. |

## Immediate Blockers

- Future analytics/ads/tracking code must honor `window.LT_COOKIE_CONSENT.hasAcceptedOptional()` before loading optional tracking.
- Terms page contains broader legal topics that are business-approved only, not attorney-approved.
- Tax/service/deposit language is implemented in checkout and corrected in current copy, but accountant/legal review is still appropriate before final live tax-policy claims.
- Future legal invoice/document terms should be code-owned or custom-template-owned first. Only add ERPNext Terms/Email Template records if the actual customer-facing invoice path requires them.
- Do not wire Stripe Dashboard URLs until the policy set is approved.

## Safe Next Slice

Prepare the legal/accounting approval packet and future analytics wiring rules:

1. Present the matrix above with GL business-proxy answers already captured.
2. Send `_resources/policies/legal-accounting-review-packet-2026-05-06.md` for legal/accounting review of public policy/live-readiness claims.
3. When analytics/ads/tracking are wired, load optional trackers only after `window.LT_COOKIE_CONSENT.hasAcceptedOptional()` returns true.
4. Re-run route and layout checks.
5. If customer email, receipt, invoice, or policy-lane copy changes, rerun `python scripts/verify/customer_documents_contract.py` and `python scripts/verify/payment_cascade_contract.py`.

## Do Not Do

- Do not invent legal terms to make the site look complete.
- Do not rely on ERPNext page copy as business truth.
- Do not use unchecked questionnaire prompts as Jeff-approved answers.
- Do not wire Stripe policy URLs while policy content is still unresolved.

## Verification

After policy edits:

```powershell
python scripts/verify/nav_ia.py
npm run test:layout-fit
```

Then route-check:

```powershell
python - <<'PY'
import urllib.request
for route in ['/privacy', '/terms-of-service', '/refund-policy', '/accessibility']:
    resp = urllib.request.urlopen('http://localhost:8081' + route, timeout=12)
    print(route, resp.status, resp.geturl())
PY
```

Before Stripe Dashboard wiring, manually confirm:

- page routes are public
- footer or checkout links expose required policies
- policy copy has GL/legal approval
- cookie/tracking posture is documented
