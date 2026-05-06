# Policy And Trust Workstream

Last updated: 2026-05-06 by Codex.

## Outcome

Make the launch policy/trust surface accurate enough to support customer trust and Stripe readiness without inventing legal or business terms.

Business source of truth: `C:\Users\baenb\projects\locally-twisted-odoo\4-20-25-jeff-cameron\`.

Do not treat current ERPNext policy pages as authoritative until each claim is traced to the Odoo business source, current GL approval, or legal approval.

## Current Stage

Source-trace pass started. Routes load, but content is not launch-approved.

Checkout now has a verified local commerce-rule contract, but policy copy still needs approval before it becomes customer/legal language. Current local behavior: goods are taxable by fulfillment ZIP/city rate; services, face painting, balloon twisting, deposits for those services, and delivery charges are non-taxable; local delivery is `$15`, Park City delivery is `$50`, and out-of-area delivery requires a quote.

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

Current ERPNext page files:

- `apps/locally_twisted/locally_twisted/www/privacy.html`
- `apps/locally_twisted/locally_twisted/www/terms_of_service.html`
- `apps/locally_twisted/locally_twisted/www/refund_policy.html`
- `apps/locally_twisted/locally_twisted/www/accessibility.html`

## Source Trace Matrix

| Page | Current route/file state | Traced source | Launch status |
|---|---|---|---|
| Privacy | Route exists. Page claims data collection, uses, sharing, cookies, security, choices, and `hi@locallytwisted.com` contact. | Questionnaire says Privacy Policy is launch-blocking and provides defaults/questions for data collected, tracking, selling, sharing, retention, privacy contact, marketing consent, children. The questionnaire appears unanswered. | Not content-approved. Needs GL/legal decision on privacy defaults, tracking, retention, privacy contact email, and cookie posture. |
| Terms of Service | Route exists. Page claims booking confirmation rules, payment terms, cancellation reference, service area, weather, client responsibilities, website-use rules, and `hi@locallytwisted.com`. | Payment of invoice as signature, contract scope, deposits, Net 30, and 10% simple late fee trace to completed `live-interview-answers.md`. Broader ToS topics such as minimum age, customer uploads, dispute venue, class action, liability cap, warranty disclaimer, and change notices are in the unanswered questionnaire. | Partially sourced. Payment terms are strong; broader ToS legal terms need GL/legal approval or intentionally narrower launch language. |
| Refund / Cancellation | Route exists. Page claims deposits, personal decor refund windows, reschedule window, weather/no partial refund, LT cancellation goodwill, corporate late payments. | Most payment/deposit/cancellation/weather/reschedule/corporate late-fee content traces to completed `live-interview-answers.md`. Materials-cost deduction traces to a lawyer drafting note, not a direct final Jeff policy. | Mostly sourced, but needs legal/GL review for decor cancellation gap between 72 hours and 7 days and for materials-cost deduction wording. |
| Accessibility | Route exists. Page says LT works to keep the site usable and uses `accessibility@locallytwisted.com`. | Questionnaire says Accessibility Statement exists and should be verified; default target is WCAG 2.1 AA and default contact is `accessibility@locallytwisted.com`. The answer appears not completed. | Low-risk but not final. Needs GL/legal approval on accessibility contact email and whether to state WCAG target/features. |
| Cookie policy/banner | No separate route found. Privacy page has a cookies/tools section. `lt-guest-cart.js` writes a `cart_count` cookie. | Questionnaire lists Cookie Consent Banner + Policy as launch-blocking and says essential-only cookies can use a simple one-line banner if no third-party tracking is used. | Open blocker. Need decide whether launch uses essential cookies only and whether a separate banner/policy is required. |
| Shipping / Delivery | No separate route found in the ERPNext policy set. Terms page has service area and travel-fee text. Local checkout contract now supports `$15` standard delivery, `$50` Park City delivery, non-taxable delivery lines, and out-of-area quote-required behavior. | Questionnaire lists Shipping & Delivery Policy as launch-blocking and has unanswered delivery-zone/logistics questions. `04-legal-live-interview.md` includes a prompt line for free delivery in Davis, Weber, Salt Lake, and Utah counties, but that file is a prompt, not completed answers. Current checkout behavior traces to GL clarification in the 2026-05-06 commerce-rules session, not legal approval. | Open blocker. Need source-traced delivery policy or GL/legal/accountant approval before Stripe/live-readiness claims. |
| Tax / service deposits | Checkout code now treats goods as taxable and services, BTFP, service deposits, and delivery charges as non-taxable. Contact Lead records store artist-service deposit/payment guidance without creating money records. | GL clarified the non-taxable service/deposit/delivery rule in the 2026-05-06 commerce-rules session. Accountant/legal approval is still required before the website presents this as final tax/legal policy language. | Code verified locally; copy not launch-approved. |

## Immediate Blockers

- Privacy answers are not completed or approved.
- Shipping/delivery policy is missing or folded into Terms without completed source answers.
- Tax/service/deposit language is now implemented in checkout but not approved as public legal/accounting copy.
- Cookie banner/policy posture is not implemented or approved.
- Terms page contains broader legal topics that are not fully sourced.
- Refund page has a decor cancellation ambiguity: completed answers cover 14+ days, 7-14 days, and <72 hours, leaving 72 hours to 7 days unclear.
- Do not wire Stripe Dashboard URLs until the policy set is approved.

## Safe Next Slice

Prepare a GL/legal approval packet instead of editing policy copy blind:

1. Present the matrix above.
2. Ask GL/legal/accountant to choose privacy defaults, tracking/cookie stance, privacy contact email, delivery policy, tax/service/deposit wording, and decor 72-hour-to-7-day cancellation rule.
3. After approval, update only the policy page copy and footer links needed for launch.
4. Re-run route and layout checks.

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
