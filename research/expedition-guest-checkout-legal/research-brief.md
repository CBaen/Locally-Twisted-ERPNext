# Research Brief — Guest Checkout Legal Compliance (US, all 50 states)

## Want

A US customer can buy a $55–$200 themed balloon item from Locally Twisted's webshop without ever being shown a "create an account" form. They enter email + name + shipping at checkout, pay via Stripe, and receive an emailed receipt. Behind the scenes a customer record exists tied to their email; they may optionally set a password later to view order history, but never have to. A separate optional checkbox at checkout offers marketing emails — unchecked by default. All of this must be unambiguously legal in every US state with no liability exposure for the merchant (a Utah LLC).

## Have

- **Merchant:** Locally Twisted, LLC. Utah-incorporated 2014. Active sales tax license. Active business license. Insurance: GL + Product + Worker's Comp + Fleet. Most customers are Utah residents; some out-of-state corporate clients. Annual revenue well below California / Virginia / Colorado / Texas privacy-law applicability thresholds (e.g., CCPA's $25M / 100K-consumer thresholds), but laws apply where the **consumer** resides regardless of merchant size in some jurisdictions.
- **Stack:** ERPNext v15.105.0 with `webshop` and `payments` apps. Stripe Test gateway configured (Stripe-Test). 30+ priced Website Items live ($55–$180 range, mostly themed bouquets and balloon decor). Webshop's current `cart.py` requires `frappe.session.user` (a logged-in User record) to complete checkout — verified at lines 379, 407, 409, 424, 539. ERPNext provides Email Templates + Notifications + `frappe.sendmail()` for transactional email (built-in). User creation has a `send_welcome_email` flag (verified at `frappe/core/doctype/user/user.py:129, 363`) that can be set to 0 to suppress the default welcome email.
- **Proposed flow:** at checkout the customer provides email + name + shipping; we silently create User (random password, `send_welcome_email=0`), Customer, Contact records; create Quotation → Sales Order; route payment through Stripe; on success send a transactional purchase receipt via Email Template + Notification. A separate marketing-opt-in checkbox sets a `marketing_opt_in` Custom Field on Customer (default 0).
- **Out of scope of this brief:** PCI compliance for card data (Stripe handles); minor (under-13) data (LT does not knowingly serve minors); B2B contract law; international customers (US only).

## Won't Accept

- Any flow that is unlawful in any US state — must be uniformly legal across the country, no state-by-state geofencing.
- Any flow that creates personal liability for Jeff Kimber or the LT LLC under state privacy or consumer protection laws.
- Forced registration form between cart and Stripe (the customer must not see "create an account").
- Marketing/promotional content in the receipt email (transactional only — strict separation).
- Any pattern requiring written or verbal lawyer review on each individual purchase.
- Patterns that depend on dark-pattern UX (pre-checked marketing boxes, hidden disclosures, deceptive language).

## Open To

- Adding required disclosures to the checkout page (privacy policy link, terms acceptance, data-use notice).
- Adding a privacy policy and terms-of-service page if not already required.
- Building a marketing-opt-in checkbox that requires affirmative action.
- State-specific disclosure language if any state demands it at checkout.
- Adopting a "no User account at all" architecture (Customer + Contact only, email as identifier) if that's safer than the silent-User pattern — currently leaning silent-User but flexibility is there.
- Adding consumer-rights mechanisms (data access, deletion request, opt-out) via web form or email address if any applicable state requires them.
- Adding an age gate or affirmation if any state requires it for general retail.

## Questions

1. **Silent account creation:** Is creating a User record (with random password, no welcome email) during a checkout flow — without an explicit "create account" UI step — legal in all 50 US states under their privacy and consumer protection laws? Specifically: does collecting customer data for order fulfillment AND simultaneously creating an account record require disclosure beyond a privacy policy link?
2. **State privacy laws applicability:** For each state with a comprehensive privacy law as of 2026 (CA — CCPA/CPRA; VA — VCDPA; CO — CPA; CT — CTDPA; UT — UCPA; TX — TDPSA; OR — OCPA; FL — FDBR; IA — ICDPA; MT — MCDPA; TN — TIPA; IN — INCDPA; DE — DPDPA; NH — NHDPA; NJ — NJDPCA; MN — MCDPA; MD — MODPA; RI — DTPPA; etc.), do thresholds apply to a Utah-based small LLC selling sub-$200 retail goods to in-state customers? Where do thresholds NOT apply (i.e., laws bind regardless of merchant size)?
3. **CAN-SPAM and transactional emails:** What header, sender-identification, and content requirements apply to a purchase receipt email under federal CAN-SPAM (15 USC 7701)? What is the legal definition of a "transactional or relationship message" under 16 CFR § 316.3 — and does our proposed receipt qualify? Do any states layer additional requirements on top of CAN-SPAM for transactional emails?
4. **Marketing email opt-in:** Is checkbox-based affirmative opt-in (unchecked by default) sufficient consent for marketing emails in every US state? Or are any states requiring double opt-in, written consent, or specific disclosure language?
5. **Checkout-page disclosures:** What language must appear on or near the checkout button on a US e-commerce site? Specifically: privacy policy link, terms of service acceptance, data-use notice, or any state-specific disclosure (e.g., California's "Notice at Collection")? Is "click-wrap" acceptance sufficient or is "browse-wrap" enough?
6. **Utah Consumer Privacy Act (UCPA):** Effective Dec 31, 2023. What does it require of a Utah-based small LLC selling to Utah residents? Even if revenue thresholds exempt LT from full UCPA obligations, are there minimum-floor requirements? What consumer rights mechanisms (access, deletion, opt-out of sale, opt-out of targeted ads) must we provide regardless of size?
7. **Silent User vs no-User architecture:** Does creating a User account with a random password (vs. collecting only email + Customer + Contact, no User) materially change our obligations under state breach-notification laws? If a breach exposed the dormant User records, are we held to a higher standard than if we'd never created Users?
8. **Privacy policy + terms-of-service minimum content:** What sections and language must a privacy policy and ToS contain for a small US e-commerce site as of 2026? Identify the floor (federal + most-restrictive state) so we can draft a single document that's legal everywhere.
9. **Marketing-opt-in storage and revocation:** If a customer checks "send me offers," what are our obligations for (a) honoring opt-out via unsubscribe link in marketing emails (CAN-SPAM 10-day rule), (b) data retention policies, (c) recordkeeping of consent itself? Are any states stricter?
10. **Recommended floor:** Synthesize the strictest-rule-wins set of disclosures, mechanics, and policies the proposed flow must include to be legal in every US state. List concretely what we need to ship before launch (checkout-page text, privacy policy clauses, ToS clauses, opt-in mechanics, opt-out mechanics, data-deletion-request mechanism, etc.).

---

**Note for researchers:** This brief is for information-gathering, not legal advice. Final compliance sign-off will come from a Utah attorney before live launch. The output of this expedition will be reviewed by counsel; aim for citation-rich, statute-rich findings researchers can hand directly to a lawyer.
