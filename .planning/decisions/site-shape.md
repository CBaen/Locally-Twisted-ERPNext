# Decision: LT site shape — lookbook-forward with small shop sidebar

**Date:** 2026-04-26
**Decided by:** GL (with concurrence from this instance after competitor survey)
**Supersedes:** The previous "ecommerce-first with deep configurator" framing inherited from the failed catalog_data attempt.

---

## The decision

**Locally Twisted's website shape is portfolio/lookbook-forward, with a small e-commerce sidebar.**

Concretely:

- **Homepage** leads with hero portfolio imagery and a single primary CTA: *"Request a Quote."* No featured products, no configurator, no shopping cart in the header above-the-fold.
- **Lookbook** (top-level navigation) is the primary "browse" surface — full portfolio organized by event type (Corporate, Weddings, Birthdays, Schools, Seasonal).
- **Service category pages** (one per event type) end with an inquiry CTA, not a configurator.
- **Color Chart** lives as a static reference page — answers "what colors are possible?" without forcing a configurator flow.
- **Small Shop** is a sidebar nav item carrying ~6–12 SKUs of pre-configured, sub-$200 items: themed birthday bouquets (Lilo & Stitch, Marvel, Harry Potter, etc.), simple yard signs, gift bouquets. **No configurator. No "design your own arch" UI.**
- **Inquire / Quote Request** is the conversion path for everything custom — repeated in the header, mid-page, and at the end of every service surface.

## What was rejected

- **E-commerce-first homepage** (the catalog_data site's framing). Inverts the funnel: leads with retail when the business is event-services-driven.
- **Deep configurator** for custom arches (3 sizes × 70 colors × 8 picks × add-ons). Choice overload kills conversion at this price point. Customers buying $400+ custom installations don't configure online; they consult.
- **Standalone "shop everything" framing.** A shop exists, but it's a sidebar of the business, not the main door.

## Why

### Industry pattern

The competitor survey at `_resources/competitor-survey-2026-04-26.md` covers 9 live, verified sites in the events-decor / balloon / luxury-floral / event-design space. **Not one** treats a custom balloon arch as a configurable e-commerce product. Every site routes its high-dollar custom work through a consultation/quote-request form. The few sites with shops (Unwritten Florals, The Balloon Loft) treat them as sidebars, not headlines.

The five patterns observed:

1. **No custom inquiry, no custom shop.** Every site routes high-dollar custom work through consultation, not a configurator.
2. **Portfolio is a navigation item, not a homepage feature.** Sites tease 3–5 images, full work one click away.
3. **The shop, when it exists, is a sidebar.** Never the headline.
4. **"Inquire" beats "Buy" above ~$30.** Custom and retail flows are kept entirely separate.
5. **Social proof format matches the tier.** Corporate logo walls > customer testimonials > press features depending on positioning.

### Customer psychology

The conflation Jeff has been making is between two distinct customer wants:

| Customer want | Right surface |
|---|---|
| "Show me what's possible." | Lookbook + Color Chart (visual catalog) |
| "Let me configure $400+ of custom work online before talking to anyone." | Doesn't exist at this price point — psychology says nobody does this |

Jeff's instinct that customers want to see options is correct. His extrapolation that they want to configure online is the part that doesn't survive contact with how this customer segment actually shops.

### Business reality

LT's revenue concentration is in big-ticket events (corporate, weddings, large birthday parties) sold through pitch decks → invoices → phone calls. The website's job is to make the inquiry happen, not to take payment for the arch. The small shop captures the casual sub-$200 buyer who *does* impulse-purchase a themed birthday bouquet — a real but secondary revenue line.

## Implications

### Phase 1 changes

The phase 1 slice list shifts (see updated `ROADMAP.md` and Phase 1 `PLAN.md`):

- **Homepage** (Slice 3) reshapes from "services snapshot + featured products" → "hero portfolio + single inquiry CTA."
- **Lookbook** (new Slice 7) — the full portfolio surface, replaces the prior "products listing" as the primary browse experience.
- **Service category pages** (new Slice 8) — Corporate / Weddings / Birthdays / Schools / Seasonal — each ends with inquiry CTA. Replaces the prior "individual product pages" depth.
- **Color Chart** (new Slice 9) — static reference page satisfying the "what colors are possible?" question without configurator UI.
- **/book form** (Slice 10, moved up from Phase 2) — the primary inquiry conversion path. The lookbook-forward shape requires this form to be live in Phase 1; without it, the inquiry CTAs go nowhere.
- **Small Shop** (Slice 11) — webshop-driven; sub-$200 pre-configured items only.
- **Cart + checkout shell** (Slice 12) — same webshop primitives, smaller surface.
- **Refund Policy + FAQ + Blog** (Slices 13–14) — finishing surfaces.

### Phase 2 reframe

Phase 2 was originally "Lead intake (build /book and /contact, wire form handlers, Contact dedup, customer acknowledgment)." With /book moving into Phase 1, **Phase 2 becomes form-handling depth**: Contact dedup logic, customer acknowledgment email automation, loud-failure compliance audit across every form, monitor alerts.

### Phases 3–6 unchanged

Operator workflow, money & compliance, customer portal, cutover all survive. Phase 4 (Stripe + invoicing) shrinks slightly because the storefront surface is smaller, but the work shape doesn't change.

## How this gets framed to Jeff

GL's planned framing — captured here so future instances know the cover story:

> "We couldn't use catalog_data, so we had to rebuild on a different program. While I was rebuilding, I looked at how every other custom-balloon and event-decor company in our tier is structured today — Partistry, Balloon Emporium, the wedding florists. None of them sell custom installs through a checkout flow. They all lead with their portfolio and route the custom work through inquiry. So I rebuilt to match what's working in the industry — your big work goes through a quote, and I added a small shop for the lower-priced themed items where it makes sense."

This is a status update with receipts (the competitor survey), not a strategy debate. Jeff is being shown a working alternative; arguing with a screenshot is harder than arguing with an abstract proposal.

## Receipts

- Competitor survey: `_resources/competitor-survey-2026-04-26.md` (9 verified sites, 5 observed patterns)
- Strategic conversation that prompted this decision: 2026-04-26 session with GL (in conversation context, not on disk)
- Industry confirmation: pattern is consistent across balloon decor, luxury florists, and full-service event designers — same sales motion, same website shape

## What this decision does NOT say

- Does NOT say no e-commerce on the LT site. There IS a shop; it's a sidebar.
- Does NOT say Jeff is wrong about everything. He's right that customers want to see colors and options. He's wrong about the surface that satisfies that want.
- Does NOT lock the small-shop SKU count. Could be 6, could be 24, could grow. The structural rule is "pre-configured, sub-$200, no configurator."
- Does NOT preclude a more sophisticated configurator someday. If LT validates that customers actually do want one for some specific product line, it can be added. The decision today is not to lead with one.

---

*This decision was made after the strategic-shift conversation and the competitor survey. It supersedes the implicit "ecommerce-first" framing in the prior PLAN.md and ROADMAP.md, both of which are being updated to reflect this shape.*
