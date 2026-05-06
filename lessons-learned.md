# Lessons Learned — Locally Twisted

**Append-only.** Newest entries at the top. Each entry: what happened, what was learned, what to do differently next time.

LT-specific patterns. Cross-client / agency-wide lessons go to `Built_by_Cameron/lessons-learned.md`. If a lesson is broadly applicable across all ERPNext builds, it ALSO goes to the global `C:\Users\baenb\.claude\lessons-learned.md`.

---

## 2026-05-06 - Report rows can become a hidden send surface

The customer reminder report looked like a harmless display layer because it only turned dry-run queue items into table rows. In a business system, a table row can still become the surface a future agent wires to a send button or schedule.

**Counter-move:** carry no-live flags into the report payload and every row, not just the source queue. For LT, `customer_reminder_review_report.py` marks the whole report `send_allowed: false`, `customer_delivery_enabled: false`, and `mutation_allowed: false`, and `customer_reminder_review_report_contract.py` rejects malformed send-enabled source rows before a Desk UI exists.

---

## 2026-05-06 - No-live reminder setup still needs send blockers

Customer reminders can feel safe when the code only builds an internal queue. They are still one step away from customer-facing collections, so every queue item needs explicit blockers for approval, recipient, invoice status, cadence, copy, and payment path.

**Counter-move:** keep the reminder surface `internal_review_only` and `draft_only_not_sent`, and test malformed send-enabled packets with fake data. For LT, `customer_reminder_dry_run_contract.py` proves overdue/current/missing-payment-path/malformed scenarios without creating database records, while the live dry-run verifier proves no Email Queue, Communication, Error Log, invoice, payment, or journal counts change.

---

## 2026-05-06 - Synthetic audits must not inherit live cutover blockers

The paperwork/backend lane started mixing two very different questions: "Can fake data safely flush out broken cascading information?" and "Are live Stripe keys and production site settings ready?" The live checks were not needed for the current work and made a fake-data audit look blocked by credentials GL explicitly barred.

**Counter-move:** keep synthetic operating readiness and live cutover readiness separate in code, verifier output, and docs. For LT, `paperwork_status.py` now runs in `synthetic_without_live_credentials` mode, `paperwork_review_digest.py` reports `cutover_deferred_not_blocking`, and `synthetic_business_pipeline.py` fails if live payment readiness is labeled as a current blocker. Run live Stripe readiness only when cutover work begins.

---

## 2026-05-06 - Aggregate digests need recursion and mutation boundaries

The paperwork review digest needed to summarize the business automation index, and the automation index also needed to classify the digest. Calling the full index from the digest would create a self-check loop once the digest was indexed.

**Counter-move:** aggregate review surfaces should call index/report helpers in a scoped mode that excludes the aggregate itself, and they need their own mutation guard. For LT, `business_automation_index.run(include_digest=False, include_synthetic=False)` lets `paperwork_review_digest.run` summarize partial connections without recursively checking the digest or synthetic pipeline surface. The digest also guards Email Queue, Communication, Payment Request, Payment Entry, Journal Entry, Sales Invoice, and Error Log counts.

---

## 2026-05-06 - Rendering a draft is still an automation boundary

The unpaid invoice draft packet renderer feels safer than reminder sending because it only produces review output. It still touches a dangerous business boundary: customer communication and invoice follow-up. If a renderer quietly creates an Email Queue row, Communication, Payment Request, Payment Entry, Journal Entry, or invoice mutation, it has become delivery or accounting automation without approval.

**Counter-move:** draft renderers need the same negative proof as review queues. The unpaid invoice packet verifier now confirms `read_only`, `send_allowed: false`, `mutation_allowed: false`, draft-only packet/section status, human approval gates, and unchanged guarded counts. Use that pattern before building Desk queues, scheduled digests, statement generators, or reminder send paths.

---

## 2026-05-06 - A draft-only reminder still needs a mutation guard

The unpaid invoice review surface looked safe because it only reads invoices and returns candidate data. That is not enough proof in a business system. If a future helper accidentally queues an email, creates a Communication, or changes a Payment Request while building the review list, the surface becomes collections automation without approval.

**Counter-move:** finance review helpers should prove the negative. The unpaid invoice verifier now checks `read_only`, `send_allowed: false`, `mutation_allowed: false`, draft-only document status, and guarded counts for Email Queue, Communication, Sales Invoice, Payment Request, Payment Entry, and Journal Entry. Use that pattern before adding any reminder, statement, or collections-related review queue.

---

## 2026-05-06 - Keep the useful prototype behavior, not the whole prototype

The portfolio correction after the exact-handoff pass showed a second failure mode: once a reference is rendered correctly, it can still be wrong for production if Codex carries over the whole prototype instead of the part GL actually wants. GL wanted the overlapping collage and stronger center balance. She did not want the tall hero, copied font imports, custom cursor, fake shell, or small production photos.

**Counter-move:** after matching a visual reference, immediately ask what belongs to production and encode that boundary in source and verifiers. For LT `/portfolio`, the current rule is: compact `What We Do` hero, native LT shell/global typography, large whole installed-work images, frequent center-column photos, no portfolio-specific Google font imports, no custom cursor artifacts, and warm page-matched image frames. The verifier should fail if the page regresses into either a small safe row or a wholesale prototype copy.

---

## 2026-05-06 - Automation needs a machine-readable map, not only a handoff paragraph

The paperwork/backend lane had many working pieces: contact intake, Lead cascade, checkout, payment success, receipts, invoice branding, outbound templates, and finance visibility. The risk was that future agents could treat "exists" as "connected" or treat a native ERPNext DocType as operational readiness. That is exactly how silent failures slip into business systems.

**Counter-move:** create a verifier-backed automation index for cross-system business work. The index should separate connected surfaces, partial surfaces, required missing surfaces, useful future surfaces, fake-data test paths, and loud-failure gaps. Keep it scheduled in Frappe when the site is expected to operate as a business system, and update the index whenever a new automation surface is added.

---

## 2026-05-06 - Hosted checkout amount parity is not implied by ERPNext totals

The money-path audit found that Stripe Checkout line items could be generated from Sales Order item rates while ERPNext `grand_total` includes taxes or charges. That means the ERPNext order can be right while hosted checkout charges the wrong amount. A local payment-readiness check is not enough proof for amount parity.

**Counter-move:** contract-test the Stripe payload builder directly. Convert money to cents, compare line-item totals to the ERPNext `grand_total`, add an explicit tax/charges adjustment when needed, and raise before redirect when the item lines exceed the ERPNext total. Any future checkout/payment refactor must rerun `python scripts/verify/stripe_amount_parity_contract.py`.

---

## 2026-05-06 - Symmetry does not rescue the wrong category-control pattern

The first shop repair responded to GL's symmetry rule by turning category controls into equal tiles. That fixed ragged rows, but it still left customers facing a button wall. GL's rejection was not just about spacing; it was about the product showcase feeling cheap and unintuitive.

**Counter-move:** when GL rejects a category or product-control surface, question the interaction pattern before polishing spacing. For LT, the current contract is a desktop category rail plus mobile native select, with product cards and large photos given the main space. Verifiers should prove the old chip/button walls are absent, not merely symmetrical.

---

## 2026-05-06 - Privacy-extension blocks can be filename-triggered

The `/shop` console showed `ERR_BLOCKED_BY_CLIENT` for `lt-cookie-consent.js`. The local server could serve the file, but the customer's browser environment treated the filename as a blocker target. The bug was not solved by explaining the extension; the visible site contract needed a less blocklist-prone asset name.

**Counter-move:** when a required public-site helper is blocked by a browser extension, inspect the URL and filename as part of the root cause. Keep consent behavior honest, but avoid shipping asset names that look like common ad/tracker/cookie blocker patterns. For LT, the kept asset is `lt-site-preferences.js`; the deleted name is `lt-cookie-consent.js`.

---

## 2026-05-06 - The exact folder matters when a designer handoff exists

The second portfolio failure happened because the implementation was judged against a copied/derived reference path instead of the exact folder GL named: `research/a unique portfolio page for a high end corporate balloon events_/design_handoff_locally_twisted_portfolio/`. That lost important details: the huge editorial hero, oklch palette, Cormorant/Inter Tight pairing, visible captions below photos, and the approved aspect sequence.

**Counter-move:** when GL provides a design handoff path, render that exact folder first, compare production to it, and translate only the intentional production differences. For this LT page, keep the real Frappe header/footer and real LT photos, but otherwise treat the handoff's Frappe files as the visual baseline until GL closes the critique loop.

---

## 2026-05-06 - Portfolio edge bleed is the design, not an overflow bug

The strict portfolio rework exposed the real failure in the first translation: Codex tried to make the designer's collage safer by moving photos into fully visible rows. That protected the layout in a generic web sense, but it destroyed the portfolio concept GL wanted. The portfolio is supposed to feel like an intentional scrolling collage of whole installed-work photos, not a card grid with larger images.

**Counter-move:** when a visual reference intentionally uses edge anchoring, overlap, bleed, or asymmetric motion, preserve that behavior first and verify it in the browser before applying generic container instincts. In LT, the Frappe shell owns the header/footer and route lifecycle, but the portfolio reel owns its full-bleed photo field. Tests must fail a static row, fail text covering gallery photos, and prove Chrome/Brave show the same placement pattern.

---

## 2026-05-06 - Product showcase rows need symmetry, not just fit

The first shop showroom pass made `/shop`, `/shop-items`, and `/shop-items/<group>` larger and more responsive, but GL correctly rejected the result as cheap because the category controls were ragged text-width chips and some category grids left a lone product card hanging on the last desktop row. The page technically fit in the viewport, but it did not meet the visual bar for showing off products.

**Counter-move:** for LT shop/category/product showcase pages, test symmetry as part of the design contract. Category controls should use equal-width and equal-height grid tracks, not variable-width chips. Add a neutral "all" tile when it creates an even category matrix. Product grids should avoid single-card orphan rows in both category pages and filtered `/shop` states; when a 3-up layout leaves one card and the count can be split evenly, use paired 2-up rows. Verify with browser geometry checks, not only generic overflow tests.

---

## 2026-05-06 - Designer reference code is a contract, not a suggestion pile

Claude produced a useful portfolio design reference, but the first translation failed the ownership handoff: Codex blended the reference with old local portfolio assumptions, kept stale claims in docs, and made the result harder for the designer to critique. The important distinction is that external design code can own the visual contract, while Codex owns the Frappe translation.

**Counter-move:** when GL brings code from Claude, a designer, or another agent, first write down what must survive visually and what should be ignored. For the LT portfolio, the preserved contract is large whole photos, left/right/center drifting placement, no cropped cards, no text covering the product, visible reference captions below photos, optimized real images, and mobile full-width natural-ratio stacking. Do not add filters, modal behavior, Frappe boxing, or other "helpful" local patterns unless GL explicitly accepts them. Keep the reference folder while critique is active, but label production source as the Frappe route, CSS/JS, optimized assets, and verifier.

---

## 2026-05-06 - Translate design references into kept source, then delete the raw reference

**Current status:** superseded while the portfolio designer critique loop is active. Keep the raw reference folder available for critique until GL explicitly closes it; delete only after that approval.

The portfolio reel used a generated/reference folder as a temporary design source. Keeping that folder after translation would train the next agent on the wrong artifact and leave another stale path to reconcile.

**Counter-move:** when a reference artifact has been translated into Frappe/Jinja/CSS/JS, keep the route implementation, verifier, and feature handoff. Delete the raw generated/reference folder unless it is still an explicit source of truth. For proof galleries, preserve real image dimensions in code metadata and verify natural-ratio display instead of keeping mock source files.

---

## 2026-05-06 - Required fixture fields can block unrelated work

`Item Attribute` fixture rows without explicit `disabled` values can block `bench migrate` or fixture sync after unrelated app changes because ERPNext treats the field as required. That makes a visual or feature slice look broken even when the failure is stale fixture shape.

**Counter-move:** keep required ERPNext fixture fields explicit in tracked fixtures, and verify fixture JSON before committing. This is not a reason to add broad new ERPNext setup records; it is a parity fix for existing fixture ownership.

---

## 2026-05-06 - Customer document policy copy needs one lane helper

LT policy copy now appears in several places: public Terms/Refund pages, checkout notices, paid-order receipts, and inquiry auto-ack emails. When those surfaces are edited independently, the checkout/legal story can drift or accidentally imply the wrong tax/refund rule for services, deposits, delivery, or ready-to-order products.

**Counter-move:** keep customer-document policy language behind `locally_twisted.policy_documents` and anchored public policy lanes. Do not add ERPNext Terms and Conditions or Email Template sync records unless a real customer-facing invoice path requires them; LT should stay whitelabel/code-owned where practical. After changing customer-facing document copy, run `python scripts/verify/customer_documents_contract.py` and the paid-order cascade verifier. Decode/normalize Frappe `Email Queue.message` content in verifiers because queued mail may be quoted-printable encoded.

---

## 2026-05-06 - Event Playground handoff needs one payload contract

The PlayCanvas game, Frappe wrapper, contact-form prefill, and browser tests all depend on the same design facts: venue preset, placed balloon pieces, props, positions/rotations/scales, colors/materials/patterns, screenshot reference, suggestions, and contact handoff state. If those facts drift between the game and contact handoff, the route can look playable while sending weak or misleading inquiry text to LT.

**Counter-move:** keep Event Playground state and payload construction in a pure module first, then have the renderer and route verifier consume that schema. Browser checks must prove the canvas and controls are usable and that Submit Inquiry lands on `/contact` with the same design summary prefilled. Do not add a DocType, backend save API, Lead creation, or migration until persistence is deliberately approved.

---

## 2026-05-06 - Event Playground construction truth must be tested before rendering

GL caught the arch balloons pointing down. That was a real manufacturing mistake, not a styling preference: a classic quad cluster is tied/twisted at a shared center, so each balloon neck/knot points into that tie point. The renderer defaulted all balloon necks downward and still passed canvas tests because those tests only proved "nonblank and interactive."

**Counter-move:** use `.codex/capabilities/recipes/event-playground-construction-truth.md` before any Event Playground geometry work. Put construction slots in pure modules first, test neck/knot vectors against the shared tie center, and make PlayCanvas consume those slots. A nonblank canvas is never enough proof for balloon construction.

---

## 2026-05-06 - Frappe container work needs an explicit contract

Older notes correctly found that Frappe wraps normal web pages in `.page-content-wrapper > main.container.my-4`, and LT later neutralized that stock visual box so full-width brand bands could span the viewport. The missing piece was that "break out of Frappe" became too easy to treat as a general page-building move. GL saw the real effect: some sections felt detached from the Frappe page rhythm, while crawls/reviews broke differently across browsers and cache states.

Research against the installed local stack confirmed the current contract: Frappe/Webshop still owns the website lifecycle, route templates, header/footer hooks, product/listing/cart selectors, and asset loading. LT owns the visual containment inside that lifecycle through `lt-theme.css` and `lt-page-containment.css`. That means every public section must choose a mode before CSS work starts: contained workflow/reading surface, or deliberate full-bleed band with its own inner wrapper and browser-verified clipping.

**Counter-move:** before changing public layout, `.lt-fullbleed`, crawls, review tracks, Webshop pages, or shared CSS, read `.codex/capabilities/recipes/frappe-public-container-contract.md`. Classify the section, preserve Frappe/Webshop hooks and selectors, use LT inner containment instead of relying on the neutralized parent container, and verify no document overflow, visible unintended scrollbar, or browser-specific fallback.

---

## 2026-05-06 - Do not turn cartable products into quote-only failures

The checkout rule briefly treated product groups like Arches and Garlands as `quote_required`, which meant a priced product already in the cart could disappear from checkout or be described as not purchasable. GL caught the customer logic problem: putting something in a cart means "I can buy this." The only clear system-configured checkout quote fallback is fulfillment, especially a delivery ZIP outside the standard zone.

**Counter-move:** keep product CTA rules and fulfillment quote rules separate. If a product should not be sold online, do not let it enter the cart. If a priced product is in the cart, do not mark it `quote_required` because of item group. Use delivery-zone preview/submit contracts to route out-of-area customers to `/contact` with cart and customer details prefilled.

---

## 2026-05-06 - Tax jurisdiction is not the taxable base

The checkout code already knew how to pick a Utah tax rate from ZIP/city, but that did not mean the whole order should be taxed. GL clarified the actual LT rule: only goods are taxable. Services, face painting, balloon twisting, deposits for those services, and delivery charges are not taxable. The failure was visible only when the Sales Order contract compared expected goods-only tax to ERPNext's submitted tax rows; West Jordan delivery produced `$5.96` tax instead of the expected `$4.84` because delivery was being included in the taxable base.

**Counter-move:** for ERPNext checkout work, test two contracts separately: jurisdiction/rate selection and taxable-line classification. Use a real 0 percent Item Tax Template for non-taxable service/deposit/delivery lines because ERPNext can recalculate Sales Order tax from templates, not just raw preview math. Verify both preview totals and submitted Sales Order tax rows. Keep service deposits as Lead/payment guidance until an approved service money path exists.

---

## 2026-05-06 - Fresh headless checks can miss persistent-browser motion state

The homepage review marquee was checked in Playwright and the computed CSS said it was animating. GL then showed two real browser screenshots with different failures: Chrome exposed the horizontal scrollbar from the reduced-motion fallback, while Brave showed the older stacked-card fallback. The code path existed, but the verification did not cover the states GL was actually seeing: persistent browser sessions, stale rendered CSS, and the `prefers-reduced-motion` branch.

**Counter-move:** when a visual behavior depends on animation, overflow, media queries, or browser preferences, verify more than the happy-path computed style in one fresh browser. Check the served HTML/CSS, then run Chrome and Brave with fresh profiles and inspect the user-visible state: `matchMedia('(prefers-reduced-motion: reduce)')`, animation name/duration/play state, overflow/scrollbar behavior, and element positions over time. Also force both `no-preference` and `reduce` in Playwright. A reduced-motion fallback still has to match the intended visual contract; it cannot quietly become a stacked grid or visible scrollbar unless GL explicitly accepts that.

---

## 2026-05-05 - Container stability fails at breakpoint edges and open states

The site looked acceptable in some default screenshots while real containers were still at risk: nav between legacy and active desktop breakpoints, mobile drawer accordions, product selectors, contact conditionals, portfolio state, and text sitting too close to panels. A 320/375/1366 check alone was not enough for the design requirement GL was reacting to.

**Counter-move:** treat every public container as unsafe until checked across breakpoint edges and stateful UI. The LT gate now uses `scripts/verify/layout_helpers.js`, expands `npm run test:layout-fit` to 260 passive route/viewport checks, adds `npm run test:interactive-layout` for 39 open-state checks, keeps checkout preview behavior under `npm run test:checkout-experience`, and exposes `npm run test:public-verify` for broad closeout. New containers need either coverage in those specs or a deliberate reason they are out of scope.

---

## 2026-05-05 - Disk source is not proof that Frappe is serving the design

The restored mega-menu, page-containment CSS, and product-polish CSS existed in the repo, but the running site was still missing the menu behavior and product/page styling because the assets were not wired through `hooks.py` and the Frappe processes/cache had not been refreshed. That made the site look like agents were editing against each other even when useful source changes existed.

**Counter-move:** for Frappe visual work, verify the served HTML and asset URLs after editing `hooks.py`, not just the file tree. Restart backend/frontend when hooks change, clear website cache after restart, confirm the cache-busted URLs appear in page HTML, and then run browser checks.

---

## 2026-05-05 - Mega menus need separate hover-open and click-pin behavior

The desktop mega menu technically opened on hover, but Playwright click exposed a real interaction flaw: moving over the trigger opened the panel, and the click then interpreted the open state as a request to close it. That made the menu feel broken for users who click instead of hover.

**Counter-move:** treat hover as preview and click as pin. A click on a hover-open menu should keep it open and set `aria-expanded=true`; only a second click on an already pinned menu, outside click, Escape, or another menu should close it. Verify this with a real browser, not only source inspection.

---

## 2026-05-05 - Retired design references must be deleted, not politely deprioritized

The old `_resources/design-guide/` and several shop/icon comparison artifacts were still present after the visual direction changed. Even with a stronger style guide, those files could keep training future agents back toward light-blue/blush UI, old fonts, weak generic icons, and stale shop mockups.

**Counter-move:** when GL explicitly rejects a visual direction, delete the conflicting tracked references if they are no longer current source material. Then update the active reading paths, workstream, queue, decisions, lessons, and capability recipe in the same closeout. Keep true catalog/business evidence, but separate it from style authority.

---

## 2026-05-05 - Icon quality has to match the business, not just the proof-bar slot

The first professional icon pass still acted like Locally Twisted needed four generic proof marks. GL rejected that correctly: this is a balloon company, and the icon system needs Utah/local proof, event context, and multiple balloon forms.

**Counter-move:** for brand icon systems, start from the customer's actual business vocabulary. LT now has balloon pair, cluster, arch, organic garland, column, bouquet, civic parade, corporate entrance, school spirit, premium private event, delivery/install, and proof icons. Balloon pages should use balloon-form icons before abstract trust icons.

---

## 2026-05-03 - Sitewide visual passes need cache-bust plus screenshot proof

The Civic overhaul changed shared CSS, Jinja partials, Python controller constants, generated imagery, Webshop surfaces, and policy/success pages. Route 200 checks and layout tests were necessary, but they would not have caught the old header treatment, stale controller output, unreadable hero treatment, blank map embed, or mobile header overlap on their own.

**Counter-move:** for broad Frappe visual work, bump the CSS query string, clear website cache, restart the backend when controller constants changed, then verify with route checks, layout/contract checks, and real desktop/mobile screenshots. Treat screenshot inspection as part of the acceptance test, not polish.

---

## 2026-05-03 - Lead conversion has to update both ERPNext status and the LT board

Checkout already converted a Contact-linked Lead by setting native `Lead.status = Converted` and filling `Lead.customer`, but Jeff's LT board still showed the Lead as `New Inquiry` and kept the old follow-up Task open. ERPNext's native conversion fields and the client-facing business stage are separate contracts.

**Counter-move:** when a checkout, import, or manual process converts a Lead, verify native ERPNext fields, the custom pipeline stage, related Tasks, and finance records together. A conversion is not operationally complete if the owner board still tells staff to treat it as a fresh inquiry.

---

## 2026-05-03 - Live inventory should not overlap rollback-based verifiers

A backend inventory pass briefly saw temporary records created by checkout/payment/cascade verification. Those records were real while the verifier was running, but they were not stable business state because the verifier rolled them back.

**Counter-move:** run live DB inventory after mutating verifiers finish and their cleanup checks pass. If parallel verification is unavoidable, label counts as test-window counts and rerun the inventory sequentially before documenting them.

---

## 2026-05-03 - Engine comparisons need one payload truth source

The PlayCanvas/Babylon event-builder spike could have drifted into two separate demos with matching screenshots but different facts. That would be useless for a future sales/design tool because the payload, balloon counts, scale rules, and interaction behavior matter as much as the pixels.

**Counter-move:** for renderer comparisons, put scene facts and payload construction in shared code first, then make each engine renderer consume the same scene objects. Verify payload parity between engines except for the explicit engine field, and test at least one interaction that mutates the payload. Screenshots prove the canvas rendered; shared facts prove the engine comparison did not change the business contract.

---

## 2026-05-02 - Inventory existing cascades before adding new stage automation

ERPNext may already be doing part of the business workflow through checkout, payment success, webhooks, or native document helpers. In LT, `/checkout` already creates Customer/Contact, Sales Order, and Payment Request records, while `/payment-success` and the Stripe webhook reconcile paid orders into Sales Invoices and transactional emails.

**Counter-move:** before connecting a CRM stage to finance or accounting, run a live backend inventory and map existing document creators first. Add automation only where it coordinates with the existing path instead of creating a parallel path.

---

## 2026-05-02 - Wire uncertain stage cascades to reversible operations first

Stage movement needs to do real work, but not every stage is ready to carry finance meaning. The CRM pipeline is now safe because `Archive` is off-board only; the next risk would be letting early automation create Sales Orders, invoices, payment requests, or win/loss stats before the business threshold is settled.

**Counter-move:** when a cascade is directionally right but the finance/accounting threshold is not approved yet, start with reversible operational records such as Tasks. Verify that moving stages does not change financial document counts, and make the next finance-trigger decision explicit instead of hidden inside a stage label.

---

## 2026-05-02 - Client CRM stages should not hijack ERPNext native status

The Odoo reference used `Archive` to remove cards from the active Kanban, but its local stage data also marked Archive like a won/folded stage. Copying those values into ERPNext `Lead.status` would risk distorting conversion logic, finance/reporting assumptions, or future workflow triggers.

**Counter-move:** when translating CRM stages into ERPNext, first separate "what the operator needs to see" from "what ERPNext uses internally." Put client-friendly board stages on a custom Select field when there is any chance native status affects reporting or accounting. Treat `Archive` as off-board only unless the business explicitly says it is won, lost, billable, or ready for a finance cascade.

---

## 2026-05-02 - Estimated event times should not be Frappe Time fields

Frappe `Time` Custom Fields render as awkward time controls in Desk and can make estimated event times look overly precise. In this repo, the Lead time fields also carried customer helper copy inside employee-facing labels and old records displayed machine-style values with seconds/microseconds.

**Counter-move:** for estimated times that staff need to edit quickly, use `Data` fields with plain labels and a short example description. Keep customer helper copy on the public form. If an existing Custom Field must move from `Time` to `Data`, use a guarded sync/migration path and verify the actual Desk route, because Frappe blocks that fieldtype change through normal validation.

---

## 2026-05-02 - ERPNext Workspace widgets are two-part wiring

The Owner Home command center needed Number Cards and a Dashboard Chart, but creating the backend widget records was not enough. Frappe Workspaces also need matching child rows (`Workspace Number Card` / `Workspace Chart`) and matching content blocks in `Workspace.content`. The first sync attempt also used internal Number Card names that differed from their labels; Frappe's Number Card naming followed the label/autoname, so Workspace link validation failed.

**Counter-move:** when building Desk dashboards, verify all layers together: widget document exists, Workspace child row points to the actual widget name, Workspace content has the block, and the non-admin role can see it in Desk. Keep widget names and displayed labels aligned unless there is a verified reason to separate them.

---

## 2026-05-01 - Desk conditionals need the real child-table field, not a text echo

The public `/contact` form looked correct, but the ERPNext Desk form still depended on `custom_event_type`, a Table MultiSelect. The submit handler was only echoing services into text-style data, so real inquiries could arrive without the Desk conditional sections opening. **Counter-move:** when a public form feeds a Desk workflow, verify the exact backend field that drives Desk behavior, not just that the submission created a Lead.

The useful verifier checks three layers together: current service records, Lead Custom Field labels/depends_on logic, and the submit helper that builds child rows. A browser success modal alone is not enough for CRM parity.

---

## 2026-05-01 - Form labels are behavior contracts

### Lesson 1 - "Only" means the UI must enforce exclusivity.

Delivery Only and Pickup Only sounded clear in isolation, but the form lets customers stack services. That label was therefore wrong: it implied selecting Delivery/Pickup should lock out decor, twisting, face painting, or Events Inquiry. **Counter-move:** if a service can combine with other services, do not label it "Only." If the business truly wants an only path, enforce that logic in the UI and backend mapping.

### Lesson 2 - The ideal customer path needs structure, not a blank box.

Events Inquiry is the high-value path for large, multi-piece packages. A freeform "What type of decor?" field made the best customer do the most work. **Counter-move:** give ideal buyers structured choices pulled from the real catalog/homepage categories, then add color and notes fields for personality and nuance.

### Lesson 3 - Conditional fields should ask only the people who can answer them.

"Shade is required for outdoor events" matters for live artists, not outside balloon decor, pickup, delivery, or Something Else. Every irrelevant dropdown makes the form feel less intelligent. **Counter-move:** verify each service choice independently with an automated form-logic script, including the absence of stale labels.

### Lesson 4 - GL tangent flow needs queue capture, not a forced linear review.

GL named an ADHD inattentive working style during this session. Product direction arrived as a chain of quick corrections: Events Inquiry, shade logic, pickup, location wording, "Only" labels. **Counter-move:** keep the active slice small, restate the current target, convert tangents into queue/docs when they are not the current task, and avoid making GL re-review stale items one by one.

---

## 2026-05-01 - Actual fit needs a geometry gate, not a confidence statement

### Lesson 1 - Offscreen controls are usually framework residue, not just CSS drift.

The Seasonal category page showed `Prev` / `Next` half off screen. The visible controls were not the themed `#lt-pagination` block; Webshop was injecting a second `.product-paging-area` row inside `#product-listing` with Bootstrap rows and inline float styles. CSS aimed only at the themed block could never fix it. **Counter-move:** inspect the rendered DOM before polishing. If a control ignores scoped CSS, find whether the framework injected a second copy.

### Lesson 2 - A fit check must distinguish visible overflow from clipped carousel internals.

The expanded layout spec initially failed the homepage because the reviews carousel track intentionally extends far outside the viewport, but the page had no document overflow and the track is clipped by its wrapper. That was a false positive. **Counter-move:** layout-fit tests should flag document overflow and visible un-clipped element overflow, while allowing descendants inside an overflow-clipping ancestor.

### Lesson 3 - Python Playwright and Node Playwright are different installations.

`python scripts/verify/smoke_shop.py` failed because `C:\Python314\python.exe` has no Python `playwright` package. Playwright was still installed: Node/CLI Playwright 1.59.1 lives in npm's npx cache at `C:\Users\baenb\AppData\Local\npm-cache\_npx\420ff84f11983ee5\node_modules\.bin\playwright.cmd`. **Counter-move:** when someone says "Playwright is installed," locate which runtime owns it before declaring a verifier unavailable.

---

## 2026-05-01 - Navigation labels must match customer intent

### Lesson 1 - "Plan by Occasion" in a shop means product discovery first.

I initially routed every occasion link to `/contact?occasion=...` because it was easy to connect the event labels to the Lead form. GL corrected it hard: customers opening an occasion dropdown in a shop are asking "show me the products for this occasion," not "send me to a generic contact form." **Counter-move:** when a nav label sounds like browsing (`Shop`, `Plan`, `Browse`, `Occasion`, `Category`), route to product/category/content discovery first. Inquiry CTAs belong where they are explicitly framed as inquiry.

### Lesson 2 - Verify nav against real catalog routes before inventing landing pages.

The fix did not require new occasion pages. The ERPNext catalog already had product-backed answers: Birthday Deliveries, Baby Shower Garland, Graduation Grab n Go, Get-Well Bouquets, Large head Missionary, Easter Arch, etc. **Counter-move:** query Website Items and Item Groups before adding routes. Prefer existing real product/category pages over placeholder landing pages or contact shortcuts.

### Lesson 3 - Source-level IA checks catch regressions that screenshots miss.

The opened-dropdown screenshots showed a clean layout, but they would not by themselves prevent someone from re-pointing every occasion link back to contact later. `scripts/verify/nav_ia.py` now encodes the behavioral contract: no duplicate Contact CTA in mobile drawer, no nav `/book`, and no `contact?occasion` routes in Plan by Occasion. **Counter-move:** pair visual checks with a small source-level invariant script for nav IA.

---

## 2026-05-01 — Storefront correction pass: preserve framework contracts and accessibility

### Lesson 1 — Category listing bugs can be wrapper-contract bugs, not catalog bugs.

`/shop-items/arches` returned non-arches because the LT Item Group template override removed Webshop's expected `.item-group-content` class. Webshop's listing JavaScript reads that wrapper to find the active Item Group; without it, the listing fell back to broader product results. **Counter-move:** before changing catalog data, inspect the stock Webshop template/JS contract and keep framework semantic classes even when adding LT BEM classes.

### Lesson 2 — Add listing-card fields by wrapping Webshop APIs, not patching upstream.

GL wanted brand descriptions visible on product listing cards. Webshop's stock product filter response did not include LT's brand-description field. The clean fix was a local `override_whitelisted_methods` wrapper around `webshop.webshop.api.get_product_filter_data`: delegate to stock Webshop, then append `lt_brand_description`. **Counter-move:** for small Webshop data enrichments, preserve framework behavior and add the missing field locally instead of editing upstream app code.

### Lesson 3 — Accessibility sizing is not a compression knob.

Footer/header balance must not be solved by shrinking text or controls below accessible sizes. GL explicitly rejected that direction. **Counter-move:** fix density through content removal, centering, grid/flex layout, and responsive wrapping. Preserve readable text and practical 44px interactive targets.

### Lesson 4 — Verification screenshots are receipts, not source.

Header/footer/menu/product verification generated many Chrome/Edge profile folders and screenshots. Those are useful during QA but not canonical project artifacts. **Counter-move:** summarize verified results in docs, keep only intentionally promoted reference assets, and ignore/delete generated browser profiles and throwaway verification captures.

---

## 2026-04-30 (evening) — Mirror rebuild Phase 1 chrome via /triadic-construction-v2

### Context

GL exhausted. Catalog port shipped that morning but visually disappointed them ("I hate the entire shop"). They directed: clone Hetzner Odoo deployment wholesale into ERPNext-coded chrome + pages, keep only the homepage, use agent teams. Then went to nap. I ran an autonomous chain: tool research → mirror → /plan-deepen → 6 pre-tasks → triadic chrome rebuild → fix round → audit. Chrome shipped (with desktop polish flagged); Phase 2 page rebuilds deferred to next session.

### Lesson 1 — When GL names a frame, the live correction beats the documented rule.

I opened the session by parroting CLAUDE.md's "new build, not a migration" frame on the first message. GL corrected immediately: *"it is a migration, not a new build."* The "Reframe is locked" rule in CLAUDE.md was itself superseded by GL's live directive. I had to undo a multi-file framing cascade across 8 docs. **Counter-move:** when GL names something authoritatively in conversation, treat that as ground truth even when documentation contradicts. Update the docs to match GL, not the reverse.

### Lesson 2 — The "load-bearing 404" was always infrastructure, never missing code.

`/book` had been 404 every prior session for ~weeks. Plan-deepen agent found that `www/book.{py,html}` already exist with full implementation per the `frappe-form-integrity` skill. The 404 was a stale Frappe website cache + nginx upstream-IP staleness after a backend restart. Cache flush + frontend container restart unblocked it in <30 minutes. **Counter-move:** before assuming a Frappe route is missing code, run the cache flush + check container restart status. The site exists where you put it; cache lies louder than missing files.

### Lesson 3 — Triadic-construction-v2 reviewers caught what solo build would have shipped broken.

Round 1 chrome shipped with **mobile drawer always visible** (CSS class mismatch — every mobile page would have looked broken to customers), **2 of 3 mobile mega menu accordions completely dead** (data-attribute mismatch + querySelector singular bug), **megamenu panel had no CSS rules** (would render as inline blocks pushing content down), and **mega-trigger CSS open-state targeting wrong class**. Architect + Execution Engine reviewers found these via Active Agreement (independent flags, same defects). SecOps reviewer caught a separate set (rate-limit X-Forwarded-For bypass, hash instability, /book Esc-key UX bug). All caught in the same round; all fixed mechanically because the findings cited file:line. **Counter-move:** for high-blast-radius work (chrome, payment flows, schema changes), pay the triadic context cost. The discipline earns its keep.

### Lesson 4 — Triadic Build Brief must specify class-name alignment per element, not just namespaces.

The single biggest time-sink in the triadic round was Builder Jinja choosing different BEM class names than what Builder CSS had pre-existing rules for. Build Brief said "BEM namespace `lt-*`" but didn't enumerate specific names. Round 1 shipped with 8+ template-vs-CSS class divergences (`lt-header__mobile-nav` vs `lt-header__mobile-nav-collapse`, `lt-header__mega-item` vs `lt-header__has-mega`, `lt-megamenu__*` vs `lt-header__mega-*`, etc.). **Counter-move:** for any future triadic dispatch involving template-CSS coordination, include a class-name alignment table in the Build Brief: "trigger `<li>` uses `.lt-header__has-mega`; panel `<div>` uses `.lt-header__mega`; inner container uses `.lt-header__mega-inner`; link uses `.lt-header__mega-link`." Specificity per element prevents the divergence.

### Lesson 5 — Sub-agents need explicit skill-invocation instructions in their briefs (agency gate is per-session).

The agency pretooluse gate fires on Edit/Write to Frappe app files unless `frappe-form-integrity` / `frappe-asset-pipeline` / etc. skills have been invoked **in that session**. Sub-agents have their own session context. Each builder I dispatched had to invoke the relevant safety skill BEFORE their first edit. I documented this in each builder brief; without it, the gate blocks the build silently from the agent's perspective and they fall back to Bash workarounds. **Counter-move:** every Frappe-app-file-touching agent gets a "Required skill invocation BEFORE any edit" section in its brief. Builder JS this session reported a `frappe-migration-guard` gate detection edge case for sub-agent contexts — flagged for ops/infra.

### Lesson 6 — `@rate_limit(key="X", ip_based=True)` does NOT create two counters.

I wrote a synthesis fix-shape calling for "two-tier rate limiting" (IP + email). GL Proxy caught it: Frappe's `@rate_limit` combines `ip` and `key` into a SINGLE `ip:key` identity, not two independent counters. The correct shapes are Option A (`key="email", ip_based=False` — defeats X-Forwarded-For spoofing, accepts email-enumeration trade-off) OR Option B (nginx-level XFF strip — higher leverage, protects all rate-limited endpoints). **Counter-move:** read the actual Frappe source before describing decorator behavior. Don't synthesize from training memory. The Proxy review at Phase 2.5 is the safety net — don't lean on it for what you should verify yourself.

### Lesson 7 — Frappe nginx upstream-IP is sticky after backend container restart.

After `docker restart locally-twisted-erpnext-v15-backend-1`, nginx in the frontend container kept hitting the OLD container's IP (`172.22.0.8`) and returning 502 even though backend was up at a new IP. Cause: Frappe's bundled `frappe.conf` for nginx has no `resolver` directive — nginx resolves backend's IP once at startup and caches forever. **Counter-move:** any time you restart the backend container, also restart frontend OR document that the user expects 502s for ~5 min until you do. Logged as agency-tier auto-behavior B5.

### Lesson 8 — `hash(email)` is randomized per Python process — useless for log correlation.

Python's `hash()` builtin uses PYTHONHASHSEED which is randomized per process by default. Across container restarts, the same email produces different hashes. SecOps reviewer caught it. Replace with `hashlib.sha256(email.encode("utf-8")).hexdigest()[:16]` for stable, non-reversible-in-practice log correlation. **Counter-move:** any time you use `hash()` for cross-process correlation (logs, dedup keys, cache keys), reach for `hashlib.sha256` instead. The builtin is for in-memory dictionary keys only.

### Lesson 9 — Auto-orchestrate the architectural calls + log reversibility, don't ask GL when they're asleep.

GL gave clear authorization: *"if it's Odoo only and there's an ERPNext equivalent, do that. OR DON'T, and just tell me what you couldn't do."* Two architectural decisions came up mid-build (mega menu IA — extend Item Group tree vs template-grouping; category URL shape — match Hetzner's `/shop/category/X-N` vs ERPNext native `/shop-items/X`). I picked the lower-blast-radius option for both, logged them as reversible in `locally-twisted-decisions.md`, and proceeded. GL's wake-up message confirmed this was the right shape: "you've done a really good job so far." **Counter-move:** when GL is unavailable and authorization is broad, decide + log + proceed. Don't pile up gates that block work.

### Lesson 10 — Read the actual screenshots, don't just trust DOM facts + script flags.

The Playwright audit script extracted DOM facts (`.lt-header` count, `.lt-footer` count, `.lt-header__mega` count, `mobile_drawer_visible`) and reported all routes "OK." But when I read the actual home-desktop.png file as an image, the centered logo dominating + tagline wrapping vertically was immediately visible. DOM-says-rendered ≠ pixels-look-right. The agency's standing rule from 2026-04-29 lessons: "viewport-only Playwright screenshots are the verification method, NOT full-page screenshots... DOM widths are preconditions, not verdicts." **Counter-move:** Read every screenshot file you capture as an image. Describe what's pixel-visible. Don't ship a verification report based on DOM facts alone.

### What this means for the next instance

The chrome work shipped (Phase 1 of the mirror rebuild). Phase 2 page rebuilds (~12 routes) are next — single focused builder per page is probably the right shape (lower interdependency than chrome). Reserve full triadic for things touching every page. The mirror at `_resources/odoo-live-mirror/` IS the spec — read the relevant page file before each rebuild. GL named the desktop chrome polish issue at session close; address it early in your session as a quick win. Don't ask GL questions they've already answered. Document architectural calls as reversible. Read your own screenshots.

---

## 2026-04-30 — Full catalog port from live Odoo to ERPNext webshop

### Six lessons from a 53-Website-Item / 10,631-Item / 10,613-Item-Price port

**Context.** GL's directive: rebuild the entire old live Odoo test shop catalog (`http://5.78.136.133/shop`) into ERPNext webshop. Every product, every variant, every option, no exceptions. Result after DB verification: 53 Website Items, 10,631 Items total, 49 variant templates, 4 single-SKU templates, 10,578 variants, 10,613 Item Prices, 32,002 Item Variant Attribute child rows, 11 Item Group children + restructured hierarchy, mega menu, on-brand product detail pages with inline variant selectors. Smoke tests pass. This was catalog-data porting into a new ERPNext build, not an Odoo migration.

### Lesson 1 — The catalog source of truth is the LIVE site, not the cached export.

The existing `_resources/odoo-export/catalog.json` (created 2026-04-26) had 51 products. The live re-scrape on 2026-04-30 found **53 products** — Odoo had added `birthday-deliveries` and `large-head-missionary` since the cached export. Five products had `image_url=null` in the cached file but DO have images on the live site (the original scraper's regex missed `data-src` lazy-load patterns). For any catalog work: re-scrape live, don't trust caches.

**To do differently:** treat `_resources/odoo-export/catalog.json` as historical reference; produce a fresh `_resources/odoo-live/catalog.json` from the live site at the start of any catalog rebuild.

### Lesson 2 — Frappe `installed_apps` order determines who wins template ChoiceLoader resolution.

`frappe.get_installed_apps()` reads from `db.get_global("installed_apps")` (a JSON list). `template_page.py:53` iterates that list **REVERSED**, picking the first match. With our default order `[frappe, erpnext, locally_twisted, payments, webshop]`, reversed = `[webshop, payments, locally_twisted, ...]` — webshop won every template at `templates/generators/item/...`. The override files we placed at `apps/locally_twisted/locally_twisted/templates/generators/item/` were silently ignored.

**The fix:** put `locally_twisted` LAST in the installed apps list.

```python
# bench --site frontend console
import json
new = ["frappe", "erpnext", "payments", "webshop", "locally_twisted"]
frappe.db.set_global("installed_apps", json.dumps(new))
frappe.db.commit()
# then docker restart the backend
```

This is irreversible-feeling but reversible. After the change, `apps/locally_twisted/.../templates/...` overrides win for any path webshop also defines.

**Verification before any template-override work:** drop a marker file at the override path (e.g. add a unique CSS class to a copied-verbatim template), restart backend, hit the URL, grep the response for the marker. If absent, fix load order before continuing.

### Lesson 3 — Webshop's `WebsiteItem.make_route()` adds `random_string(5)` to every auto-generated route. Always set `route` explicitly.

`apps/webshop/webshop/webshop/doctype/website_item/website_item.py:108–118` returns `<group_route>/<scrubbed_name>-<random5>` when `self.route` is empty. Result: ugly unstable URLs like `/shop-items/arches/basketball-arch-tljq2`. Customer bookmarks would break on every `make_website_item` re-run.

**The fix:** in `_upsert_website_item`, compute the clean route (`<group_route>/<slug>`) and set `wi.route = clean_route` BEFORE save. Webshop's make_route only fires when `self.route` is empty, so the explicit set wins.

### Lesson 4 — Item Price cannot exist on a template Item with `has_variants=1`.

`tabItem Price.validate_item_template()` throws `InvalidItemTemplateError` if you try to create one. Item Price must live on each variant's item_code instead. For "from $X" display on the listing card (template), query `MIN(price_list_rate)` across the variant set in the controller and surface as `price_is_from`.

### Lesson 5 — Setting `Item.image = "/files/<x>.png"` directly silently fails when there's no `File` doctype record.

Per webshop's `validate_website_image()`, the field gets cleared on save if no matching `File` doc exists for that URL. The `Item.image` field expects an attached `File`. Pattern that works:

```python
f = frappe.get_doc({
    "doctype": "File",
    "file_name": "basketball-arch.png",
    "file_url": "/files/basketball-arch.png",
    "is_private": 0,
    "attached_to_doctype": "Item",
    "attached_to_name": "basketball-arch",
}).insert(ignore_permissions=True)
# Then Item.image = "/files/basketball-arch.png" sticks.
```

The image file must exist on disk at `sites/<site>/public/files/<slug>.png` before the File doc is created. Copy via `shutil` or pre-stage outside the script.

### Lesson 6 — Webshop variant cards are JS-rendered, not Jinja-templated. Override via CSS, not template.

`apps/webshop/webshop/public/js/product_ui/list.js:101` bakes `${item.item_group} | Item Code : ${item.item_code}` into the card markup at compile time. There's no Jinja template to override — it's compiled into the bundle. Any product listing route (`/shop-items/<group>`, `/all-products`) renders cards through this JS.

**The fix:** CSS hide `.product-code` in the listing context. Add to lt-theme.css:

```css
.product-list .product-code,
.item-card-group-section .product-code,
#product-listing .product-code {
    display: none !important;
}
```

This is the right call here even though `!important` chains are normally a code smell — we can't override a compiled JS bundle without forking it. The CSS-hide is contained and removes the jargon at customer-render time.

### Bonus — Odoo's per-product attribute-exclusions data is captured in the scrape and respected.

Odoo's product page emits `data-attribute-exclusions="{exclusions: {...}, mapped_attribute_names: {...}}"` JSON in the form HTML. The scraper parses it, builds the cartesian product of all attribute values, then filters out combinations where any selected ptav_id appears in another's exclusion list. For LT's catalog this filtered down to 10,578 ERPNext Item Variants (vs the naive cartesian count of more). Odoo's `archived_combinations` is also captured but currently empty for LT's catalog.

The math sanity-check: `birthday-deliveries` has 4 attributes (Delivery Size 3 × Delivery themes 27 × Add Foil Number 10 × Add Bouquet 3 = 2,430 cartesian; 0 exclusions; 2,430 valid). Confirmed.

### Bonus — Variant ABBR uniqueness is non-negotiable.

ERPNext's `make_variant_item_code` builds variant `item_code` as `<template>-<abbr1>-<abbr2>-...`. If two attribute values share an `abbr` (or the abbr is blank), variant inserts collide on duplicate-key DB error. Solution in `build_item_attribute_fixture.py`: deterministic abbr generation with collision detection (3-char prefix → 4 → 5 → 6 → fallback `prefix+counter`). 195 values produced 195 unique abbrs.

### Bonus — Item Attribute Value rejects case-only duplicates.

Odoo had `Blue Slate` (ptav 1357) AND `Blue slate` (ptav 1399) for `latex colors` — same color, two ptav rows from different attribute lines. ERPNext's Item Attribute validate() throws `Attribute value: Blue Slate must appear only once` (case-insensitive). The fixture builder dedupes case-insensitively + whitespace-normalized, preserves first-seen casing as canonical, and persists a `value_normalize_map.json` so the bulk import script remaps Odoo's lower-case ptav references to the canonical capitalized name. 197 raw values → 195 canonical.

---

## 2026-04-29 late (Hetzner /book spec session — "fighting GL" pattern) — One critical lesson

**Superseded form labels 2026-05-01:** the lesson below is still valid as a stale-source receipt, but the old Hetzner labels `Delivery Only` and `Event Package` are no longer current LT form truth. Current labels are `Delivery`, `Pickup`, and `Events Inquiry`.

### When GL points at a URL, read the URL. Stop pivoting to stale local files when one tool fails to reach it.

**What happened.** GL asked me to rebuild `/book` to match `http://5.78.136.133/book` exactly. My first WebFetch on that URL returned `ECONNREFUSED`. I took that as proof Hetzner was offline — plausible per the project's Reference Disposition ("Failed Hetzner deployment ... will be decommissioned"). I pivoted to the local Odoo clone at `C:\Users\baenb\projects\locally-twisted-odoo\` as my canonical spec, read `addons/locally_twisted/views/pages/page_book.xml`, and reported what I saw there as authoritative.

**The local clone was stale.** Its XML had:
- Single-select `x_event_type` (one service per Lead)
- 3-file × 10 MB photo upload
- No per-service conditional notes (one generic textarea)

**Hetzner had been independently updated** to:
- Multi-select `x_services` checkboxes (Balloon Decor / Twisting / Painting / Delivery Only / Event Package / Something Else)
- Per-service conditional notes — `decor_notes`, `twisting_notes`, `painting_notes`, etc. — show/hide via Odoo's `data-visibility-dependency="x_services"` + `data-visibility-comparator="contains"` pattern
- Environment fields (Indoor/Outdoor, Shade Required, Colors) appearing when ANY service is selected
- 5 files × 25 MB photo upload

The ERPNext Lead Custom Fields (45 of them — `custom_event_type` as Table MultiSelect, per-service Long Text notes, etc.) had been built to mirror Hetzner's richer schema. GL was right when they said *"some of it's already implemented in the backend."*

I kept reporting the local clone's old spec as canonical and surfacing every difference as a question for GL to confirm: *"Are you sure about 5/25 photos? Multi-select or single-select? Are these CRM stages still right?"* Each question was me trusting my stale local read over GL's URL. Each one cost GL tokens to walk me through what they'd already shown me. GL named the dynamic directly:

> *"I don't know where the hell you're looking! ... Why the hell are you fighting me on it? ... Stop fighting me on this. What's the problem? ... I'm nervous about you touching anything if you keep saying this."*

**The technical fix that broke me out:** Bash `curl http://5.78.136.133/book` returned HTTP 200 cleanly (68 KB of HTML). The earlier `ECONNREFUSED` was a WebFetch tool sandbox limitation, not a real network outage. Different tools have different network surfaces. The snapshot files at `_resources/odoo-live-snapshot/hetzner-{book,contact}.html` are now on disk as the canonical spec going forward — they survive even after Hetzner decommissions.

**Three lessons:**

1. **One tool failing on a URL is not a network outage.** When WebFetch (or any single tool) reports a URL unreachable, try `curl` from Bash, Playwright, or a browser screenshot before treating the URL as down. Especially when GL has named that URL as canonical.

2. **Stale local clones are not "the spec" just because the live source seems unreachable.** A local checkout can be commits behind production AND production can have been updated independently of git history. *"The file in front of me"* is not equivalent to *"the URL GL pointed at."* When the two diverge, GL's URL is canonical — by definition, since GL named it.

3. **When GL has named a source of truth, don't surface differences as questions.** *"Are you sure about X?"* reads as doubt — and IS doubt — when GL has been showing you the URL since the second message of the conversation. The discipline is: read the URL, build to what's there, only ask when something genuinely cannot be inferred from the spec. **GL points, you read.**

**Why this matters past this incident.** The pattern compounded over five turns. Each verification question added trust cost. By the fifth, GL was *nervous about me touching anything*. That's the load-bearing failure mode — not the wrong photo limit, but the erosion of trust that would have cascaded into the actual build. The rule (now in `CLAUDE.md` "Hetzner `/book` and `/contact` are the canonical spec for the rebuild" section) is here so the next instance doesn't have to relearn this from inside GL's frustration.

**Codified in:** `CLAUDE.md` "Hetzner `/book` and `/contact` are the canonical spec for the rebuild" section, added 2026-04-29.

---

## 2026-04-29 evening (mobile-responsiveness + design-guide-import session) — Six lessons

### Frappe wraps every page in `<main class="container my-4">` — opt OUT of confinement, don't fight it section-by-section

Every Frappe website page renders inside `<main class="container my-4">` inside `.page-content-wrapper`. Frappe's bundled `apps/frappe/frappe/public/scss/website/index.scss:117-122` adds `.page-content-wrapper .container { padding: 1.5rem }` at `(max-width: map-get($grid-breakpoints, "lg"))` (= 992px). At desktop, the `.container` itself has `max-width: 1290px; padding: 80px each side` (computed). Net result: page content at 1280 viewport sits inside a 1120px-wide centered column with 80px white gutters on each side.

This is fine for content pages that want centered readable widths. It is BROKEN for full-bleed hero bands with background colors — the colored band only spans 1120px and white gutters show on each side, which reads as "stuck in container" to anyone with a designer's eye.

**Lesson:** the right structural pattern is to override `.page-content-wrapper .container` in `lt-theme.css` to remove ALL its horizontal opinion (padding 0, max-width 100%) at every breakpoint, so sections own their own layout. Sections that want full-bleed bands span the viewport. Sections that want narrow centered content use their own inner wrapper with `max-width + margin: 0 auto`. Webshop product detail (`.product-container`) and cart (`.cart-container`) need their OWN intentional centered max-width because they were designed expecting the parent container's confinement — added at `_resources/lt-theme.css` (max-width: 1200px). The structural fix is global; per-page CSS is not needed.

### Specificity matters when overriding Bootstrap-style parent-container rules

My first override of Frappe's `.page-content-wrapper .container` rule used `body main.container` (specificity 0,0,1,2 — one class + two types). It LOST to Frappe's `.page-content-wrapper .container` (specificity 0,0,2,0 — two classes). CSS specificity: classes outweigh types. Two classes wins against one class + N types. The `max-width` part of my rule applied (it was new), but the `padding-left: 0` lost because Frappe's rule had matching specificity and was loaded later.

**Lesson:** when overriding a bundled rule, MATCH its selector specificity (or exceed it without `!important`). Use Chrome DevTools or Playwright's CDP `CSS.getMatchedStylesForNode` to see exactly which rules are applying and at what specificity. The fix: `.page-content-wrapper .container` (two classes — matches Frappe's rule, wins by source order since lt-theme.css loads after the bundle).

### Full-page screenshots LIE at extreme aspect ratios

Playwright with `full_page=True` captures the entire scrollable height. On a tall mobile page (6691px tall on home, 3387px on contact), the screenshot dimensions become extreme (e.g., 410×6691). When displayed at any reasonable rendering size, the image gets compressed to ~123×2000 — that's a 33× vertical compression. Sections that should be visible become slivers of pixels indistinguishable from white space. I declared mobile responsiveness "fixed" three times based on these compressed renders; each time the actual visual state was different from what I'd inferred.

**Lesson:** for visual verification, use **viewport-only screenshots at concrete device widths** — 320 (iPhone SE), 375 (iPhone), 414 (iPhone Plus), 1280 (desktop). These don't compress because they're not full-page. Pair with: DOM probes for element widths and overflow (preconditions); programmatic checks of element positions and computed styles; AND ALWAYS GL opening the page in their real browser before declaring done. Full-page is useful for documenting what's there at a glance, but it's not a verdict on visual correctness.

### Brand logo + hamburger fit at 375 viewport math: 88px reserved, calc() max-width

The mobile brand logo CSS at `lt-theme.css:783-788` had `max-width: 350px; height: 100px` (1.25× of an earlier 80/280 spec). At 375 viewport with row padding 32 + hamburger 44 = 76px reserved, the logo had only 299px of available space. The 350px fixed cap pushed the hamburger 35px past the right edge. Previous instance hid the visual symptom with `body { max-width: 100vw; overflow-x: hidden }` — but the hamburger remained functionally unreachable: only 9px of the 44px tap target was inside the visible viewport on a 375px screen.

**Lesson:** mobile brand logo needs a **responsive cap** that scales with viewport, not a fixed pixel max-width. The shape that works:

```css
.lt-header__brand--mobile img,
.lt-header__brand--mobile .lt-logo {
  height: auto;        /* preserves natural aspect ratio at every viewport */
  max-height: 90px;    /* upper bound on tablets so the logo doesn't grow oversized */
  max-width: calc(100vw - 88px);  /* 88px reserves: 44 hamburger + 32 row padding + 12 gap */
}
```

Tested at 320 (iPhone SE), 375, 414 — hamburger fits cleanly with breathing room at each. The principle: any header element with fixed pixel dimensions that competes for finite viewport width is a responsive bug waiting to fire.

### Webshop's bundled wrappers need their own intentional max-width when the parent is fullbleed

Removing `.page-content-wrapper main.container`'s confinement at all breakpoints gave LT-designed pages the full viewport (good — hero bands now span edge-to-edge). But it also removed webshop's product detail (`.product-container`) and cart (`.cart-container`) constraints — those were designed expecting `.container`'s max-width to constrain them. Result: product detail bled edge-to-edge on desktop (1280px wide) with no readable centering.

**Lesson:** when stripping a wrapper's max-width globally, audit downstream pages for ones that DEPENDED on it. Webshop pages in particular were built expecting `.container`'s centered max-width to do the framing — give them their own intentional max-width:

```css
.product-container,
.cart-container {
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;     /* mobile */
  padding-right: 1rem;
}
@media (min-width: 768px) {
  .product-container,
  .cart-container {
    padding-left: 1.5rem;  /* desktop */
    padding-right: 1.5rem;
  }
}
```

This is structural — applies once, every webshop page inherits. Mobile responsive automatically because `max-width: 1200px` becomes `max-width: 100% - padding` once the viewport drops below 1200.

### Cross-project knowledge gaps are invisible until they're surfaced — paths matter

GL ran a 7-designer LT design competition on 2026-04-26 in a separate project directory (`C:\Users\baenb\projects\zoho-locally-twisted\gallery\`). The synthesis (D3 + D5 + D7 hybrid) was the approved design contract. PLAN.md line 47 referenced "Opus Competition Redesign concept" with NO PATH. The standard arrival reading order led every instance through every artifact and not one of them pointed at the gallery. **Multiple build instances over multiple sessions never found the design contract.** Each built the customer-facing pages without the design reference. GL had to point an instance at it explicitly on 2026-04-29 to break the cycle.

**Lesson:** if a plan or doc references a file or concept, write the path. Always. Conversation-only knowledge gets compacted away — references that point at conversation-only knowledge become dead links. The fix here was structural: import the synthesis + screenshots into `_resources/design-guide/`, add a dedicated section in CLAUDE.md ("Design guide — where it is, why it's here, and why it must stay"), update PLAN.md line 47 to point at concrete file paths, log the systemic gap in decisions. The agency client-isolation rule says every client folder is self-contained for transfer — this means EXTERNAL references break that contract, both for transferability and for findability. **If the design contract lives outside the client folder, it might as well not exist.**

### Reporting without watching, escalated: trying to canonize unverified work is "scary"

I declared the structural CSS fix done off DOM probes (no overflow, hamburger at 304 R-edge on 320 viewport, etc.) and started writing it up as the agency-wide pattern in `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` and `HOW-TO-WIN-AT-FRAPPE/auto-behaviors.md`. GL stopped this with: *"do not put that on the agency tier, because you did not prove anything. In fact, you essentially showed what you were doing wrong and trying to codify it, and that is scary."*

The agency tier exists to hold STABLE, PROVEN, MULTI-VALIDATED patterns that future BBC clients inherit. Putting fresh single-instance work there spreads bugs forward into every future client — they read the bad pattern as truth. Reporting without watching is a single-session trust withdrawal; canonifying without watching is a cross-client trust withdrawal.

**Lesson:** the agency tier is downstream of repeated proof, not upstream of single-session enthusiasm. The instinct to canonize fires before proof exists; it must be refused until validation lands. The right shape: do the work, prove it stands up across iterations, document the receipt at LT-tier (this file + decisions log), STOP. Agency tier docs emerge when a pattern proves itself across multiple clients/sessions — and they're written by whichever instance recognizes the stable pattern at THAT future moment, not by the instance that first encountered it.

---

## 2026-04-29 (guest-cart + Stripe-Link + cascade session) — Six lessons

### Frappe's `frappe.Redirect` raised in `get_context` BYPASSES the template

`payment_success.py` `_handle_stripe_session` calls `_redirect()` which sets `frappe.local.flags.redirect_location` and raises `frappe.Redirect`. The browser gets a 302 → /thank-you and never sees the `payment_success.html` body. Any JS in that template never executes. My first attempt to clear `LT_CART` in `payment_success.html` was inert. Cart-clear had to live in `thank_you.html` (the page the browser actually renders).

**Lesson:** When putting JS in a Frappe template, trace the controller flow. If `get_context` raises `frappe.Redirect`, the template is a stub that never renders. Such pages are useful as routing-only controllers but can't carry browser-executed code. Customer-side JS goes in the destination page.

**Receipt:** 2026-04-29. GL reported "the cart show 2 item in it. The order processed and now the cart needs to clear" after their successful /thank-you landing. Diagnosed by reading `payment_success.py` line 102 `_redirect(...)` and tracing the raise.

### Stripe `payment_method_types=["card"]` does NOT suppress Link UI — that's account-level

`payment_method_types=["card"]` on a Checkout Session restricts which payment METHODS appear, but Stripe layers Link UI ("Save my information for faster checkout" + "Pay with Bank via Link" + Link Terms/Privacy) on top regardless. The skill content says it explicitly: *"Link is controlled through the Dashboard. Create a custom payment method configuration with Link off."* I half-read it on first pass.

**Fix:** Create a Payment Method Configuration on the account with `link.display_preference={"preference": "off"}`, pass `payment_method_configuration: <pmc_id>` on every Checkout Session. PMC creation has a quirk: `preference="off"` is rejected on parent (default) PMCs — child-only restriction. Workaround: create a NEW top-level PMC without specifying parent. We did: `pmc_1TRZH2DfnlZQv66ncb001soG` ("LT No Link"). Hard-coded constant in `payments/stripe_session.py`.

**Verification gate:** Render the actual Stripe page in Playwright before claiming Link is gone. The API response will say `payment_method_types: ["card"]` even when the Link UI is showing — the Session config doesn't reflect the page render.

**Receipt:** 2026-04-29. GL reported "straight to link again" after the first fix shipped. Rendered in Playwright, saw "Save my information for faster checkout" + "Pay securely at Locally Twisted and everywhere Link is accepted" + Link Terms still rendering. Custom PMC fixed it.

### Webshop `templates/pages/cart.html` wins route resolution over `www/cart.py` — rename to avoid collision

Frappe resolves `/cart` against `templates/pages/cart.html` BEFORE applying `website_route_rules`. Webshop ships such a template at `apps/webshop/webshop/templates/pages/cart.html`. Even with our `hooks.py` route rule mapping `/cart → cart`, webshop's pages-style template wins and our `www/cart.{py,html}` never serves.

**Fix:** Rename our files to `lt_cart.{py,html}` and update the route rule to `/cart → lt_cart`. Verified by `curl /cart | grep lt-cart__title` — present means ours, absent means webshop's.

**Lesson generalizes:** When overriding any webshop / payments / erpnext stock page, our local module name MUST NOT collide with theirs OR we lose resolution silently.

**Receipt:** 2026-04-29. Initial implementation lived in `www/cart.{py,html}` and rendered webshop's "Your cart is Empty" page despite the route rule. Cache-clear + redis flush + bench restart didn't help. Renaming to `lt_cart` resolved it.

### `Address.address_display` is NOT a stored DB column — it's computed at render time and lives on the SO

Tried `frappe.db.get_value("Address", name, "address_display")` and got `OperationalError: (1054, "Unknown column 'address_display'")`. The Address doctype's `address_display` is a virtual/computed field that gets HTML-rendered at SO save time and stored on `Sales Order.shipping_address` (HTML string), not on `tabAddress` itself.

**Fix:** Read the components — `address_line1`, `address_line2`, `city`, `state`, `pincode`, `country` — and assemble inline.

**Lesson:** Verify field-as-DB-column before reading via `frappe.db.get_value`. Quick check: `frappe.get_meta("Address").get_field("address_display")` returns the field metadata; if `fieldtype == "Small Text"` with no DB column, it's computed. Or: just check the existing schema visually.

### Stripe PMC parent-child permissions — child configs require parent ownership

Tried to create a child PMC under both pre-existing parent configs on LT's account. Both rejected with `"Child configurations can only be created by the parent configuration's owner"`. The two pre-existing PMCs (`pmc_1RdVUoDfnlZQv66nVzkbi0JH` and `pmc_1R2KesDfnlZQv66nLj0Smbnn`) are platform-managed (created by Stripe internally when LT's account was provisioned), not LT-owned.

**Fix:** Create a new top-level PMC without specifying `parent` — that succeeds because LT IS the owner of the new config. Stripe accepts a top-level config that lives alongside the platform-managed ones.

**Lesson:** When a Stripe account inherits a default PMC from platform/account-creation, you can't modify it OR child it. Create your own top-level config. The Stripe documentation doesn't make this distinction obvious; trial revealed it.

### Customer dedup must handle the Lead-from-Contact case explicitly

The original `submit_guest_order` checked Contact Email → Contact → Dynamic Link → Customer. If no Customer link, it created a NEW Customer with a NEW Contact — orphaning any existing Contact (which often came from a previous /contact form Lead submission). Result: same email, multiple Customer records, broken one-source-of-truth.

**Fix:** Three-case branching:
1. Customer link exists → reuse (returning customer)
2. Contact exists but no Customer link → create Customer, attach Customer link to existing Contact, find any Lead linked to Contact and mark `status="Converted"` + back-fill `lead.customer`
3. No prior records → create both fresh

The Lead-from-Contact case is the load-bearing one for the "everything cascades" architecture GL named this session. Without it, every customer who fills /contact then /shop becomes an orphan.

**Receipt:** 2026-04-29. GL named the ambition: *"Everything should cascade. We should also be adding the customer information in contacts unless it's a duplicate."* The orphan hole would have shipped silently broken without GL's framing.

---

## 2026-04-29 (Stripe migration session) — Six things learned migrating Charges API → Checkout Sessions

### `/payment-success` upstream URL bug + guest 403 require route override

Frappe's `payments` app builds the post-charge redirect URL at `apps/payments/payments/payment_gateways/doctype/stripe_settings/stripe_settings.py:272`. When `redirect_to` is `None`, the code unconditionally appends `?redirect_to=None` (literal string "None") even when the URL already has `?`. The result is a malformed URL like:

```
/payment-success?doctype=Payment%20Request&docname=ACC-PRQ-...?redirect_to=None
                                                              ^ should be & not ?
```

The malformed second `?` mashes the redirect_to suffix into the docname value. AND — even with a clean URL — Frappe's bundled `payment_success.py` calls `frappe.get_doc("Payment Request", docname)` under the GUEST session, which 403s because Payment Request is restricted.

**Fix (don't patch upstream — `apps/payments/` is bind-mounted from a gitignored upstream clone):** Override the route in our app via `website_route_rules` in `hooks.py`, with our own `www/payment_success.py` that:
1. Strips any `?redirect_to=None` tail off `docname`
2. Verifies the linked `Integration Request` (or Stripe session) is `Completed` — proves the charge actually succeeded; defends against guessing PR names
3. Looks up the SO with elevated read perms (we never read PR as guest)
4. Redirects to `/thank-you?order=<so_name>`

**Receipt:** GL hit this 2026-04-29 with the bug-report URL `/payment-success?doctype=Payment%20Request&docname=ACC-PRQ-2026-00008?redirect_to=None` returning 403. Override pattern fixed it. See `apps/locally_twisted/locally_twisted/www/payment_success.py`.

### Frappe payments app uses legacy Charges API — every BBC client needs Checkout Sessions before customer-facing work

Frappe's `payments` app (`apps/payments/payments/payment_gateways/doctype/stripe_settings/stripe_settings.py:create_charge_on_stripe`) calls `stripe.Charge.create()` — the **legacy Charges API**. The `stripe-best-practices` skill explicitly says: "Never recommend the Charges API." Reasons:

- No 3DS / SCA support (will fail in EU; may fail with US issuers requiring 3DS)
- No dynamic payment methods (no Apple Pay, Google Pay, Link auto-injection)
- No fraud signals as rich as PaymentIntents

The customer-facing form Frappe ships (`/stripe_checkout`) is also a custom card UI that looks unbranded and erodes trust at point of payment. GL's reaction 2026-04-29: *"This looks unprofessional. I don't trust it."*

**Fix:** Bypass Frappe's payment_url entirely. Create a Stripe Checkout Session directly from our app and hand the customer the `checkout.stripe.com/c/pay/cs_test_...` URL. Customer sees Stripe's polished hosted page with their full UI: dynamic payment methods, security badges, real-time validation, "Powered by Stripe" footer.

**Pattern:** New `apps/locally_twisted/locally_twisted/payments/stripe_session.py` with `create_session_for_sales_order(...)`. Called from `submit_guest_order` after PR creation. Returns the hosted URL.

**For every future BBC client on Frappe**: do this BEFORE any customer-facing demo. The Frappe-bundled card form is too embarrassing to ship.

### Stripe CLI's `--api-key` flag bypasses login when CLI auth is blocked

Stripe CLI normally requires browser-based login + 2FA via `stripe login`. For LT, Jeff's phone holds the 2FA — not always reachable when GL needs to test. Workaround: `stripe listen --api-key <sk_test_...>` accepts the secret key directly and bypasses the stored auth entirely.

**Pattern that works:**
```bash
export STRIPE_LT_KEY=$(grep '^STRIPE_TEST_SECRET_KEY=' .env | sed 's/^STRIPE_TEST_SECRET_KEY=//')
stripe listen --api-key "$STRIPE_LT_KEY" --forward-to http://localhost:8081/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook
```

The listener prints `whsec_...` on the second line. Pass that to `scripts/setup/set_stripe_webhook_secret.py whsec_<value>` to persist in `site_config.json`. Restart backend.

**Caveat:** the secret rotates each time the listener restarts. So this is for dev convenience, not a stable production webhook. For prod, use Stripe Dashboard → Webhooks → Add endpoint, get the stable signing secret.

**Receipt:** 2026-04-29. The CLI's stored auth was BBC's (and BBC's test key had expired). Fresh login to LT's account was blocked by 2FA. The `--api-key` flag let us point the listener at LT's account using the secret key already in `.env`.

### Webhook signing secret belongs in `site_config.json`, not Stripe Settings doctype

Per-environment values that should NEVER travel between dev/staging/production live in `site_config.json`. Doctypes get backed up + restored across sites; `site_config` does not. The Stripe webhook secret for the local dev listener is different from the one Stripe Cloud will issue for production.

**Pattern:** `frappe.conf.get('stripe_webhook_signing_secret')` reads from `site_config.json` at the site root. Setup helper at `scripts/setup/set_stripe_webhook_secret.py` writes via `bench --site frontend set-config`.

This was a deliberate choice over adding a Custom Field to Stripe Settings. Custom Fields are fixtures that travel; `site_config` is per-site by design.

### Server-side reconciliation on `/payment-success` keeps the demo working without webhooks

The customer-facing flow can mark the SO/PR Paid synchronously when the customer's browser lands on `/payment-success?session_id=...` — using `stripe.checkout.Session.retrieve()` to verify `payment_status == 'paid'`, then calling `pr.set_as_paid()`.

This makes the webhook **optional** for demo purposes. The webhook handler still exists (and is signature-verified, idempotent) for production where it's the safety net for browser-closed-before-redirect cases. Whichever path fires first marks the PR Paid; the second path no-ops.

**Trade-off accepted:** if the customer closes their browser between Stripe success and our redirect, the SO won't be marked Paid until the webhook fires. For LT's controlled-demo and small-customer-volume situation, that's fine. For a high-volume e-commerce build, the webhook should be the source of truth.

### "I had it backwards" — the .env keys are the auth, the CLI is separate

Twice this session I asked GL for credentials they'd already provided. The .env file's `STRIPE_TEST_PUBLISHABLE_KEY` + `STRIPE_TEST_SECRET_KEY` ARE LT's authentication for ERPNext's Stripe integration. The Stripe CLI's stored auth (visible via `stripe config --list`) is a SEPARATE auth context for the listener tool.

**Lesson for the next instance:** before asking GL for credentials, check (a) `.env` for service-side keys, (b) `stripe config --list` for CLI auth, (c) `bench --site frontend execute frappe.client.get_value` against Stripe Settings. If something is already there, don't ask GL to redo it.

GL named this directly: *"I've already done this authentication!"* — the second time. Anti-pattern #5 fired on top of #5: don't make GL prove they've done something.

---

## 2026-04-29 (mobile-drawer build) — `web_include_css` browser-cache trap

### What happened

Edited `lt-theme.css` to add a mobile drawer overlay (drawer + backdrop + body scroll lock). Server-side everything was correct: `curl /assets/locally_twisted/css/lt-theme.css` returned the new content with `Last-Modified` set to the edit time. Playwright (fresh browser context, no cache) rendered the page perfectly — drawer hidden on desktop via `position: fixed; visibility: hidden; transform: translateX(100%)`.

But on GL's actual browser, the drawer rendered as inline content on **every page**, on desktop. The "Menu" heading, X close button, and all 7 nav links appeared in normal page flow below the desktop nav.

### Why

`web_include_css` injects a static URL (`/assets/locally_twisted/css/lt-theme.css`) with no version query string. Nginx serves it with `Last-Modified` and `ETag`, so a polite browser should revalidate — but in practice, Chromium-family browsers cache aggressively and serve stale CSS for hours-to-days unless explicitly forced.

When GL navigated to a page after the edit:
- The HTML was fresh (Frappe templates are server-rendered per request) → new drawer markup loaded
- The CSS was cached (browser served the old `lt-theme.css`) → no `position: fixed` rule for `.lt-header__mobile-nav-collapse` → drawer fell into normal document flow

The new HTML + old CSS combination is the worst case: the user sees the new structure rendered with the old (or missing) styles. This is invisible to Playwright (fresh context, no cache) and to `curl` (always fetches fresh) — only a real long-lived browser session reproduces it.

### What to do differently

**Standing rule:** every edit to `lt-theme.css` requires a bump to the `?v=` query string in `hooks.py`'s `web_include_css` line. Format: `YYYYMMDD-N`.

Current line:
```python
web_include_css = "/assets/locally_twisted/css/lt-theme.css?v=20260429-1"
```

Each edit → bump the version. Each version bump → backend restart (`docker restart locally-twisted-erpnext-v15-backend-1`) so Frappe re-reads `hooks.py`. The query string change forces every browser to fetch fresh CSS the next time the page loads — no hard-refresh needed by the user.

### Verification gate (post-CSS-edit ritual update)

The existing operational ritual was:
> Edit Jinja / CSS / Web Page record → `python scripts/dev/clear_website_cache.py`

That clears server-side template cache but does NOT bust browser caches. Updated ritual:
1. Edit `lt-theme.css`
2. Bump `?v=` in `hooks.py`
3. `docker restart locally-twisted-erpnext-v15-backend-1 && sleep 8`
4. `python scripts/dev/clear_website_cache.py`
5. Verify in a fresh-incognito Playwright AND in GL's actual browser before declaring done

Without step 2, GL's browser will serve stale CSS even though the server-side file is current. This pattern bit us 2026-04-29 with the mobile drawer overlay.

### Belt-and-suspenders option (deferred)

A more durable fix: compute the version dynamically from the file's mtime in `hooks.py`. Sketch:
```python
import os
_THEME = os.path.dirname(os.path.abspath(__file__)) + "/public/css/lt-theme.css"
_V = int(os.path.getmtime(_THEME)) if os.path.exists(_THEME) else 0
web_include_css = f"/assets/locally_twisted/css/lt-theme.css?v={_V}"
```

Pro: no manual bump, no rule to remember. Con: needs to be tested against Frappe's hooks.py loader (does it tolerate computed values? do containers see the right file path?). Park as a future cleanup once the manual rule has lived through enough sessions to confirm it's reliable.

---

## 2026-04-29 (Stripe wiring + true guest checkout session) — Five Frappe internals discovered

### Frappe Payment Request `payment_url` is gated behind `send_mail` — manual call required when suppressed

`Payment Request.on_submit` (apps/erpnext/...accounts/doctype/payment_request/payment_request.py:215) calls `set_payment_request_url()` ONLY inside the `if send_mail and self.payment_channel != "Phone":` branch. `send_mail` becomes False when EITHER `ref_doc.order_type == "Shopping Cart"` OR `self.flags.mute_email = True` (line 211). Both are necessary for guest checkout — but they ALSO suppress the URL-generation call.

**Fix:** after `pr.submit()`, call `pr.set_payment_request_url()` manually then `pr.reload()`. See `apps/locally_twisted/locally_twisted/www/checkout.py` for the working pattern.

**Receipt:** smoke test #3 (URL Test customer, since cleaned). After fixing wkhtmltopdf error, `payment_url` came back None. Traced to `set_payment_request_url` not being called. Manual call populated it correctly.

### wkhtmltopdf inside the Frappe Docker container can't reach localhost:8081

Anywhere Frappe auto-renders a PDF inside the running container — `attach_print()`, Sales Order print formats, Payment Request emails — wkhtmltopdf is invoked and tries to fetch CSS/assets from the site's public URL. Inside the container's network namespace, `localhost:8081` doesn't resolve. Result: `OSError: wkhtmltopdf reported an error: Exit with code 1 due to network error: ConnectionRefusedError`.

**Workaround for Payment Request:** set `Sales Order.order_type = "Shopping Cart"` AND `payment_request.flags.mute_email = True` BEFORE `pr.submit()`. Both checks are at `payment_request.py:211`. Either alone may not be enough.

**Long-term fix (deferred):** configure `host_name` in `site_config.json` to a docker-internal hostname (e.g., `http://frontend:80`) so wkhtmltopdf can reach back to the site from inside the network. Future hardening item.

**Receipt:** smoke test #2 (Trace Test, since cleaned). Got the full traceback chain: `Payment Request on_submit → send_email → attach_print → pdfkit.to_pdf → wkhtmltopdf → ConnectionRefusedError`.

### `Contact.links` is a child table, NOT a column — query Dynamic Link directly

`Contact` has a `links` field that looks like a column in Customize Form, but it's a Table-fieldtype (child of Contact). Querying `frappe.db.get_value("Contact", ..., ["links"])` errors with `pymysql.err.OperationalError: (1054, "Unknown column 'links' in 'SELECT'")`.

**Fix pattern for Contact → Customer lookup:**
```python
contact_name = frappe.db.get_value("Contact Email", {"email_id": email}, "parent")
if contact_name:
    customer_name = frappe.db.get_value(
        "Dynamic Link",
        {"parent": contact_name, "link_doctype": "Customer", "parenttype": "Contact"},
        "link_name",
    )
```

Same pattern applies to any parent doctype's Table fields — query the child table by `parent` field, not the parent's "column."

**Receipt:** first guest-checkout smoke test failed with the Unknown column error. Fix is in `checkout.py:292-302` with comments.

### Stripe Settings auto-creates the entire payment chain on insert

Inserting a `Stripe Settings` record with `gateway_name`, `publishable_key`, `secret_key` triggers ERPNext's `on_update` hook which auto-creates:
- Payment Gateway named `Stripe-{gateway_name}` (e.g., `Stripe-Test`)
- Bank Account named `Stripe-{gateway_name} - {company_abbr}` (e.g., `Stripe-Test - LT`) — Currency = company default
- Payment Gateway Account linking the gateway to the bank account, marked default

You don't need to create any of those manually. Just insert the Stripe Settings → wire `Webshop Settings.payment_gateway_account` to the auto-created PGA name → done. Pattern codified in `scripts/setup/configure_stripe_test_mode.py`.

**Receipt:** session 2026-04-29. Wrote configure_stripe_test_mode.py expecting to need follow-up scripts for PG / PGA / Account creation. None needed — all four records existed after one insert.

### Webshop checkout requires `payment_gateway_account` set OR `enable_checkout=1` won't stick

`Webshop Settings.enable_checkout = 1` set via `frappe.client.set_value` silently reverts to 0 if `payment_gateway_account` is null. The save validator quietly rejects the change. Set both fields in the same `set_value` call (with the multi-field `fieldname` dict format) and both stick.

**Pattern:**
```python
frappe.client.set_value(
    doctype="Webshop Settings",
    name="Webshop Settings",
    fieldname={
        "payment_gateway_account": "Stripe-Test - USD - LT",
        "enable_checkout": 1,
    },
)
```

**Receipt:** session 2026-04-29. First attempt set only `enable_checkout=1`, saved silently, value was still "0" on read-back. Second attempt set both fields together — both took.

---

## 2026-04-28 (BTFP restructure + ribbons + font weight + color session) — Three CSS gotchas

### DM Serif Display is a single-weight font (400 only) — never override `font-weight` on heading classes

The brand serif at `https://fonts.googleapis.com/css2?family=DM+Serif+Display` has only the default cut. Setting `font-weight: 600` on `.lt-faq h1`, `.lt-faq__group-title`, `.lt-policy h1`, `.lt-policy h2`, etc. produces synthetic-bold (faux-bold) rendering — chunky, heavy, unrefined.

**Fix:** remove `font-weight: 600` from any class that targets a heading (h1/h2/h3) which inherits the global `h1, h2, h3 { font-family: 'DM Serif Display'; font-weight: 400; }` rule. Want emphasis? Use SIZE not WEIGHT (e.g., bumped FAQ group titles from 1.25rem → 1.5rem after removing the weight override).

`font-weight: 600` IS valid on Raleway-based classes (`.lt-faq__link`, `.lt-policy__link`, `.lt-faq__answer strong`) — Raleway has real 600. The rule is heading-class-specific.

**Receipt:** GL flagged the chunky look on /faq + /refund-policy. Comparing to BTFP intro h1 (no override → elegant) confirmed the cause. Fix landed in `faq.py` and `refund_policy.py` 2026-04-28.

### CSS `margin: 0` (shorthand) defeats `.lt-fullbleed` negative margins

`.lt-fullbleed` (in lt-theme.css) uses:
```css
margin-left: -50vw;
margin-right: -50vw;
```

Any rule with `margin: 0` or `margin: <something>` (the shorthand) wipes out the negative margins because shorthand sets all four sides. Result: the section stops at the parent container's edge instead of going edge-to-edge.

**Fix:** when defining a class that needs to coexist with `.lt-fullbleed`, use specific properties (`margin-top: 0; margin-bottom: 0;`) instead of the shorthand. Or just not set vertical margins at all.

**Receipt:** GL flagged "the ribbon containers that are thin and supposed to go across the whole page dont." The blush + soft-blue ribbons had `.lt-btfp__ribbon { margin: 0 }`. Replaced with specific top/bottom margins; ribbons span full width.

### `--lt-near-white` was too cold (#FBFBFB read as bluish-grey) — bumped to #fffcfc

GL: *"the main white background is so white it's bluish and/or gray... Try fffcfc for the main background."* Updating the CSS custom property at `:root { --lt-near-white: #FBFBFB }` → `#fffcfc` makes the body, BTFP booking section, and (later) the footer copyright bar feel warm rather than cold. `#FFFFFF` (the `--lt-white` token, used on cards and contrasted panels) stays unchanged for visible contrast.

**Pattern lesson:** `--lt-near-white` is the new "base white" token across the site. When choosing between `--lt-white` and `--lt-near-white` for a background, pick `--lt-near-white` for surfaces that should feel calm/quiet and `--lt-white` for surfaces that need to pop against the surrounding bands.

---

## 2026-04-27 (small-shop seed session) — Six webshop gotchas

### `upload_file` API does NOT auto-write the file_url to the parent doc's field

Called Frappe's `/api/method/upload_file` endpoint with `doctype=Item`, `docname=<slug>`, `fieldname=image`, `is_private=0` and got back a valid `{"file_url": "/files/<slug>.png"}` response. **The File record was created** with `attached_to_doctype=Item`, `attached_to_name=<slug>`, `attached_to_field=image`. **But `Item.image` stayed null.**

**Why:** the upload endpoint creates the File attachment record but does NOT write the file_url back into the parent doc's named field. Two separate operations.

**Fix:** explicit `frappe.client.set_value` call after upload — `Item.image = file_url`. AND for storefront display, also set the **separate** `Website Item.website_image` field (Item.image and Website Item.website_image are independent in v15).

**Receipt:** Seed script ran successfully, 33 File records created with the right attached_to_field, but the storefront showed empty placeholder boxes ("NB", "GG" letter avatars). Auditing Item records showed all 33 with `image: None` despite the File records existing.

### Webshop is OFF by default — `Webshop Settings.enabled = 0`

Fresh install of `frappe/webshop` ships with the storefront effectively disabled. **All these critical fields default to 0:** `enabled`, `show_price`, `show_stock_availability`, `enable_field_filters`, `enable_attribute_filters`, `enable_checkout`, `enable_wishlist`, `enable_reviews`, `allow_items_not_in_stock`. **And `price_list` defaults to None.**

**Fix:** explicitly set every field that matters BEFORE expecting browse / price-display / cart to work. Minimum to get a browseable shop with prices:
```
enabled = 1
show_price = 1
allow_items_not_in_stock = 1   # required for non-stock (made-to-order) items
products_per_page = 12         # default 0 = silently broken
price_list = "Standard Selling"  # default None = no prices visible
default_customer_group = "Individual"
enable_checkout = 1            # otherwise "Add to Quote" instead of "Add to Cart"
```

**Receipt:** Created 33 Website Items with `published=1`. /all-products rendered exactly 2 of them with no prices. Spent multiple turns chasing pagination + permission filter theories before discovering Webshop Settings.enabled=0 was silently filtering the entire result set in `add_display_details`.

### Webshop's whitelisted method path is `webshop.webshop.api.*`, not `webshop.api.*`

Folder layout: `apps/webshop/webshop/webshop/api.py`. Frappe convention says this Python module is `webshop.webshop.api`. The compiled JS bundle correctly calls `frappe.call({method: "webshop.webshop.api.get_product_filter_data"})`. **But intuitively the path "looks like" it should be `webshop.api.*` — and that's wrong.**

Calling `webshop.api.get_product_filter_data` returns HTTP 417 EXPECTATION FAILED with `ValidationError: Failed to get method ... with No module named 'webshop.api'`.

**Pattern:** Frappe apps double-namespace. The `<app_name>` Python package contains a `<app_name>` sub-module containing the module files. So `<app>.<module>.<file>` is the import path, even when `<app> == <module>`.

**Receipt:** Spent a turn convinced the JS was calling the wrong path because my direct curl was getting 417. The JS was correct; my curl was wrong.

### Frappe's `body { display: flex; height: 100vh; overflow-y: auto }` defeats Playwright `full_page=True`

The webshop pages set the body to a fixed-height flex container with internal overflow-scroll. **Playwright's `full_page=True` only captures `documentElement.scrollHeight`, which on these pages = viewport height = 800px** — even though the actual content (product grid) extends thousands of pixels below.

The user experience is fine: customers scroll inside the page body and see all the products. **But if you screenshot at the default 1280×800 viewport and trust what you see, you'll declare the shop "broken" when only the first row visible.**

**Fix when verifying with Playwright:** use a tall viewport (`viewport={"width": 1280, "height": 3500}`). The DOM still renders identically; the viewport just captures more in the screenshot.

**Receipt:** Spent two iterations debugging "only 2 items render" before checking `body.offsetHeight` (= 800) vs `#products-grid-area.offsetHeight` (= 2707). 12 items WERE rendered, just below the captured frame.

**Pattern:** Always probe `document.documentElement.scrollHeight` AND the children's heights before trusting a Playwright screenshot's "what's missing" implication. Add the height probe to the standard verification preamble.

### Setting `Item.standard_rate` auto-creates an Item Price — explicit Item Price insert hits a duplicate-detection exception

When inserting an Item via `frappe.client.insert` with `standard_rate` populated, ERPNext's Item controller auto-creates a corresponding Item Price record (under "Standard Buying" by default, or "Standard Selling" for sales-only items). A subsequent explicit `Item Price` insert for the same item + price list raises `ItemPriceDuplicateItem` (HTTP 417), which is NOT caught by the standard `"already exists" / "DuplicateEntryError"` patterns.

**Fix:** expand idempotency-detection in any seed script to ALSO catch `ItemPriceDuplicateItem` and `"appears multiple times"`. Or skip the explicit Item Price insert entirely when standard_rate is set on the Item.

**Receipt:** First seeder run blew up at item #1 with HTTP 417 because of the duplicate. Patched the idempotency check, re-ran, succeeded.

### Webshop initial render goes through AJAX, not server-side Jinja

The `/all-products` page's index.html is empty for products (just `<div id="product-listing"><!-- Rendered via JS --></div>`). The JS in `index.js` instantiates `webshop.ProductView` which calls `frappe.call({method: "webshop.webshop.api.get_product_filter_data"})` and renders results client-side.

**Implication for verification:** `curl http://localhost:8081/all-products | grep <product-name>` returns nothing — products are not in the server-rendered HTML. Use Playwright with `wait_until="networkidle"` to capture post-JS state.

**Implication for SEO:** the storefront is JS-rendered, which is bad for crawlers without execution. If SEO matters for the small shop, server-side rendering of the first batch is a future concern. Out of scope for v1.

---

## 2026-04-27 (homepage build session) — Five gotchas + two reusable patterns

### Frappe Python module cache is sticky — restart backend after editing `www/<route>.py`

Edited `home.py` PAGE_CSS expecting the next `clear-website-cache` to refresh the served HTML. It did NOT. The HTML markup updated but the inline `<style>` block (injected via `context.colocated_css`) kept serving the OLD CSS.

**Why:** Frappe imports `www/home.py` once per Python worker process, then caches the module. `bench --site frontend clear-cache` clears Frappe's render cache, but doesn't reload Python imports. Editing the .py file means the running gunicorn worker still holds the old module in memory.

**Fix:** `docker restart locally-twisted-erpnext-v15-backend-1` — that bounces the gunicorn workers and forces re-import on next request. Sleep 8s for the container to come up, then test.

**Receipt:** Spent a turn confused why `lt-fullbleed` wasn't visibly working. `curl localhost:8081/ | grep "@keyframes lt-hero-cycle"` showed 0 matches (the v2 keyframes weren't in the served HTML). Restart fixed it immediately.

**Pattern:** Whenever PAGE_CSS or any Python data structure changes in a `www/` controller, the cycle is: edit → `docker restart <backend>` → `clear-website-cache` → test. Template-only changes (just HTML) re-render on next page hit; controller changes need the restart.

### Web Page DocType records compete with `www/` files for the same route

Visited `/` after creating `home.py` + `home.html` and got the prior "Site under construction" placeholder, NOT my new homepage. Diagnosed via SQL: `SELECT name, route, published FROM \`tabWeb Page\` WHERE route IN ('home');` → returned name="locally-twisted", route="home", published=1.

**Why:** Website Settings.home_page = "home". When `/` resolves, Frappe looks for a route named "home" via multiple resolvers. A published Web Page record AND a `www/home.html` file both claim that route. The Web Page record won.

**Fix:** `UPDATE \`tabWeb Page\` SET published = 0 WHERE name = 'locally-twisted';` — deactivates the placeholder. The www/home.html file then takes precedence.

**Pattern:** Before creating any new `www/<route>.<py|html>` file, check if a published Web Page record already claims that route. If yes, decide: (a) deactivate the Web Page record (cleanest), (b) move the Web Page content into your www/ template, (c) pick a different route. Don't assume www/ wins by default — it depends on Website Settings.home_page and which resolver runs first.

### Frappe full-bleed pattern — `width: 100vw` + `margin-left: -50vw` breaks out of the parent .container

Bands rendered as colored stripes inside the centered content column, leaving white margins on left and right (GL's "Image #5" complaint about banners cut off). The `templates/web.html` parent wraps content in a `.container` with max-width that constrains everything inside.

**Fix:** A `.lt-fullbleed` modifier class:

```css
.lt-fullbleed {
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
}
```

Applied to `<section>` elements that should read as full-width bands (hero, reviews, featured, crawl, CTA, twisting spotlight). Inside each section, an inner `.lt-<block>__inner` div with `max-width: 1200px; margin: 0 auto;` keeps content readable.

**Receipt:** The first homepage v2 deploy showed bands visibly constrained. Adding `.lt-fullbleed` to 6 sections fixed it without touching the parent template.

**Pattern:** This is the standard CSS technique for "break out of a constraining parent container." Document it in the meal — every BBC client's portal pages have the same parent.container constraint.

### CSS-only cycling content (hero headlines, blog post titles, etc.) — staggered animation-delay on absolutely-positioned children

GL wanted the hero headline to cycle through blog post titles while a stable tagline stays put underneath. Implemented with pure CSS (no JS):

```css
.lt-hero__cycling { position: relative; min-height: 4.4rem; }
.lt-hero__title {
    position: absolute; inset: 0;
    opacity: 0;
    animation: lt-hero-cycle 32s infinite;
}
.lt-hero__title:nth-child(1) { animation-delay: 0s; }
.lt-hero__title:nth-child(2) { animation-delay: 8s; }
.lt-hero__title:nth-child(3) { animation-delay: 16s; }
.lt-hero__title:nth-child(4) { animation-delay: 24s; }
@keyframes lt-hero-cycle {
    0%   { opacity: 0; }
    3%   { opacity: 1; }
    22%  { opacity: 1; }
    25%  { opacity: 0; }
    100% { opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
    .lt-hero__title { animation: none; opacity: 0; }
    .lt-hero__title:nth-child(1) { opacity: 1; }
}
```

**First-paint gotcha:** at t=0 the keyframe is at 0% which is opacity 0. Title 1 invisible until 1s into the cycle. Solutions: (a) negative `animation-delay: -1s` on title 1 to start mid-cycle, or (b) live with the 1s fade-in delay (current state — Playwright captures show title 1 visible by the time `wait_until="networkidle"` fires).

**Pattern:** Reuse for any cycling content where one stable element + one rotating element is the desired UX (testimonials, blog teasers, mood-to-quote in lookbook). Total cycle = N × per-title duration; staggered delays = full duration / N.

### Carousel of cards — same CSS marquee pattern as text crawl, just bigger items

GL pivoted reviews from 5-inline-cards to a horizontal-scrolling carousel of all 19 reviews. Reused the existing `.lt-crawl` pattern verbatim, swapping text spans for full review cards:

- Outer viewport: `overflow: hidden; mask-image: linear-gradient(...);` for edge fade
- Track: `display: flex; gap: 1rem; width: max-content; animation: scroll Ns linear infinite;`
- Items: `flex: 0 0 320px;` (fixed card width, no shrink)
- Track has duplicate set (aria-hidden) for seamless loop
- `.viewport:hover .track { animation-play-state: paused; }` for reading-on-hover
- `prefers-reduced-motion` falls back to flex-wrap (cards stack)

**Speed scaling:** text crawl = 270s for 54 names; card carousel = 360s for 19 cards. Cards are bigger and need reading time.

**Pattern:** Same primitive can do client-name marquee, review-card carousel, photo-strip carousel, etc. Worth a recipe (kitchen note dropped at agency-tier capabilities).

### `git status` showed 6 deleted `_oneshot_*` files persisting from prior session — auto-commit hook handles writes, not deletions

The git status at session start showed 6 ` D ` (working-tree-deleted, unstaged) entries from prior session's cleanup. These weren't blocking but they made `git status` noisy.

**Why:** the auto-commit hook fires on Write tool calls. Deletions via filesystem don't trigger it. Net effect: deleted files stay as unstaged deletions until someone commits them explicitly.

**Pattern:** If a session ends with stale ` D ` entries in git status, that's not a leak — but worth a cleanup commit if doing housekeeping. Otherwise the next instance will see them too.

---

## 2026-04-26 (codification + chrome + accessibility + contact + BTFP session) — Five gotchas worth carrying forward

This session shipped four real surfaces (chrome, accessibility, contact, BTFP) and one meal. Five gotchas hit during the work, each with a verified receipt. All five are now codified in `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` "Known gotchas" section so the next instance doesn't rediscover.

### Frappe `www/` does NOT auto-translate underscored filenames to dashed URLs

A controller named `<app>/www/balloon_twisting_and_face_painting.py` serves at `/balloon_twisting_and_face_painting`, NOT at `/balloon-twisting-and-face-painting`. Python module names cannot have dashes; URLs typically should. Bridge the two with `website_route_rules` in `hooks.py`. After editing hooks.py: cache clear is not enough — also flush Redis and restart the backend; the route map caches aggressively.

### Frappe's website bundle has direct `<p>` rules that override inherited text-align

Setting `text-align: center` on a parent section does not reliably reach `<h1>` / `<p>` children — Frappe's bundle has direct selectors at higher specificity. Direct selectors always beat inherited values regardless of cascade order. **Fix:** declare `text-align: center` directly on each text-bearing block via its BEM class. This bit twice in the same session (footer brand block, BTFP intro lede); same pattern, same fix.

### Webshop's CSS/JS bundles need `bench build` (Node + yarn required)

`webshop/hooks.py` registers `web_include_css = "webshop-web.bundle.css"` + `web_include_js = "web.bundle.js"`. Without `bench build`, those bundles aren't compiled, `assets.json` lacks the entries, Frappe falls back to bare paths, browsers 404. Worse: `web.bundle.js` defines the global `webshop` JS namespace; without it, `/all-products` throws `Uncaught ReferenceError: webshop is not defined`. The frappe_docker production image has no Node, BUT Node v20 is available via nvm at `/home/frappe/.nvm/versions/node/v20.19.2/`. Symlink it into `/usr/local/bin` so `/bin/sh` subprocesses (which `bench build` uses) find it. Same for yarn (install via `npm install -g yarn`). All wrapped in `scripts/setup/install_webshop.py --build-assets` for reproducibility after container recreation.

### Lead Source records don't exist on a fresh ERPNext install

`Lead.source` is a Link to `Lead Source`. On a fresh install, that DocType has zero records. Setting `source="Website"` raises `LinkValidationError`. Fix: idempotently create the source before creating the Lead (`frappe.db.exists` + try-`insert` with `ignore_if_duplicate`). Caught at the LT contact-page first smoke test before GL ever saw it. The same pattern applies to any Link-field default: ensure-or-create the linked record before creating the parent.

### Browser cache + `web_include_css` files

Files registered via `web_include_css` serve via the symlink chain. Their `Last-Modified` and `ETag` update on edit, but Brave (and other browsers) sometimes don't re-validate within a session. Visual symptom: page shows a mix of old and new CSS rules; new BEM classes look unstyled (logo at native size, lists with bullets, no flex). DevTools Network shows the file from cache. **Fix:** hard-refresh (`Ctrl+Shift+R`). **For the meal:** ALWAYS include "hard refresh" in the handoff to GL when shipping a CSS-touching change. Saves a confused round-trip.

### Generalizable lesson promoted to agency-tier

Each of these is now in the meal's "Known gotchas" section with a receipt. The next instance reading the meal sees them as patterns-to-anticipate, not patterns-to-rediscover.

---

## 2026-04-26 (codification session) — `extend_doctype_class` is NOT consumed by Frappe v15

External research (Magic Research / `frappe-erpnext-non-gpl-hooks-comparison.md`) recommended preferring `extend_doctype_class` over `override_doctype_class` for "lower-conflict" coupling. Verified against running Frappe v15 source: `grep -rn 'extend_doctype_class' apps/frappe/` returns NO consumer in Frappe core. The Payments app declares `extend_doctype_class = {"Web Form": "..."}` in its `hooks.py`, but Frappe never reads that hook key — Payments' actual Web Form behavior change comes through `override_whitelisted_methods` instead.

**Generalizable lesson:** verify external research against the running source before codifying. If GL hadn't asked for it to be codified at agency tier, this wrong claim could have led the next instance to declare a hook that does nothing. The verify-against-source rule worked — it caught a 95%-correct external research piece's one wrong claim. Codified at `Built_by_Cameron/.claude/capabilities/recipes/license-isolated-app-architecture.md` "Corrections from source" section.

---

## 2026-04-26 (session end) — TWO consecutive landing-page failures share one pattern: invent + band-aid + claim-done-off-DOM-facts

**What happened:** This session's instance built a landing page using `Web Page` content_type=Page Builder with 4 default Web Templates. The build looked complete from DOM facts (curl showed all sections rendered, Playwright captured a 1366×3818 screenshot, all the section IDs and class names were present). The instance reported it as "tier 1 native" and ready for review. GL opened the page in their actual browser. **It wasn't visible. It wasn't responsive. The copy was made-up.**

**Root cause is now nameable:** Both this session's failure AND the prior Slice 2 failure share the same anti-pattern:
1. **Invent placeholder copy** instead of pulling from the approved Odoo XML / live site source
2. **Use band-aid CSS** (`!important` chains in the prior session; default Page Builder template + thin theme CSS in this session) instead of using the framework's intended override surfaces
3. **Declare done off DOM facts** (the DOM has the elements; the page must be working) instead of verifying GL can see the rendered output in a real browser at multiple viewport widths

**The architectural primitives weren't the problem.** Web Page DocType + Page Builder + custom Frappe app + web_include_css are all valid Frappe paths. They CAN produce a working result. They DID NOT, twice in a row, because the technique inside the architecture was wrong.

**What the third instance must do differently:**
1. **Source content from the Odoo XML or live locallytwisted.com — never invent.** Documented as a standing decision this session.
2. **GL's eyes on the actual page > any DOM fact.** A successful Playwright capture is a precondition, not a verdict. GL opens the page on their phone and their laptop and confirms. THEN it's done.
3. **Match GL's STYLE-GUIDE.md visual identity.** Not "looks roughly right." The brand foundation has specific fonts, colors, spacing. Slop fails.
4. **Mobile-first verification.** 375px viewport BEFORE 1366px desktop. If it doesn't work on mobile, it isn't done — Jeff's customers use phones.
5. **The platform-direction decision (custom Jinja vs decoupled vs Frappe Builder) is GL's call, made consciously.** Don't presume Frappe is the answer because you arrive in a Frappe codebase. The expedition synthesis is the briefing.

**Generalizable lesson promoted to agency tier:** This is a specific case of the broader "verify with reality, not with claims" anti-pattern in the global `anti-gl-patterns.md`. The LT-specific receipts are now in this file's 2026-04-26 (Slice 2 build) entry AND this entry. Two strikes. The third instance must break the pattern.

---

## 2026-04-26 (Jinja override path validation) — The override DOES resolve in our Docker bind-mount setup

**What happened:** Two prior HANDOFFs claimed "override Jinja partials at `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html`" was the path forward for Slice 2. Nobody had verified the override actually resolved in our specific bench setup. This session: dropped a minimal test file with a visible string, cleared cache, fetched the home page, confirmed the test string appeared in served HTML.

**Verified working:**
```
apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html
```
Place a file at this path in our custom app. Frappe's template lookup resolves it before Frappe's standard footer at `apps/frappe/frappe/templates/includes/footer/footer.html`. Same pattern works for navbar and other Jinja partials.

**Required after creating/editing the override:** `python scripts/dev/clear_website_cache.py` — Frappe caches the resolved template path; the cache must be cleared for the override to take effect on next request.

**The test file was REMOVED after validation** — it was overriding the real Frappe footer with the test string, which is not what we want long-term. The next instance creates the real footer override only when ready to build the actual Slice 2 redo.

**Generalizable lesson:** When a HANDOFF claims an architectural path is "the way forward" but nobody has executed even the minimal version, the next instance MUST verify the path before building substantively on top of it. One test file proves the assumption (or surfaces a deeper problem to fix). The cost of the test is minutes; the cost of building on an invalid assumption is a session.

---

## 2026-04-26 (webshop install + framework study + Web Page tabs finding) — Read the DocType schema BEFORE planning custom code

**What happened:** The pricing calculator on the BTFP service page was planned as a "tier 4 custom Web Template" build — meaning we'd write a custom Jinja template + register it via hooks + extend it from a Web Page record. Three instances in a row independently classified it this way, including me when I wrote the v1 index. The calculator was treated as the "irreducibly custom code" piece that justified opting into tier 4.

GL surfaced the actual answer mid-session: *"the previous instance edited this page http://localhost:8081/app/web-page/locally-twisted by using the content field update, not the scripting tab where you can literally just add javascript. You can create webpages with javascript but the prior instance just filled in the content field and it made everything look bad — because they should have used java! You can use java on these pages!"*

I went and read the Web Page DocType schema (`apps/frappe/frappe/website/doctype/web_page/web_page.json`). It has these tabs natively:

| Tab | Field | What it natively supports |
|---|---|---|
| Content | `content_type`, `main_section`/`main_section_html`/`main_section_md`, `page_blocks` | Body layout (multiple input modes including Page Builder) |
| Script | `javascript` (Code field) | **Per-page JavaScript that runs at page load** |
| Style | `css` (Code field), `insert_style` (Check) | **Per-page CSS scoped to this page** |
| Header and Breadcrumbs | `header` (HTML), `breadcrumbs` (Code), `dynamic_template` | Custom hero HTML, breadcrumb logic |
| Settings | `show_sidebar`, `enable_comments`, `full_width` | Layout toggles |
| Meta Tags | `meta_title`, `meta_description`, `meta_image`, `dynamic_route` | Per-page SEO |
| Context | `context_script` (Code, Python) | **Server-side Python that runs BEFORE render — inject variables into the Jinja context** |

**The calculator collapses from tier 4 to tier 1:**
- Page Builder for static layout (H1, intro, FAQ accordion) → `page_blocks`
- HTML form inputs → an HTML block in Page Builder OR `main_section_html`
- Live price math → `javascript` field
- Calculator-specific styling → `css` field (with `insert_style=1`)
- No custom Web Template, no hooks, no app code, no Jinja overrides. Pure DocType configuration.

**What was learned (load-bearing for future client work):**

1. **DocTypes are the configuration surface, including for "code" things.** Frappe's Code-fieldtype fields (javascript, css, context_script) are configuration, not code-in-the-traditional-sense. They live in DocType records. They're versioned via fixtures. They survive cleanly across upgrades. Writing a custom Web Template to hold the same JavaScript is strictly worse: more files, more places to break, no benefit.

2. **The previous instance's mistake is fully named:** they used `main_section` (Rich Text) only. They didn't open the Script tab or the Style tab or use Page Builder. They didn't read the schema. They assumed the page surface was just "what `main_section` accepts." Then when they needed interactivity, they assumed they'd need to override a template — when in fact the right answer was already on the same DocType form, in a different tab.

3. **The general rule:** before reaching for a custom Web Template, custom hook, custom controller, or template override — **read the DocType's `.json` schema in the running container.** Frappe DocTypes have many more fields than the desk UI immediately surfaces. Tabs are collapsed by default. Code-fieldtype fields are easy to miss. The schema is authoritative; the form layout is just one view of it.

**Generalizable lesson promoted to agency-tier:** added a "Standing principle: System-native first" section at the top of `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` — every BBC client benefits.

---

## 2026-04-26 (Slice 2 build) — Frappe / ERPNext quirks discovered while building the website shell

A pile of gotchas hit during a single session of building the navbar + footer + scaffolding the custom Frappe app. Each one bit, each one was band-aided rather than learned-from in the moment, each one is real. Logging here so the next instance doesn't rediscover.

### `bench new-app` license validator is case-sensitive (lowercase `mit`)

The CLI prompt says `App License [mit]:` and looks like it accepts free text — it does not. Click validates against the exact list `mit`, `agpl-3.0`, `apache-2.0`, etc. Pass `MIT` (uppercase) and `bench new-app` aborts with a validation error and creates nothing. Pass `mit` (lowercase) and it proceeds.

**Lesson:** when feeding answers via heredoc/stdin to `bench new-app`, use lowercase license values. The list is documented in the prompt itself.

### Top Bar Item parent rows cannot have a URL when they have child items

`Website Settings.top_bar_items` accepts a child table where dropdown structure is encoded by `parent_label`: items with `parent_label = "Foo"` become children of the parent row whose `label = "Foo"`. **Frappe validates that a parent row's `url` is empty when it has children.** Set `{label: "What We Make", url: "/shop"}` while having children with `parent_label: "What We Make"` and the API returns `ValidationError: What We Make in row N cannot have both URL and child items`.

**Lesson:** parent dropdown rows are pure triggers, not link destinations. `url=""` for the parent; children carry the actual destinations.

### Footer Items need explicit URL-less parent rows (column headers) defined within the same table

Same shape as `top_bar_items`. `Website Settings.footer_items` rendering as columns by `parent_label` requires the parent value to exist as its own row in the same list. Skip the parent rows and Frappe raises `ValidationError: Shop does not exist in row 1` for every child whose `parent_label` doesn't match an in-list row.

**Lesson:** before child rows like `{label: "All Products", parent_label: "Shop"}`, prepend an empty-URL row `{label: "Shop", url: ""}`. Frappe groups under that parent.

### Web Page `content_type` is a hidden field-router (HTML reads `main_section_html`, Rich Text reads `main_section`)

The `Web Page` DocType has multiple body-content fields and `content_type` selects which one renders. Set `content_type="HTML"` and Frappe renders from `main_section_html`. Set `main_section` instead — the page article renders **empty** with no error, no warning, no log entry. The page exists, the title appears, but the body is just `<article>...</article>` with nothing inside.

**Lesson:** `content_type="Rich Text"` is the safe default if you're putting raw HTML in `main_section`. Always verify with a `curl` of the served page after writing a Web Page record — the article tag should contain your content.

### Frappe HTML sanitizer strips inline SVG `<path d="...">` from CMS fields like `Website Settings.address`

Wrote inline SVGs with explicit path data (Instagram, Facebook, etc. social icons) into the `address` field's HTML. Curl of the served page showed `<svg viewbox="0 0 24 24"><path></path></svg>` — viewBox lowercased, every `d=` attribute stripped, the SVG visually empty. The sanitizer treats CMS fields as untrusted user input and removes attributes deemed risky for XSS.

**Lesson:** for any iconography or styled rendering inside CMS-editable fields, use one of these instead:
- CSS `background-image: url(...)` referencing a real SVG file in `apps/<app>/<app>/public/icons/icon.svg`. Class names on the `<a>` survive sanitization; the icon comes from CSS.
- Inline SVG only inside `head_html` or `body_html` (less sanitized) or a Web Template's Jinja (not sanitized at all).
- Font icons via class names if your app loads an icon font.

### `head_html` styles load BEFORE Frappe's bundled stylesheets in the cascade

Pushed the entire LT theme CSS as a `<style>` block in `Website Settings.head_html`. The block lands in the `<head>` very early. Frappe's `website.bundle.css` and `erpnext-web.bundle.css` `<link>` tags load *after* — meaning equal-specificity rules in those bundles win. `.web-footer { background-color: var(--lt-soft-blue); }` is silently overridden by `.web-footer { background-color: ...; }` in Frappe's bundle.

**Lesson:** `head_html` is a fallback / quick-prototype surface, NOT the production override surface. The right way to override theme CSS in a custom Frappe app is `website_theme_scss` in `hooks.py` plus an SCSS file at `<app>/<app>/public/scss/website.scss`. That gets compiled INTO the website bundle and wins at equal specificity (because it's the LATER file in the merged bundle). For static CSS that doesn't need SCSS compilation, `web_include_css` in `hooks.py` is also fine because that `<link>` tag injects after the bundled CSS.

### `data:image/svg+xml;utf8,...` data URIs silently fail to render in real browsers

Tried to bypass the sanitizer issue by encoding social-icon SVGs as CSS `background-image: url("data:image/svg+xml;utf8,%3Csvg ...")`. Several browsers (real Chromium, Firefox) silently rendered the circles with no icon — accepting the CSS without error, painting the gradient/color background, but failing to decode the SVG. The headless `chrome --screenshot` flag rendered it slightly differently than Playwright's full Chromium, so the breakage was invisible in our quick captures.

**Cause:** the prefix `;utf8,` is non-standard. Real spec is `data:image/svg+xml;charset=utf-8,...` or just `data:image/svg+xml,...`. Additionally, unencoded spaces inside the SVG path `d` attribute trip stricter parsers.

**Lesson:** when you need icons in CSS, use real SVG files in the app's `public/icons/` folder and reference them via plain `url("/assets/<app>/icons/<name>.svg")`. Encoding ambiguity gone. The files are also greppable, version-controllable, and reusable across rules.

### Frappe's navbar-toggler markup is `<svg><use href="#icon-menu"/></svg>`, not Bootstrap's `.navbar-toggler-icon` span

Wrote CSS targeting Bootstrap's standard `.navbar-toggler-icon` span class to skin the mobile hamburger. The class doesn't exist in Frappe's rendered navbar — Frappe outputs `<button class="navbar-toggler"><span><svg class="icon icon-lg"><use href="#icon-menu"/></svg></span></button>` and references an SVG sprite for the icon.

**Lesson:** to override the toggler icon, hide the inner `<span>/<svg>` and put the icon as a `background-image` on the button itself:

```css
.navbar-toggler { background-image: url("/assets/<app>/icons/menu.svg") !important; ... }
.navbar-toggler > span, .navbar-toggler svg { display: none !important; }
```

### Frappe auto-prepends `©` to the copyright field

Set `Website Settings.copyright = "© 2026 Locally Twisted · Accessibility · Refund Policy"`. Rendered output: `© © 2026 Locally Twisted · ...`. Frappe's footer template prepends a `©` glyph itself; supplying one in the field value gives you doubles.

**Lesson:** copyright field value should NOT begin with `©`. Start with the year.

### Editable pip install (`uv pip install -e <app>`) lives in container's writable layer; lost on `docker compose up --force-recreate`

After scaffolding the custom Frappe app inside the backend container with `bench new-app`, the editable Python package was registered via `uv pip install -e /home/frappe/frappe-bench/apps/locally_twisted` so `import locally_twisted` resolves and Frappe's hook system picks up `hooks.py`. Then a docker compose recreate (e.g., to apply a new bind-mount) destroyed the container's writable layer and the editable install with it. New container had the app's source via the bind-mount, but no `locally_twisted` in the Python env — every page rendered HTTP 500 with `ModuleNotFoundError: No module named 'locally_twisted'`.

**Lesson:** the editable pip install must be re-run after every container recreation, in EVERY frappe-image service that imports app code (backend, queue-long, queue-short, scheduler — websocket runs Node so doesn't need it). The clean long-term fix is to bake the install step into the `configurator` service's command in `pwd.yml` so it runs automatically on stack startup. **Until that's done**, treat container recreations like a manual checkpoint that requires:

```bash
for svc in backend queue-long queue-short scheduler; do
  docker exec "<project>-${svc}-1" \
    uv pip install -e /home/frappe/frappe-bench/apps/<app> --python /home/frappe/frappe-bench/env/bin/python
done
docker restart <project>-backend-1 <project>-queue-long-1 <project>-queue-short-1 <project>-scheduler-1
```

### `.web-footer`'s computed height "constraint" — RESOLVED 2026-04-26 (current session)

The previous instance reported `.web-footer`'s computed height was "mysteriously constrained to ~305 px" while its child `.container` was 755 px tall. This was logged as UNRESOLVED.

**Root cause from reading Frappe's actual source in the running container** (`docker exec backend cat /home/frappe/frappe-bench/apps/frappe/frappe/public/scss/website/footer.scss`): there is **no `max-height` rule on `.web-footer`**. The actual SCSS is:

```scss
.web-footer {
  padding: 3rem 0;
  min-height: 140px;
  background-color: var(--fg-color);
  border-top: 1px solid $border-color;
  margin-top: auto;
}
```

The `margin-top: auto` participates in Frappe's intended sticky-footer pattern: `apps/frappe/frappe/public/scss/website/base.scss` declares `html { height: 100% }` and `body { display: flex; flex-direction: column }`. The footer is the last flex child and `margin-top: auto` pushes it to the bottom of body when the main content is shorter than viewport. **This is not a bug — this is Frappe's intended layout.**

The previous "305 px constraint" observation likely came from one or more of:
1. The previous instance's own `lt-theme.css` `!important` chain on `.web-footer` interacting with the body's flex column in unexpected ways
2. Measurement confusion between multiple `.container` elements on the page (the header has a `.container` too; the previous DOM-fact dump may have grabbed the wrong one)
3. The page state at measurement time differed from what the screenshot rendered (cached CSS bundle, stale cookies, etc.)

**The right move forward** (per the agency `frappe-conventions.md` "Verified against source — 2026-04-26" appendix and per GL's directive "work WITHIN Frappe, don't fight it"):

1. Override the Jinja partial at `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html`. Your override resolves before Frappe's standard one. Use whatever class names you want — no inheritance from `.web-footer` necessary.
2. Strip the `!important` chains from `lt-theme.css`. They were band-aids around the wrong problem.
3. Use `web_include_css` (already wired in `hooks.py`) for the LT theme CSS — it loads AFTER the website bundle in cascade order, so equal-specificity rules win without `!important`.
4. For SCSS that needs Frappe's variables and to be compiled into the bundle, register `website_theme_scss` in `hooks.py` and create `apps/locally_twisted/locally_twisted/public/scss/website.scss`.

**Status: resolved.** Slice 2 redo can proceed using the right primitives; the framework was never the obstacle.

---

## 2026-04-26 — "Jeff doesn't know" needs more precision than the standing docs gave it

**What happened:** Inherited HANDOFF.md and CLAUDE.md framing that read, in effect, "Jeff Kimber doesn't know about the prior failed Odoo attempt; no artifact on disk should leak that." Operated under that assumption for the first part of this session. GL corrected the framing directly: Jeff knows about the Odoo attempt and has lived its failures over months of paid work. What Jeff does not yet know is that GL has decided to migrate infrastructure entirely to ERPNext. The hidden piece is the platform pivot, not the existence of the prior work.

**What was learned:**

1. **One-line summaries of trust dynamics lose load-bearing nuance.** "Jeff doesn't know about the prior Odoo attempt" is a paraphrase that erased months of paid work Jeff has been watching firsthand. A future instance reading the cleaner version might guard the wrong fact and either over-disclose (treating the prior work as something to confess) or under-disclose (acting in conversation as if Odoo never existed, which would be jarring against Jeff's actual experience).

2. **The actual operating rule (per GL 2026-04-26):** Jeff knows the Odoo work happened and watched it struggle. He does not know that GL is migrating off Odoo entirely. The platform pivot stays internal until Phase 1 (customer-facing site + storefront) is demo-ready. The recovery move is showing Jeff a working customer-facing site as the result of months of work, not announcing a do-over.

3. **Operational implication:** Phase 1's bar is not "functional." It is "visibly polished enough that Jeff's reaction is 'oh, this is real.'" The visual quality is what makes the platform pivot land as "I built you something good" rather than "I had to throw it all out." Functional-but-ugly fails the demo even if every test passes.

**Generalizable lesson:** When standing docs use "X doesn't know Y" to encode a trust-state, ask whether Y is the precise fact being protected or a paraphrase of one. Paraphrases compound: each instance restates them slightly cleaner, and over a few sessions the actual nuance is lost. For load-bearing trust dynamics, ask GL once for the precise statement and write that verbatim. Don't tidy. (This receipt also lives in project memory at `<memory>/jeff_trust_and_phase_1_demo_stakes.md` — auto-injected on session start.)

---

## 2026-04-26 — A project frame can be wrong, not just labels. Reframe early, propagate everywhere, delete the old.

**What happened:** Inherited a project framed as "Odoo → ERPNext migration." Spent half a session deepening planning artifacts on top of that framing (PROJECT.md, ROADMAP.md, queue, decisions log, HANDOFF, scripts, capability docs). Then GL revealed: there is no production Odoo — it failed in testing, never went live, Jeff doesn't know. The frame wasn't just labeled wrong; it was structurally wrong. The 10-phase ROADMAP organized work around model translations from a system that's reference material, not a system being migrated. The "stealth migration / trust damage from prior failures" Core Value referenced damage Jeff never experienced.

**What was learned:**
1. **Surface framing assumptions BEFORE building artifacts on top of them.** The first instance who built the planning machinery never asked "wait, is this even a migration?" because the standing files said it was. Cost: significant churn to undo.
2. **A wrong frame deepens its own debt.** Every artifact written under the wrong frame must either be rewritten or deleted. The cost compounds with every layer.
3. **Reframing requires deletion, not just rewriting.** Stale REQUIREMENTS.md tied to old phases. Stale `phases/01-inventory/` research from a deferred-then-renamed phase. Empty `Locally-Twisted-Frontend/` placeholder. All deleted in this session. GitHub is the archive; we store nothing unnecessary.
4. **The reframe needs a "Reference Disposition" section in CLAUDE.md** so future instances can't accidentally re-introduce the old framing by reaching into the prior dir for resources. Make it explicit: these things will be retired; future instances must NOT assume they exist.

**Generalizable lesson:** When inheriting a project, sanity-check the frame against the human's current reality before extending the planning artifacts. Three honest questions cover most cases: "Who is this FOR (and do they know what we're doing for them)?" "What is this REPLACING (vs. building from scratch)?" "What does success LOOK LIKE on demo day?" If any of the answers contradicts what the standing docs assume, stop and reframe. The cost of pausing is low; the cost of compounding the wrong frame is high.

---

## 2026-04-26 — Don't trust API silent success — verify the field landed where you think

**What happened:** Set ERPNext Website Settings.`website_theme_css` via the Frappe `set_value` API. API returned `{"message": {...}}` — looked like success. Curled the served homepage; CSS wasn't in the head. Tried again with stronger parsing; still nothing. Spent two cycles debugging "why isn't my CSS appearing" before checking the DocType field list and finding `website_theme_css` doesn't exist as a field on Website Settings. The right field is `head_html`. Frappe's set_value silently accepted the write to the non-existent field.

**Generalizable lesson:** When a write API returns success but the visible state doesn't change, before re-trying the write, **list the actual fields available on the DocType**. Don't trust field names from memory or pattern-matching. The Frappe API for inspecting a DocType: `GET /api/resource/DocType/<NAME>` returns the full schema including the field list. Spend 30 seconds checking the schema before another 5 minutes debugging the wrong field.

---

## 2026-04-26 — WebFetch failure ≠ site down. Verify with a second tool before alarming the human.

**What happened:** WebFetch tool returned `ECONNREFUSED` for `http://5.78.136.133/`. Reported to GL "the live site is DOWN." This was wrong — `curl -sI` returned HTTP 200 immediately. The WebFetch tool just doesn't handle raw-IP URLs through its proxy layer; it has nothing to do with the site's actual reachability.

**Generalizable lesson:** When a network-dependent tool fails, the failure could be the tool, the network path, the URL format, or the actual server. Reach for a second tool (curl, ping, browser screenshot) before reporting a server outage to the human. **The cost of a false-alarm-then-correction is the same anti-pattern as "report without watching" — it withdraws trust from your reporting.**

---

## 2026-04-26 — Cloudflare blocks default Python urllib User-Agent

**What happened:** First call to `https://api.together.xyz/v1/images/generations` returned HTTP 403 with Cloudflare error code 1010. Worked immediately after adding a real browser User-Agent header.

**Generalizable lesson:** When a third-party API returns 403 + Cloudflare error, the User-Agent is the first thing to check. Default urllib UA looks like `Python-urllib/3.x` and is blocked by many Cloudflare-protected APIs as a generic-bot signature. Always pass `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36` (or similar real-browser string) for any API call from Python.

---

## 2026-04-26 — `bench set-config host_name` is not enough — `frappe_docker` nginx rewrites the Origin header BEFORE socketio sees it

**What happened:** GL still saw `socketio_client.js:69 Error connecting to socket.io: Invalid origin` after Trellis's earlier fix. Server-side `bench --site frontend show-config` showed `host_name: http://localhost:8081` set correctly. `curl /socket.io/?EIO=4&transport=polling` returned HTTP 200 from the host. The websocket service itself was up and listening. Yet the browser kept rejecting.

**Root cause:** `frappe_docker`'s nginx config at `/etc/nginx/conf.d/frappe.conf:47` contains:
```
proxy_set_header Origin $proxy_x_forwarded_proto://frontend;
```
That line REWRITES the browser's `Origin: http://localhost:8081` header to `Origin: http://frontend` (the internal Docker service hostname) before proxying to the socketio upstream. The socketio Node service is configured with `origin: true` (echo whatever Origin you receive back as `Access-Control-Allow-Origin`). So the response comes back as `Access-Control-Allow-Origin: http://frontend` — which doesn't match the browser's actual origin → CORS rejection → "Invalid origin" surface in the JS client. **Trellis's earlier `bench set-config host_name` fix targeted the wrong layer entirely.**

**Fix (verified working):** Patch the in-container nginx config to pass through the original Origin:
```
proxy_set_header Origin $http_origin;
```
Then `nginx -s reload` (no container restart needed → no DNS cache trap).

This project ships the patch as `scripts/fix/patch_nginx_socketio_origin.py` (run via `docker cp` + `docker exec`). The patch is NOT persistent across container recreation — it edits the in-container file. For permanent fix, mount a custom `frappe.conf` via a docker-compose override.

**Verify:**
```bash
curl -sS -i "http://localhost:8081/socket.io/?EIO=4&transport=polling" -H "Origin: http://localhost:8081" | grep -i access-control-allow-origin
# Expected: Access-Control-Allow-Origin: http://localhost:8081  (matches what you sent)
```

**Why the upstream `frappe_docker` design rewrites Origin:** the assumption is TLS terminated at a load balancer in front of nginx, with consistent internal hostname `frontend`. For browser-direct localhost access (no LB, no TLS), pass-through is correct. Production deployments to Frappe Cloud won't hit this because Frappe Cloud uses its own nginx layer.

**Generalizable lesson:** When a CORS / origin error persists after the obvious config fix, check whether nginx is rewriting headers BEFORE the upstream sees them. `proxy_set_header` lines are easy to miss — but they silently override what the upstream thinks the request looks like. (Also captured in global lessons-learned 2026-04-26.)

---

## 2026-04-25 evening — Frappe socket.io throws "Invalid origin" when site is on a non-default port

**What happened:** Opened the LT ERPNext UI at `http://localhost:8081`. Browser console showed `Error connecting to socket.io: Invalid origin` and `GET /socket.io/... → 400`. Real-time UI features (notifications, live updates, multi-tab sync) silently broken.

**Root cause (incomplete — see 2026-04-26 entry above for the actual fix):** `frappe_docker`'s `pwd.yml` brings the site up assuming Frappe's default port 8080. We map host port 8081→8080 inside the container for LT (so BBC and LT can both run). The `host_name` in the site's config was unset, so Frappe's `get_allowed_origins()` defaulted to something that didn't include `http://localhost:8081`. The socketio server (Node, separate container) rejects mismatched Origin headers as a CSRF defense.

**The trap that bit me on first attempt:** I restarted only the websocket container. That fixed the origin check (it re-read host_name from site config), but Docker assigned the websocket container a *new internal IP* on restart. The frontend (nginx) container had cached the OLD IP from its initial DNS resolution and kept trying to proxy `/socket.io/` to the dead address — producing **502 Bad Gateway** with `connect() failed (113: No route to host)` in nginx's error log. Restarting the websocket without restarting nginx turned an "Invalid origin / 400" symptom into a "No route to host / 502" symptom. nginx in `frappe_docker` does not use a `resolver` directive, so it never re-resolves on its own.

The compose-level `restart` (or restarting frontend + websocket together) avoids this entirely because Docker re-establishes the network and nginx re-resolves on its first proxy attempt.

**What to do for any future site spinup at non-default port:** Run the `set-config host_name` step immediately after `bench new-site` finishes, BEFORE the user touches the UI. AND apply the nginx Origin patch (per 2026-04-26 entry).

**Generalizable lesson:** in `frappe_docker` (and similar nginx + Compose stacks), restarting an upstream container without also bouncing nginx will give you a confusing 502 because nginx caches DNS at startup. Default to `docker compose restart` for the whole project, not single-container `docker restart`, when troubleshooting the data plane.

---

## 2026-04-25 — `gsd-tools commit` returns "nothing_to_commit" because the post-Write auto-commit hook beats it

**What happened:** `node gsd-tools.cjs commit "..." --files PROJECT.md` repeatedly returned `{"committed": false, "reason": "nothing_to_commit"}` even though the file was clearly new. Confused me into staging manually.

**Root cause:** This workspace has a post-Write hook that auto-commits files after the Write/Edit tool succeeds. By the time the GSD `commit` call runs, the file is already in HEAD with an "auto: Write ..." commit message. There's nothing for `gsd-tools commit` to commit.

**What to do:** When `nothing_to_commit` returns, run `git log --oneline -3` to confirm the auto-commit happened (look for `auto: Write FILENAME`). If yes, the workflow can proceed — the file IS in version control, just under a different commit message than the GSD workflow expected. The workflow's commit calls are belt-and-suspenders; the auto-hook is the suspenders.

---

## 2026-04-25 — `git status` on Windows hides freshly-staged dotfiles in the porcelain output

**What happened:** Staged `.gitignore` and `.planning/PROJECT.md` via `git add`. `git ls-files --stage` showed both files indexed with their hashes. `git status --short` and `git status` showed neither as staged — and showed all the OTHER files as untracked. Misleading.

**Root cause:** Unknown — possibly Git Bash + Windows interaction with first-commit-on-empty-repo state. The plumbing (ls-files, commit, ls-tree) was correct; only the porcelain (status) lied.

**What to do:** Trust `git ls-files --stage` and `git ls-tree -r HEAD --name-only` over `git status` when verifying first-commit state on Windows. The actual commit succeeds; status display is unreliable.

---

## 2026-04-25 — Frappe `pwd.yml` defaults to v16.15.1 image; v15 line is stable but you must pin manually

**What happened:** Cloned `frappe_docker`, expected to bring up ERPNext v15. The default `pwd.yml` pinned all 8 service images to `frappe/erpnext:v16.15.1`. Had to swap them all to `frappe/erpnext:v15.105.0` before starting.

**What to do:** When installing Frappe via `frappe_docker`, immediately edit `pwd.yml` to pin the desired tag *before* `docker compose up`. The rolling `v15` tag exists and points to the latest patch (currently `v15.105.0`), but pin to a specific patch for reproducibility — rolling tags will silently pull a newer patch on next `up`. (Also see agency-level v15-stability standing rule in `Built_by_Cameron/CLAUDE.md`.)

---

## 2026-04-25 — Frappe images are large; cache them on the first install, second site comes up in seconds

**What happened:** First `docker compose up` for a Frappe stack took several minutes (image pull, layer extraction). The second compose project for LT used the same `frappe/erpnext:v15.105.0` image and came up in 18 seconds — Docker recognized the layers and just retagged.

**What to do:** When spinning up multiple ERPNext sites locally, reuse the same image tag across compose projects. Each site gets its own volumes (named differently per project) but shares the image. This is fast and disk-efficient.

---

## 2026-04-25 — WSL2 default RAM allocation is below ERPNext's working set; bump `.wslconfig` to 8 GB before installing

**What happened:** Initial WSL2 had 1.5 GB RAM cap (set in `.wslconfig` from a prior expedition). Frappe stack runs MariaDB + Redis + web + socketio + scheduler + 2 worker queues — 1.5 GB was below ERPNext's 4 GB minimum. Visible in `docker info` as `MemTotal: ~1.47 GB`.

**What to do:** Edit `C:\Users\baenb\.wslconfig` `[wsl2]` section to `memory=8GB processors=4 swap=2GB` (the machine has 47.7 GB total — 8 GB is conservative). After edit, `wsl --shutdown` then run any docker command to wake the daemon with the new limits. Verify with `docker info | grep MemTotal`.

---

## 2026-04-25 — Frappe Cloud Sites plan is $5/mo per site, not $25-100; transfer is self-service

**What happened:** Quoted GL "$25-100/mo per client" early in a Frappe Cloud cost discussion based on bad memory of the pricing. GL was about to make decisions on bad numbers. Re-checked the actual pricing page.

**Real numbers (2026-04, verified at frappe.io/cloud/pricing):**
- **Sites plan**: starts at $5/month per site, includes custom apps, custom domain, SSH access
- **Servers plan**: starts at $20/month for the whole server, unlimited sites/benches
- **Free trial**: 14 days, no payment method

**Site transfer mechanism (verified at discuss.frappe.io/t/transfer-ownership-on-frappe-cloud/122800):** Self-service via the dashboard's Actions tab. Receiving Frappe Cloud team must exist (have GL's client create their own account first). Server-level transfer requires a support ticket; site-level does not.

**What to do:** When quoting hosting costs, verify against the live pricing page. Frappe's pricing has changed; training-data memory is unreliable. The cheap-and-transferable model is the right fit for the agency's "build → sell → transfer ownership" pattern.

---

## 2026-04-25 — When GL forbids touching one file, the boundary is the file (don't extrapolate to "GL must do the work")

**What happened:** GL said "leave odoo specific scripts and skills alone — we need to create ERPNext specific ones." I extrapolated this to "GL must be the executor of any production-touching work" and drafted a human-in-the-loop pattern where GL would paste production query results back to me. GL corrected: "the standard process is YOU preparing the script and executing it once it's been researched and built correctly."

**What to do:** When GL sets a boundary on a *file*, the boundary is on that file. Build new tooling elsewhere. The standard process — agent builds, agent tests, agent executes — still applies. Don't outsource execution to GL based on a misread of the boundary's scope.

---

## 2026-04-25 — Building infrastructure ≠ building the thing GL asked for

**What happened:** Spent significant tokens scaffolding GSD project structure (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, config), then planning Phase 1 with research + planner + checker + revision iterations + threat models + validation strategies. Two ERPNext sites running but completely empty. Zero translation from Odoo had occurred. GL: "you haven't even rebuilt the site in ERPNext?! Focus on the rebuild."

**What to do:** When GL asks for a *thing*, the score is "is the thing built yet?" not "is there a beautiful planning artifact for the thing." Set up the minimum scaffolding required to start building, then start building. The planning machinery is meant to *serve* the build, not to *be* the build. If you find yourself iterating planner-checker loops on a phase that hasn't moved one bit closer to the deliverable, stop and start doing the deliverable.

This is the global anti-pattern #2 (Drift from GL's actual ask). Receipt added to `anti-gl-patterns.md` (project-local).
