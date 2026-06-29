# Meta Bouquet Ad Test - 2026-06-28

## Scope

Operating brand: `locally_twisted`.

Prepare a Locally Twisted Meta ad landing page and first measurement plan for
this ready-to-order bouquet product:

- Large head Missionary:
  `/shop-items/bouquets/large-head-missionary`

2026-06-29 focus correction: the first ad attempt should focus on Large head
Missionary only. Birthday Deliveries remains useful, but it is held until the
missionary attempt is reviewed and is not routed in this release.

This work is source and planning only. It does not approve or perform live Meta
campaign creation, spend, audience changes, custom conversions, standard event
changes, customer-list use, Frappe Cloud deploys, or live ERPNext/Frappe
settings changes.

2026-06-29 live product-copy update:

- Live `Website Item` `WEB-ITM-0039` / `large-head-missionary` was updated
  through the existing logged-in Frappe browser session. This was a scoped
  product-copy data update only.
- Public verification at
  `https://locallytwisted.com/shop-items/bouquets/large-head-missionary`
  confirmed the live product page now includes `mission calling`,
  `SLC airport`, `homecomings`, `open houses`, and `farewell events`, and no
  longer includes the old departure-first phrases `day someone leaves on a
  mission` or `send-off bouquet`.
- No live Meta campaign/ad set/ad/ad creative/budget/audience/status changed.
- No live Frappe Cloud app deploy or source release was performed.
- `/missionary-balloon-gift` remains a live 404 until the source landing-page
  route is released through Frappe Cloud.
- Live `/faq` and `/contact` are app-template routes, not editable `Web Page`
  records; source has been corrected, but live still shows stale checkout pause
  wording until a Frappe Cloud app release.

## Research Basis

Official/current-source checks used:

- Meta Pixel get-started docs:
  `https://developers.facebook.com/docs/meta-pixel/get-started/`
  describe PageView tracking through `fbq('track', 'PageView')`.
- Meta Pixel reference:
  `https://developers.facebook.com/docs/meta-pixel/reference/`
  documents standard events through `fbq('track')`, including events such as
  `ViewContent`, `AddToCart`, and `Purchase`.
- Meta Marketing API Insights:
  `https://developers.facebook.com/docs/marketing-api/insights/`
  is the reporting source for ad performance data such as delivery and spend
  metrics.
- Meta Business Help, landing page views:
  `https://www.facebook.com/business/help/417293491972212`
  says landing-page-view optimization tries to show ads to people likely to
  click and fully load the website.
- Meta Business Help official snippets checked on 2026-06-28 say location
  targeting is used to show ads to people in specific geographic areas,
  Advantage+ audience uses Meta's AI to find the audience, detailed targeting
  may broaden beyond selected interests, and Audience Controls include
  locations and minimum age. The pages themselves were login-blocked in the
  browser, so treat this as official-snippet evidence until Ads Manager setup
  confirms the exact available controls.
- Meta ad personal-attributes policy:
  `https://transparency.meta.com/policies/ad-standards/objectionable-content/privacy-violations-personal-attributes/`
  says ads must not assert or imply personal attributes such as religion or
  beliefs. Meta's examples allow product/service descriptions such as
  religion-adjacent dating services, but disallow copy that asks or implies
  the viewer's own religious identity. The missionary route should therefore
  use "Missionary" and Utah-local event context, but avoid "Are you..." or
  "meet other..." personal-attribute phrasing.
- Direct authenticated Meta targeting search on 2026-06-29 used the current
  system-user token against Graph API `v25.0`. It performed GET-only
  targeting-search and suggestion calls; no campaign, ad set, budget, creative,
  customer data, lead, message, pixel, or access mutation occurred. Results:
  - `Mormon`, `Mormons`, and `LDS` did not return usable LDS/Mormon audience
    interests. The only Mormon-related hits were Broadway musical interests;
    `LDS` returned `Ryan Reynolds`.
  - `Latter-day Saint`, `Latter-day Saints`, `LDS Church`, `Missionary`,
    `Missionary work`, `Missionaries`, `Mission call`, `Return missionary`,
    `missionary homecoming`, and `SLC airport` returned zero ad-interest
    matches.
  - Usable non-sensitive product/context signals did return, including `Utah`,
    `Salt Lake City`, `Homecoming`, `Gift`, `Custom gifts and clothing`,
    `Party supply stores`, and `Event management`.
  - Recommendation from the confirmed account state: do not build the first
    missionary ad around direct Mormon/LDS/Missionary detailed targeting. Use
    local delivery geography, a 30-65+ buyer age range, broad Advantage-style
    delivery, and product/event creative that clearly says `Missionary`,
    `SLC airport`, `homecoming`, `mission call`, and `farewell party`.
- Direct authenticated Meta asset confirmation on 2026-06-29:
  - Ad account `act_27813262` is active, USD, `America/Denver`.
  - Page `Locally Twisted` is connected to Instagram business account
    `locally_twisted`.
  - Pixel `1079085392230103` / `locally twisted` is present and had
    `last_fired_time` on 2026-06-28.
  - The older Shopify pixel `149178523772697` is present but last fired in
    2021.
  - Custom conversions are currently empty.
  - Last-7-day insights returned zero rows.
  - No Meta mutation occurred.
- Direct Ads Manager UI check on 2026-06-29 opened
  `https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=27813262`
  in the existing Brave browser session. Meta redirected to the Ads Manager
  login page, so UI confirmation is blocked until GL logs into Meta in Brave.
  Treat the Marketing API proof above as the current direct account evidence;
  do not claim browser UI access is ready.
- SLC airport missionary/homecoming context:
  - Finance & Commerce/Bloomberg reported that returning missionaries are often
    greeted at Salt Lake City International Airport by family, banners,
    balloons, horns, photographers, and large meet-and-greet crowds:
    `https://finance-commerce.com/2018/10/salt-lake-city-renovates-airport-with-nod-to-mormon-missionaries/`
  - KUTV/AP reported that returning missionary greetings include crowds,
    banners, balloons, videographers, and homecoming parties:
    `https://kutv.com/news/local/crowds-banners-balloons-greet-lds-missionaries-at-airport-05-29-2015`
  - Deseret News described SLC airport welcome committees with banners,
    balloons, phones recording, and returning missionary families as a frequent
    local scene:
    `https://www.deseret.com/opinion/2023/6/21/23767292/salt-lake-city-airport-latter-day-saint-missionaries/`

## 2026-06-29 Missionary Positioning Correction

GL corrected the missionary product angle: this should not be departure-first.
The strongest buyer contexts are:

1. Congratulating someone on a mission calling.
2. The missionary return/homecoming, especially SLC airport pickup.
3. Welcome-home porches, open houses, and family photos.
4. Farewell events last, because the balloon cannot travel on the plane but can
   still work as a farewell-party gift or table piece.

The website and landing-page copy should use `Missionary`, `mission calling`,
`SLC airport`, `return`, `homecoming`, and `farewell`. It does not need to use
`Mormon` or `LDS` for Utah buyers to understand the context.

## Landing Pages

New customer URL:

- `/missionary-balloon-gift`

Final Meta test URL:

- `/missionary-balloon-gift?utm_source=meta&utm_medium=paid_social&utm_campaign=lt_bouquet_test_2026q3&utm_content=missionary_gift_ad_v1`

The landing page:

- make the ad promise match the exact product configurator;
- preserve `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`,
  `utm_content`, and `fbclid` from the ad URL onto product/contact CTAs;
- avoid direct `fbq`, `gtag`, or GTM calls in the route template;
- route the customer to the product configurator first, with contact as the
  fallback for delivery/timing questions;
- use local product media already present on the live product page.
- position the missionary page around mission call celebrations, SLC airport
  returns, homecomings, welcome-home/open-house photos, and farewell events.

## First Test Recommendation

Draft campaign shape for later approval:

- Objective: Traffic, optimized for landing page views, for the first small
  test because only consent-gated PageView tracking is approved in source.
- Structure: for the first attempt, one missionary ad set and one missionary ad
  are enough. Keep Birthday Deliveries out of the first launch so the first
  readout is about this product, not two different buyer jobs competing for the
  same small budget.
- Geography: first test should stay inside standard local delivery counties:
  Davis, Weber, Salt Lake, and Utah counties. Do not include Park City/Summit
  in the first $20/day test unless GL deliberately wants to test the $50
  delivery lane; live FAQ says Park City delivery is ZIP `84060`, `84068`, and
  `84098`.
- Audience controls/demographics:
  - Missionary Balloon Gift: all genders, ages 30-65+, standard local delivery
    counties.
  - Use age as a buyer-likelihood guard, not as copy. Do not write copy that
    calls out age or implies the viewer's personal traits.
- Detailed targeting: keep the first test broad. Direct authenticated Meta
  targeting search did not return usable Mormon/LDS/Missionary interests for
  this ad account. If detailed targeting is used at all, keep it to
  non-sensitive product/event signals such as `Gift`, `Homecoming`,
  `Salt Lake City`, `Utah`, `Party supply stores`, and `Event management`, and
  expect Advantage audience delivery to broaden. Do not use customer lists,
  lookalikes, or offline customer data without separate approval.
- Placements: Meta placements can be proposed for Facebook and Instagram, but
  exact placements/status need approval before launch.
- Budget status: GL approved `$20/day total` on 2026-06-28. Since the first
  attempt is now missionary-only, the launch packet should ask whether to use
  the full approved ceiling on one missionary ad set or start lower. The budget
  ceiling does not approve campaign launch, audience/location setup, creative
  upload, schedule, tracking changes, or ad status.
- Creative: product-photo-led static ads first. More variants can be added
  after the first signal pass.

## Draft Ad Copy

Missionary Balloon Gift:

- Headline: `Make the missionary welcome-home moment impossible to miss.`
- Primary text: `Celebrate the mission calling, the SLC airport return, the welcome-home porch, or the farewell party with a personalized larger-than-life missionary balloon gift.`
- CTA: `Shop Now` or `Learn More`
- Final URL: missionary final URL above.
- Alternate headline: `A photo-ready missionary balloon gift for the big Utah moments.`
- Alternate primary text: `Choose Elder or Sister, skin tone, hair color, and accents online. Built for airport pickups, homecomings, mission call celebrations, open houses, and farewell events.`

Policy note: keep the missionary copy product/event focused. Avoid phrases such
as "Are you LDS?", "your religion", "your faith", or "meet other..." patterns
that imply personal attributes. The word "Missionary" is required because it is
the product/event language Utah buyers recognize.

Hashtags/keywords note:

- Meta paid ads do not work like Google keyword campaigns. Keywords are useful
  for landing-page copy, competitor research, creative signals, and maybe
  detailed-targeting suggestions, but there is no search-keyword bidding plan
  in this Meta test.
- Do not stuff hashtags. For static Facebook/Instagram ads, use zero hashtags
  first or at most one generic brand/context tag if the creative format expects
  it, such as `#UtahBalloons` or `#BirthdayBalloons`.
- Avoid Mormon/LDS hashtags in paid missionary ads until Ads Manager/policy
  research confirms the risk. The creative and landing page should use
  `Missionary`, `SLC airport`, `homecoming`, `mission calling`, and `farewell`
  language because Utah buyers will understand the context.

## Measurement Plan

Available once these pages are deployed and tracking settings remain approved:

- Meta PageView via the existing consent-gated pixel bridge.
- Meta landing page view and delivery metrics inside Ads Manager.
- URL-level UTM reporting from the two final URLs.
- Attribution preservation from landing page to product/contact CTAs.
- Public form attribution capture through the existing LT marketing bridge when
  a visitor submits a form.

Not yet approved or implemented:

- `ViewContent`, `AddToCart`, `InitiateCheckout`, or `Purchase` browser events.
- Conversions API/server events.
- URL-based custom conversions in Meta.
- Offline conversion upload or customer-list audiences.
- ROAS or purchase optimization based on verified events.

Recommended next measurement upgrade after landing pages are reviewed:

1. Add a disabled-by-default event taxonomy for `ViewContent`, `AddToCart`,
   `InitiateCheckout`, and `Purchase`.
2. Verify locally that events are consent-gated, deduplicated, and do not expose
   PII.
3. Request exact approval before enabling standard events or custom
   conversions.
4. Move later campaigns from landing-page-view learning toward Sales/Purchase
   optimization only after event quality is proven.

## Pre-Spend Research And Blockers

Do this before the first dollar is spent:

1. Resolve checkout-path truth. Live FAQ/contact copy said online checkout or
   ready-to-order was paused while the live product page exposed checkout
   controls. Source copy has been changed to say checkout is available on
   ready-to-order product pages that show online ordering, while quote/contact
   remains the path for custom installs, delivery questions, out-of-area
   delivery, and timing that needs confirmation. Live FAQ/contact still need a
   Frappe Cloud app release and public verification.
2. Browser-proof the two landing pages on desktop and mobile after they are in
   the correct Frappe runtime path. The isolated task worktree is source-proven,
   not rendered-proven.
3. Confirm the checkout/product path works for both products through the point
   before payment, including delivery/pickup choices and no false success.
4. Confirm delivery geography with Jeff/GL. Source/public FAQ supports Davis,
   Weber, Salt Lake, and Utah counties for standard local delivery; Park City is
   a separate $50 delivery lane.
5. Re-run Meta read-only inventory or inspect Ads Manager to confirm the ad
   account, billing/payment method, Page/Instagram placement availability,
   Pixel, custom conversions, and no active conflicting campaigns. The latest
   inventory rerun from this worktree was blocked by missing `META_ACCESS_TOKEN`
   in the shell; no Meta request was made.
6. Direct authenticated Meta targeting search found no usable
   Mormon/LDS/Missionary detailed interests. Do not spend time forcing that
   targeting path for attempt one; rely on local geography, buyer-age controls,
   product/event copy, and creative.
7. Check Meta Ad Library and local competitors for active balloon delivery,
   birthday balloon, missionary homecoming, mission call, and SLC airport pickup
   gift ads in Utah. Capture pricing, promise, offer, image style, and CTA
   patterns.
8. Choose final creative crops for Feed, Stories/Reels, and mobile landing-page
   preview. Do not launch with raw product images that crop the product badly.
9. Decide whether PageView/landing-page-view measurement is enough for this
   small test. If the goal is real impact measurement, implement and approve at
   least `ViewContent`, `AddToCart`, `InitiateCheckout`, and `Purchase` or an
   equivalent server-side purchase attribution lane before judging ROAS.
10. Define the 7-day readout: spend, impressions, reach, frequency, CPM, CTR,
   CPC, landing page views, cost per landing page view, product CTA clicks where
   available, attributed inquiries/orders, and manual order notes.

## Approval Needed Before Live Action

Use this approval packet before each live step:

```text
Platform:
Object:
Current state:
Proposed change:
Business reason:
Data touched:
Spend/billing impact:
Customer-visible impact:
Rollback:
Exact approval needed:
```

Minimum approvals still needed:

- Approved on 2026-06-29: deploy the missionary landing page, FAQ/contact
  source copy, and verifier support to the approved site.
- Birthday Deliveries requires a separate review and approval before routing.
- Approve creating the exact Meta campaign/ad sets/ads, including objective,
  budget, schedule, audience, placements, creative, final URLs, and initial
  status.
- Approve any measurement change beyond the already approved PageView lane.

## Verification

Source checks run on 2026-06-28:

- `python -m py_compile apps/locally_twisted/locally_twisted/www/product_ad_pages.py apps/locally_twisted/locally_twisted/www/missionary_balloon_gift.py scripts/verify/meta_bouquet_ad_landing_pages.py`
- `npm run test:meta-bouquet-ad-landing`
- `python scripts/verify/marketing_measurement_bridge_contract.py`
- `node --check scripts/verify/layout_helpers.js`
- `node -e "JSON.parse(require('fs').readFileSync('package.json','utf8')); JSON.parse(require('fs').readFileSync('verifier-manifest.json','utf8'));"`
- `python scripts/verify/verifier_cli_contract.py`
- capability evidence JSONL parse check
- `python /home/guidingl/projects/capabilities-framework/tools/capability_maintenance_review.py --root project=/home/guidingl/agent-worktrees/builtbycameron-lt/codex-20260628-lt-meta-bouquet-ad-groundwork__bouquet-ads/capabilities --no-write --json`

Capability maintenance note:

- Added one evidence event to
  `capabilities/evidence/capability-evidence.jsonl`.
- The read-only maintenance review completed without writes and reported the
  existing project capability root as graph-unhealthy: 42 graph errors and 58
  graph warnings. This ad slice did not add a new capability card, dependency,
  or backlink edge. A broad LT capability graph repair should be handled as its
  own cleanup lane.

Unverified:

- Rendered Frappe browser layout in this task worktree.
- Frappe Cloud deployment/live route availability.
- Live Meta campaign setup or ad delivery.
- Purchase or add-to-cart measurement.

The render gap exists because the local Frappe stack mounts the main checkout,
not this isolated task worktree. Browser proof should happen after this branch
is reviewed in the correct local/staging app path or after an approved staging
deploy.
