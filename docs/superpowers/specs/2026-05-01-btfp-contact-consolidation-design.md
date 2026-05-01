# BTFP Refresh And Contact Consolidation Design

Date: 2026-05-01
Status: Approved design, pending implementation plan

## Goal

Create one customer inquiry surface for Locally Twisted while refreshing the Balloon Twisting & Face Painting page with real content from the Hetzner reference and the current ERPNext design direction.

The customer-facing entry point is `/contact`. ERPNext still keeps the internal Lead, Contact, Communication, and later CRM cascade architecture.

## Decisions

### Canonical Inquiry Route

`/contact` is the only meaningful public inquiry page.

It handles:

- general questions
- event inquiries
- booking-style intake
- Jeff texting a link to someone who already called
- service-page CTAs

Guided contact URLs may prefill context:

- `/contact?intent=quick`
- `/contact?service=btfp`
- `/contact?service=twisting`
- `/contact?service=face-painting`

`/book` should not remain a separate public page. If the route remains for compatibility, it should redirect to `/contact?intent=quick` and should not appear in navigation, footer links, docs, CTAs, or customer-facing copy.

### Internal ERPNext Architecture

The consolidation is only on the customer-facing surface.

All inquiry paths still feed the same ERPNext architecture:

- Lead creation
- Contact deduplication
- Communication timeline entry
- auto-acknowledgment behavior
- future CRM/booking cascade work

No second form pipeline should be introduced for BTFP.

## Balloon Twisting & Face Painting Page

`/balloon-twisting-and-face-painting` becomes an editorial service page, not a form page.

It should use a hybrid direction:

- real content and facts from `http://5.78.136.133/balloon-twisting-and-face-painting`
- current ERPNext visual direction already present locally
- relevant design-contest influence: editorial layout, spec tables, quiet CTAs, restrained accents

### Page Structure

1. Hero/intro with calm service positioning.
2. Two service cards: Balloon Twisting and Face Painting.
3. Real photos from the existing app assets.
4. Spec-table facts replacing placeholder text.
5. Booking/process section that explains what happens next.
6. Event-type section.
7. FAQ section using concrete Hetzner content.
8. CTAs pointing to `/contact?service=btfp`.

### Facts To Carry Forward

Use verified Hetzner content where specific:

- `$130 first hour, $115 each additional hour - per artist`
- `$50 deposit per artist at booking`
- balloon artist typically serves `15-20 children per hour`
- face painting is a separate skill staffed separately from balloon twisting
- for larger events or events needing both services at once, staff one of each
- outdoor events are supported
- direct sun and wind affect balloon longevity
- recommended booking lead time: `2-3 weeks` for standard events, `4-6 weeks` for weddings and large corporate events
- service area: Wasatch Front including Salt Lake City, Provo, Ogden, Park City, surrounding areas, and regular travel to Logan/other Utah locations

### Deposit CTA

Do not include a `Pay $50 Deposit` checkout CTA until the ERPNext deposit product/payment flow is verified.

The page may mention that a deposit holds the date, but the customer action should be to start the contact flow.

### Removed From BTFP Page

Remove or retire the embedded BTFP-specific form and page-local submit behavior from the customer flow.

The page should link to the canonical contact form instead of posting to a separate endpoint.

## Contact Page Behavior

`/contact` uses the existing shared inquiry form, with smarter query-param prefill.

Expected behavior:

- `/contact` renders the standard all-purpose inquiry form.
- `/contact?service=btfp` preselects Balloon Twisting and Face Painting.
- `/contact?service=twisting` preselects Balloon Twisting.
- `/contact?service=face-painting` preselects Face Painting.
- `/contact?intent=quick` renders the same form with copy suitable for Jeff texting someone a fast follow-up link.

The page should also have link-preview metadata suitable for text messages:

- title: `Contact Locally Twisted`
- description: `Tell us about your celebration. Balloon decor, twisting, and face painting along the Wasatch Front.`
- image: use an existing brand/logo/balloon dog image if available and appropriate

## Error Handling

Customer-facing form errors must be visible and recoverable.

Backend failures must be logged through Frappe error logging. Form submission should not fail silently or show a blank page.

## Verification Requirements

Implementation is done only after verifying:

- `/balloon-twisting-and-face-painting` returns HTTP 200.
- BTFP page no longer presents an embedded BTFP form as the inquiry path.
- BTFP CTAs route to `/contact?service=btfp`.
- `/contact?service=btfp` visibly preselects Balloon Twisting and Face Painting.
- `/contact?service=twisting` visibly preselects Balloon Twisting.
- `/contact?service=face-painting` visibly preselects Face Painting.
- `/book`, if present, redirects to `/contact?intent=quick`.
- Contact form submission still creates a Lead and Communication.
- Website cache is cleared after Jinja/CSS/controller edits.
- Desktop and mobile screenshots are inspected for both BTFP and contact pages.

## Out Of Scope For This Slice

- Building or verifying the deposit checkout flow.
- Redesigning the whole contact page beyond what is necessary for canonical inquiry behavior.
- Reworking ERPNext Lead schema.
- Rewriting unrelated webshop/cart behavior.
- New legal or policy language beyond already sourced business facts.

