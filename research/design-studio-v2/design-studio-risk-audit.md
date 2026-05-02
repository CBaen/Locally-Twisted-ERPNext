# Design Studio V2 Risk Audit

Last updated: 2026-05-02 by Codex.

Role: QA, risk, and contradiction audit for the future `Plan Custom Decor` / Design Studio lane.

This is a V2 planning artifact. It is not evidence that a design studio exists on the production site, and it must not be used to delay V1 launch unless a proposed V2 action touches launch-critical routes, forms, checkout, policy pages, navigation, or brand trust.

## Files Read

- `AGENTS.md`
- `.codex/capabilities/INDEX.md`
- `workstreams/design-studio-v2.md`
- `research/design-studio-v2/README.md`
- `research/contest-customizable-event-decor-tool/FINAL-SURFACE.md`
- `research/contest-customizable-event-decor-tool/PRODUCT-DETAILS.md`
- `workstreams/launch-v1-success-contract.md`
- `workstreams/website-launch.md`
- `workstreams/brand-audience-style-reset.md`

## Output File Changed

- Created `research/design-studio-v2/design-studio-risk-audit.md`

## Verified, Inferred, And Needs Approval

Verified from current project docs:

- Design Studio is explicitly a background V2 planning lane, not a V1 blocker.
- V1 launch-critical paths include `/`, `/contact`, `/book`, policy pages, `/shop`, cart, checkout, product/category pages, and visual/accessibility launch quality.
- `/book` is supposed to redirect to `/contact?intent=quick`, not become a separate V1 form.
- The product split is `Ready to Order` for simpler ecommerce and `Plan Custom Decor` for larger consultative installations.
- The intended production direction is Frappe-native, with vanilla JS/Frappe/jQuery preferred for early prototype work and no separate build pipeline unless approved.
- Contest artifacts are source material only, not final product direction.
- Color names are load-bearing; hex values are only approximations until Jeff provides approved mappings.
- Balloon decor construction rules differ by type: classic arches/columns/backdrops use cluster logic; organic garlands/organic pieces use different placement logic; drops are representational after release.
- Locally Twisted is the customer-facing brand. Jeff is the owner/process source, not the center of the brand.

Inferred:

- The first prototype can be useful only if it is deliberately narrow and cannot be confused with the live launch offering.
- The largest near-term risk is not code complexity; it is accidentally turning a V2 concept into a V1 dependency or a misleading customer promise.
- A design rendering that looks polished but ignores construction physics would be worse than no rendering because it would create bad expectations for sales follow-up.
- Save/share is likely high-value for corporate, school, civic, venue, and premium private buyers, but it has privacy and token risks that need design before production.

Needs GL/Jeff approval:

- Approved customer-facing name: `Plan Custom Decor`, `Design Studio`, or another label.
- Whether any V1 teaser or guided inquiry copy should mention the future studio.
- Approved balloon color hex/Pantone approximations and color-name display rules.
- Which scale references are acceptable and not misleading.
- Whether public token share links are acceptable, or whether saved designs must be account-only.
- Whether first prototype includes organic garland, or waits until classic arch/columns/backdrop rendering is proven.

## Top 10 Risks, Ordered By Severity

1. V2 work contaminates V1 launch scope.

   Severity: Critical.

   Evidence: `launch-v1-success-contract.md` explicitly defers the Design Studio/configurator until after V1. `website-launch.md` lists active launch gates around inquiry, policy, shop, visual QA, and checkout.

   Risk: Any prototype work that touches `/contact`, `/book`, checkout, shop product logic, navigation, shared CSS, or public route behavior can slow launch or create a customer-facing broken path.

   Mitigation: Keep V2 prototype and specs isolated until the controller approves implementation. No edits to V1 routes, current CSS/JS, apps, contact schema, checkout, or nav from this lane.

2. Misleading render creates false sales promises.

   Severity: Critical.

   Evidence: `PRODUCT-DETAILS.md` says construction physics are load-bearing and designs that violate them produce un-buildable mockups. `design-studio-v2.md` warns against pretending a planning rendering is a final engineering blueprint.

   Risk: Customers may treat the visual as an exact install promise, while Jeff/Locally Twisted may need to change structure, scale, color placement, or safety constraints during quoting.

   Mitigation: Block prototype work until physics rules are explicit enough to reject bad renderings. Production must label visuals as planning concepts, not guaranteed engineering drawings.

3. Scope ballooning into a full configurator too early.

   Severity: High.

   Evidence: `design-studio-v2.md` recommends a narrow first prototype: event context, one primary piece, complementary pieces, organization palette, scale references, summary card, pieces considered, and payload shape.

   Risk: Trying to support all product families, all sizes, add-ons, pricing, organic placement, drops, bouquets, centerpieces, saved accounts, and CRM automation at once will likely stall the lane and increase launch collision risk.

   Mitigation: First prototype should include only classic arch, pair of classic columns, and backdrop/photo-op wall unless GL approves a wider prototype. Organic garland should wait unless the physics lane clears it.

4. Ready-to-order ecommerce and custom planning get blurred.

   Severity: High.

   Evidence: `design-studio-v2.md` creates a hard product split: `Ready to Order` means customer is ready to buy; `Plan Custom Decor` means consultative, multi-piece, stakeholder-heavy planning.

   Risk: Customers may expect custom installs to have cart-like checkout certainty or expect simple products to require planning friction.

   Mitigation: Keep copy, routing, CTAs, and payloads separate. Prototype must not make custom decor feel like a direct purchase flow unless quote logic is explicitly designed and approved.

5. Customer UX overload for non-technical users.

   Severity: High.

   Evidence: Contest synthesis favored C4's visual thumbnails, low cognitive load, plain-language style names, and C2's permission-to-ignore suggestions. Product details include complex math that should not be exposed directly to customers.

   Risk: Color math, cluster counts, density tiers, dimensions, scale, organization palettes, and multi-piece composition can overwhelm users who only want to explain an event.

   Mitigation: Use visual-first choices, plain labels, bounded steps, skip affordances, and one-piece exit. Keep construction math in the renderer and sales payload, not as the main customer experience.

6. Accessibility is treated as a later polish pass.

   Severity: High.

   Evidence: V1 launch gates treat inaccessible controls, clipped text, and mobile issues as launch blockers. The contest artifacts emphasize visual SVG thumbnails and swatches, which are high-risk controls if not labeled and keyboard reachable.

   Risk: Color swatches, SVG style cards, drag/tap regions, ghost suggestions, and share actions may be unusable by keyboard, screen-reader, low-vision, or color-blind customers.

   Mitigation: Prototype spec must require named buttons, visible focus, keyboard navigation, non-color-only labels, readable touch targets, and text alternatives for style thumbnails.

7. Mobile layout fails under real content.

   Severity: Medium-high.

   Evidence: `website-launch.md` recently tracked 320px overflow fixes and requires desktop/mobile screenshots. Design Studio involves dense controls, palette grids, summaries, and visual previews.

   Risk: The studio may look good on desktop but become clipped, horizontally scrolling, or too cramped on small phones, especially with long color names like `Reflex Champagne` and multi-piece summaries.

   Mitigation: Block production integration until mobile layout is verified at narrow widths. Prototype should design mobile-first control stacking, summary collapse, and preview sizing from the start.

8. Frappe-native feasibility is overclaimed from contest mockups.

   Severity: Medium-high.

   Evidence: Contest entries declared Frappe-recreatable and one included `frappe.call()` Lead creation, but `design-studio-v2.md` still lists future DocTypes, methods, save/share, CRM handoff, and payload structure as probable production shape, not completed work.

   Risk: "Frappe-native PASS" from static mockups may be treated as proof that persistence, permissions, guest sessions, token links, CRM updates, and error handling are solved.

   Mitigation: Prototype can prove browser interaction only. Production integration needs a separate Frappe architecture spec, DocType/API review, permission model, and loud-failure testing.

9. Brand drifts back toward toy-like party-store styling.

   Severity: Medium-high.

   Evidence: `brand-audience-style-reset.md` says Locally Twisted should feel like Utah's experienced event balloon decor company and not a small cute party catalog. `design-studio-v2.md` says playful through balloon work, not toy-like UI.

   Risk: The contest's coloring-book language, rainbow-first surfaces, and childlike visual metaphors could undermine the professional/civic/corporate buyer direction.

   Mitigation: Use the contest mechanics selectively, not the contest tone. Customer-facing language should use Locally Twisted/we/us and focus on planning, scale, event context, and useful follow-up.

10. Save/share and stakeholder features leak private event data.

   Severity: Medium-high.

   Evidence: `design-studio-v2.md` lists save/share and stakeholder state as intended outcomes and open decisions. No approved model exists yet for public token links versus account-only saved designs.

   Risk: Shared designs could expose names, emails, phone numbers, company/school names, private event locations, dates, inspiration photos, or quote details through guessable or forwarded links.

   Mitigation: Prototype may use local-only payload examples. Production save/share must wait for approved token/account model, data minimization, expiration/revocation behavior, and privacy copy.

## What Should Block Prototype Work

- No documented physics constraints for the first supported pieces.
- No narrow first-prototype scope.
- No decision on whether organic garland is in or out of the first prototype.
- No clear customer-facing distinction between `Ready to Order` and `Plan Custom Decor`.
- No rule that renderings are planning concepts, not final engineering promises.
- No accessibility baseline for swatches, style cards, SVG previews, and keyboard operation.
- No mobile-first layout plan for the palette, preview, and summary.
- Any plan that requires editing V1 launch-critical files or routes.
- Any plan that requires modifying `apps/`, current CSS/JS, contact forms, checkout, or launch workstreams from this V2 lane.

## What Can Wait Until Production Integration

- Final DocType names and complete schema.
- Full save-to-account behavior.
- Public share-link implementation.
- Full CRM Lead create/update automation.
- Pricing logic.
- Quote document generation.
- Inspiration photo upload and color extraction.
- Full catalog integration.
- Organic garland renderer, if classic shapes prove the first renderer first.
- Drop renderer, bouquet gallery logic, and themed product exceptions.
- Staff-facing Desk workflow polish beyond ensuring the eventual payload is readable.

## Key Decisions

- Keep Design Studio as V2. It should not block V1 launch.
- Use `Plan Custom Decor` for the buyer mode unless GL chooses another customer-facing label.
- Treat contest outputs as a parts bin: C4 for visual-first low-load choices, C2 for palette-aware suggestions, C3 for dual-audience summary, C1 for pieces-considered payload.
- Keep Frappe-native as the production north star.
- Keep first prototype narrow: classic arch, pair of classic columns, and backdrop/photo-op wall are the safest initial proof set.
- Keep color names as the payload truth. Hex approximations are visual aids only until approved.
- Keep Jeff in internal context and sales follow-up, but keep Locally Twisted as the brand.
- Keep balloon decor construction separate from balloon twisting and face painting.

## Risks Or Contradictions

- The contest surface repeatedly uses "coloring book" framing, while the brand reset warns against childlike or small-party-store presentation. The mechanics may be useful; the tone is risky.
- Contest entries claim Frappe-recreatable PASS, but production persistence, permissions, privacy, guest sessions, share links, and CRM update behavior remain unverified.
- The synthesis pipeline includes a CRM Lead payload, while the launch lane says another agent owns form audit and contact/form schema coordination. This is a production integration dependency, not a prototype prerequisite.
- The product details allow any size for arches, columns, garlands, and backdrops, while the first prototype needs bounded controls. Prototype should use common reference points or constrained inputs without implying those are the only real options.
- Customers want brand/team color matching, but approved hex/Pantone mappings are not available. The tool can capture names and intent, but cannot certify exact color matches yet.
- Drops can be visually represented only as proportional mixes after release; any spatial patterning for drops would be misleading.
- Organic pieces are high-value but have artist-led placement and controlled-random rules. They are risky as a first rendering proof.
- Backdrop sizing is a known gap from the contest field. Because backdrops are any-size/sqft-priced, the prototype must either include a simple width x height path or clearly defer exact sizing.
- Save/share is strategically attractive for stakeholders, but it carries privacy risk and cannot be treated as a simple static URL feature.
- Visual proof rules say generated/concept assets must not be presented as completed work. The studio must preserve that same distinction for customer-created renderings.

## Questions For GL/Jeff

- What customer-facing name should win: `Plan Custom Decor`, `Design Studio`, or another label?
- Should V1 mention this future tool at all, or should V1 only use normal inquiry paths?
- Should the first prototype exclude organic garland until classic arch/columns/backdrop rules are proven?
- Which three to five event contexts should the first prototype support: corporate, school, civic, venue, wedding, parade, private party, or other?
- Which scale references are approved for customer-facing use?
- Are organization names, event dates, and inspiration images allowed inside share links, or should share links contain only anonymous design payloads?
- Should share links expire, require an account, or both?
- What exact disclaimer should appear near generated planning visuals?
- Which Locally Twisted color hex approximations are approved for the first customer-facing palette?
- Should the completion summary say `Send to Locally Twisted`, `Send to our team`, or another company-centered CTA?

## Verification Or Source Evidence

- `workstreams/design-studio-v2.md` verifies V2/background status, product split, Frappe-native north star, first prototype boundary, quality gates, and open decisions.
- `research/contest-customizable-event-decor-tool/FINAL-SURFACE.md` verifies the contest synthesis inputs: visual style cards, pre-tinted suggestions, dual-audience summary, and pieces-considered payload.
- `research/contest-customizable-event-decor-tool/PRODUCT-DETAILS.md` verifies construction physics, product distinctions, color-name priority, and known contest gaps.
- `workstreams/launch-v1-success-contract.md` verifies that Design Studio/configurator is deferred until after V1 and identifies launch blockers.
- `workstreams/website-launch.md` verifies active launch lanes, collision points, current launch gates, and the rule not to touch form/schema work without coordination.
- `workstreams/brand-audience-style-reset.md` verifies the brand direction: Locally Twisted as the brand, premium/professional Utah event authority, proof-first imagery, and caution against toy-like styling or founder-dependent copy.
