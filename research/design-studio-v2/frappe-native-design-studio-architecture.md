# Frappe-Native Design Studio Architecture

Last updated: 2026-05-02 by Codex.

Status: background V2 architecture spec only. Do not treat this as implementation approval or proof that a public Design Studio route exists.

## Sources Read

Verified in this pass:

- `AGENTS.md`
- `workstreams/design-studio-v2.md`
- `research/design-studio-v2/README.md`
- `research/contest-customizable-event-decor-tool/FINAL-SURFACE.md`
- `research/contest-customizable-event-decor-tool/PRODUCT-DETAILS.md`
- `workstreams/brand-audience-style-reset.md`
- `apps/locally_twisted/locally_twisted/hooks.py`
- `apps/locally_twisted/locally_twisted/www/contact.py`
- `apps/locally_twisted/locally_twisted/www/contact.html`
- `apps/locally_twisted/locally_twisted/www/book.py`
- `apps/locally_twisted/locally_twisted/www/shop.py`
- `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`
- `apps/locally_twisted/locally_twisted/api/cart.py`
- `apps/locally_twisted/locally_twisted/api/newsletter.py`
- `apps/locally_twisted/locally_twisted/api/product_listing.py`
- `apps/locally_twisted/locally_twisted/api/variant_media.py`
- `apps/locally_twisted/locally_twisted/lead_cascade.py`
- `apps/locally_twisted/locally_twisted/product_options.py`
- `apps/locally_twisted/locally_twisted/public/`
- `.codex/capabilities/INDEX.md`

Not verified in this pass:

- Live browser rendering of any future Design Studio route.
- Current database schema for proposed future DocTypes.
- Whether Jeff has approved final color hex/Pantone mappings, share behavior, or exact CRM labels for the studio.

## Current Frappe Evidence

Verified:

- The project already uses Frappe website pages in `apps/locally_twisted/locally_twisted/www/`.
- Friendly public route aliases live in `website_route_rules` in `hooks.py`.
- Shared website CSS is included with `web_include_css` and cache-bust query strings.
- Shared website JS is included with `web_include_js`.
- Guest-safe public methods use `@frappe.whitelist(allow_guest=True)`.
- Public endpoints use server validation, rate limiting where needed, and loud failure logging through `frappe.log_error`.
- The current inquiry flow creates ERPNext `Lead` records through `locally_twisted.www.book.submit_book_inquiry`.
- `Lead` creation cascades into title cleanup, Contact linking, and customer acknowledgement through `lead_cascade.py`.
- The current Lead service truth is structured in `custom_event_type` child rows, not only free-text notes.
- Existing public JS avoids assuming the full Desk bundle exists on public pages; `lt-newsletter.js` uses direct `/api/method/...` POSTs instead of relying on `frappe.call`.

Inferred:

- The future Design Studio can fit the same local app pattern without a separate app, service, React build, or external frontend runtime.
- Saved design sessions should be first-class Frappe records once production work starts, but the first clickable prototype should remain file/research-based until the spec wave is reconciled.

## Recommended Route Structure

Prototype recommendation:

- Keep the first interactive prototype under `research/design-studio-v2/` as static HTML/CSS/JS or documented mockups.
- Do not add a hidden Frappe route until the controller approves implementation.
- Reason: this lane is explicitly non-launch-critical, current route changes affect shared Frappe website resolution, and other agents are actively changing launch files.

Production recommendation:

- Public customer route: `/plan-custom-decor`
- Frappe page file: `apps/locally_twisted/locally_twisted/www/plan_custom_decor.html`
- Optional controller: `apps/locally_twisted/locally_twisted/www/plan_custom_decor.py`
- Optional route alias in `website_route_rules`: `{"from_route": "/plan-custom-decor", "to_route": "plan_custom_decor"}`
- Saved/share view route: `/design/<token>` or `/plan-custom-decor/<token>`

Route behavior:

- `/shop` remains the Ready to Order ecommerce surface.
- `/plan-custom-decor` is the consultative planning surface for larger multi-piece installations.
- `/contact` remains the canonical human inquiry path.
- Do not make `/book` the Design Studio route. Existing guidance treats `/book` as legacy quick-contact compatibility.

## Public JS And CSS Structure

Prototype:

- Static files may live under `research/design-studio-v2/prototype/` if approved later.
- No production assets should be registered from `hooks.py` during research.

Production:

- JS folder: `apps/locally_twisted/locally_twisted/public/js/design_studio/`
- CSS folder or file:
  - Preferred shared studio CSS: `apps/locally_twisted/locally_twisted/public/css/lt-design-studio.css`
  - Alternative early page-scoped CSS: inline `<style>` in `plan_custom_decor.html` only while the route is still experimental.
- Include strategy:
  - Add studio JS/CSS globally through `web_include_js` / `web_include_css` only if the file self-detects `[data-lt-design-studio]` and exits on other pages.
  - Better production option: page template includes route-specific script tags so unrelated V1 pages do not download studio code.
- JS modules:
  - `state.js`: design payload state, schema version, undoable updates.
  - `palette.js`: approved named color list and closest-match metadata.
  - `rules.js`: client-side rendering rules mirrored from server-side validated rules.
  - `renderer-svg.js`: inline SVG preview for arch, columns, backdrop, and later controlled organic work.
  - `api.js`: direct `/api/method/...` POST wrapper with CSRF, response parsing, and visible error handling.
  - `index.js`: DOM binding for `[data-lt-design-studio]`.

Do not use:

- A separate Next/React app.
- A standalone service.
- A separate build system.
- `head_html` CSS injection.

Those choices are only justified if vanilla JS plus Frappe website pages cannot meet a tested requirement.

## Future DocType Shape

Recommended production records:

- `LT Decor Design`
  - Owner record for one saved design session.
  - Fields:
    - `title`
    - `status`: Draft, Shared, Submitted, Converted, Archived
    - `schema_version`
    - `customer_name`
    - `customer_email`
    - `customer_phone`
    - `company_or_organization`
    - `event_context`
    - `event_date`
    - `event_location`
    - `guest_count`
    - `indoor_outdoor`
    - `palette_context`: school, company, city, church, venue, theme, other
    - `palette_notes`
    - `design_json`: canonical JSON payload
    - `summary_for_customer`
    - `summary_for_sales`
    - `pieces_considered_json`
    - `lead`: Link to `Lead`
    - `submitted_on`
    - `expires_on`
    - `created_from_guest`: Check
    - `owner_user`: Link to `User`

- `LT Decor Design Piece`
  - Child rows for selected pieces.
  - Fields:
    - `piece_id`
    - `piece_type`: classic_arch, classic_columns, backdrop_wall, organic_garland, balloon_drop, bouquet_logo
    - `display_label`
    - `quantity`
    - `dimensions_json`
    - `style`
    - `selected_colors_json`
    - `region_assignments_json`
    - `rules_summary_json`
    - `render_summary`
    - `sort_order`

- `LT Decor Design Share`
  - Optional child rows or separate DocType for guest/stakeholder links.
  - Fields:
    - `token_hash`
    - `token_label`
    - `permission`: view, comment, duplicate
    - `expires_on`
    - `last_viewed_on`
    - `revoked`

Inferred future supporting DocTypes:

- `LT Decor Color`: only after Jeff/GL approve customer-facing hex approximations.
- `LT Decor Rule`: only after the renderer needs editable formulas.
- `LT Decor Layout Template`: only after the first route proves which multi-piece layouts are actually needed.

Avoid over-modeling the first production slice. Store the canonical payload as JSON first, then promote frequently edited rule data into DocTypes once the workflow stabilizes.

## Guest Save And Share Token Behavior

Recommended behavior:

- Guests can save a draft only after providing email, or they can use local browser draft only before email capture.
- Guest share links use random high-entropy tokens.
- Store only a token hash in the database, not the raw token.
- Share links expire by default, for example 30 days.
- Guest share pages are read-only unless the visitor duplicates the design into their own session.
- Share pages should show no private internal notes, supplier notes, cost assumptions, or CRM-only fields.
- Revoke links when a design is submitted, archived, or manually revoked.
- Rate-limit guest save, share, and submit endpoints.

Privacy stance:

- A shared design may expose event style, organization colors, event context, and contact-adjacent details. Treat it as sensitive enough for token expiry and no search indexing.
- Add `noindex` to share pages.
- Do not put email, phone, full address, or internal sales notes on public token pages.

## Account Save Behavior

Recommended behavior:

- Logged-in customers can save designs to their account.
- Account-owned designs should use standard Frappe permissions where possible.
- If the user is logged in, set `owner_user` and keep edits tied to that user.
- If a guest later logs in with the same email, offer to attach the guest draft after email verification rather than auto-merging silently.
- Submitted designs become read-only snapshots unless the customer duplicates them into a new draft.

## Lead And CRM Submission Payload

Production endpoint recommendation:

- `locally_twisted.api.design_studio.save_design`
- `locally_twisted.api.design_studio.create_share_link`
- `locally_twisted.api.design_studio.submit_design_inquiry`
- All three should validate server-side. Guest methods should be rate-limited.

Lead mapping:

- `source`: Website
- `custom_source_channel`: Plan Custom Decor
- `custom_event_type`: child row for Balloon Decor, and possibly Events Inquiry if that remains the large-install intake label.
- `custom_decor_types`: plain-language list of selected pieces.
- `custom_package_notes` or a future dedicated design-summary field: sales summary.
- `custom_colors`: selected catalog color names and palette context.
- `custom_indoor_outdoor`: indoor/outdoor/both.
- `custom_event_date`, `custom_event_location`, `custom_guest_count`: from event basics when supplied.
- `custom_anything_else`: customer notes plus "planning visualization, not final engineering drawing" disclaimer.

Lead timeline:

- Create a `Communication` on the Lead with the readable summary.
- Include:
  - selected pieces
  - dimensions
  - selected color names
  - color-role attribution
  - pieces considered but not selected
  - scale references
  - customer notes
  - share/design link for internal review

Do not put the raw full JSON only in a free-text field. Store full JSON on `LT Decor Design` and link the Lead to it.

## Proposed Design Payload Contract

The browser should submit one canonical JSON object. Version it from day one.

```json
{
  "schema_version": "design-studio-v1",
  "studio_version": "2026-05-02-draft",
  "session_id": "client-generated-uuid",
  "event": {
    "context": "corporate",
    "date": null,
    "location": "",
    "guest_count": null,
    "indoor_outdoor": "",
    "venue_notes": ""
  },
  "customer": {
    "name": "",
    "email": "",
    "phone": "",
    "company_or_organization": ""
  },
  "palette": {
    "context": "organization",
    "source_label": "",
    "notes": "",
    "colors": [
      {
        "name": "Reflex Gold",
        "role": "primary",
        "approx_hex": "#c7a44a",
        "match_status": "approximate"
      }
    ]
  },
  "pieces": [
    {
      "piece_id": "piece-1",
      "piece_type": "classic_arch",
      "display_label": "Classic arch",
      "quantity": 1,
      "dimensions": {
        "length_ft": 20
      },
      "style": "alternating",
      "selected_colors": ["Reflex Gold", "Royal Blue"],
      "region_assignments": [
        {
          "region": "main",
          "color_names": ["Reflex Gold", "Royal Blue"]
        }
      ],
      "rules_summary": {
        "engine": "structured_cluster",
        "customer_visible_precision": "planning_visual",
        "balloon_math_visible_to_customer": false
      },
      "summary": "20 ft classic arch using Reflex Gold and Royal Blue."
    }
  ],
  "suggestions": {
    "pieces_shown": [
      {
        "piece_type": "classic_columns",
        "reason": "Pairs with entrance arch",
        "inherited_colors": ["Reflex Gold", "Royal Blue"]
      }
    ],
    "pieces_declined": [
      {
        "piece_type": "classic_columns",
        "reason": "Customer skipped suggested pair"
      }
    ]
  },
  "render": {
    "renderer": "svg",
    "thumbnail_svg": "",
    "alt_summary": "Planning visualization of a classic arch in Reflex Gold and Royal Blue."
  },
  "customer_notes": "",
  "sales_summary": {
    "short": "Corporate decor inquiry for a 20 ft classic arch.",
    "pieces_considered": "Customer was shown classic columns but did not add them.",
    "follow_up_questions": [
      "Confirm venue dimensions and install timing.",
      "Confirm color match against organization palette."
    ]
  },
  "disclaimers": {
    "not_final_engineering": true,
    "colors_are_approximate": true,
    "pricing_not_final": true
  }
}
```

Required server validation:

- Payload must parse as JSON object.
- `schema_version` must be recognized.
- `pieces` must be non-empty before Lead submission.
- Color names must be from an approved server-side list.
- Piece types and style names must be allowed server-side.
- Dimensions must be bounded to sane maximums before saving.
- Customer email must pass Frappe email validation before Lead creation.
- Raw SVG from the browser should not be trusted as executable content.

## Loud Failure Behavior

Customer-facing:

- Every save/share/submit failure shows a visible message near the active button.
- Submission failure must include phone and email fallback.
- Never show a blank page or silent spinner.
- Disable submit only while request is in flight, then restore it on error.

Developer-facing:

- Unexpected exceptions call `frappe.log_error` with sanitized context.
- Do not log raw design JSON if it contains contact details. Log design id, schema version, endpoint, remote IP, and a short payload hash.
- Validation errors should use `frappe.throw` with plain user-safe messages.

Operational:

- No partial silent Lead creation. If the design record is saved but Lead creation fails, the UI should say the inquiry was not sent and give the fallback contact path.
- If Lead creation succeeds but Communication creation fails, log loudly and still return the Lead id with a warning for internal review.
- If a share token cannot be created, do not pretend the design was shared.

## Prototype Vs Hidden Frappe Route

Recommendation:

- First prototype: keep under `research/design-studio-v2/`.
- Second prototype, after controller review: hidden/unlinked Frappe route is acceptable if browser/device verification inside Frappe is needed.
- Production candidate: public `/plan-custom-decor` only after GL/Jeff approve UX, privacy, CRM payload, color handling, and launch timing.

Reasoning:

- Research prototype protects V1 launch routes.
- Hidden Frappe route proves real template, asset, CSRF, and guest API behavior when needed.
- Public route should wait until save/share/submit behavior is intentionally enabled or intentionally disabled.

## Key Decisions

Recommended:

- Build inside the existing `locally_twisted` Frappe app.
- Use Frappe website routes and whitelisted methods.
- Use vanilla JS and SVG/canvas rendering before considering any frontend framework.
- Store saved sessions in a future `LT Decor Design` DocType with JSON payload plus child rows for operational search/readability.
- Use `/plan-custom-decor` as the customer-facing route.
- Keep `/shop` as Ready to Order and `/contact` as canonical inquiry fallback.
- Keep the first prototype in research until the controller reconciles the spec wave.
- Treat color names as load-bearing and hex values as approximate until Jeff/GL approve mappings.

Not recommended:

- Separate app.
- Separate service.
- Separate external frontend build.
- Directly adding Design Studio fields to Lead as the only storage model.
- Public token links with no expiry.
- Making Jeff the public-facing CTA language.

## Risks

Guest sharing:

- Public token links can leak event plans or organization palette details if forwarded.
- Mitigation: token hashing, expiry, noindex, no PII on share page, revoke controls.

Privacy:

- Designs can include contact details, venue details, and event context.
- Mitigation: separate internal design record from public share view; redact public share fields.

Spam:

- Guest save/share/submit endpoints can become spam targets.
- Mitigation: Frappe rate limits, payload size caps, optional honeypot, and minimum useful-payload validation.

CRM payload quality:

- A pretty design can still be useless to sales if it lacks dimensions, color names, event context, and pieces considered.
- Mitigation: require structured payload fields before submit and create a readable Lead Communication.

Misleading render:

- Customers may treat the visualization as final engineering or exact color proof.
- Mitigation: persistent plain-language disclaimer and server-side rule validation.

Launch risk:

- Adding route rules, hooks, global assets, or Lead schema during V1 launch can collide with active launch work.
- Mitigation: no implementation until reviewed; use a feature branch or isolated workstream once approved.

## Questions For GL / Jeff

- Should share links exist for guests, or should saved designs require an account?
- What expiry window is acceptable for guest share links?
- Which event details may appear on a public shared design page?
- Are approximate hex values approved for the 53 named latex colors, or should the first version show names only?
- Should the studio submit into current `Balloon Decor` Lead service only, or also mark `Events Inquiry` for larger installs?
- What minimum fields make a Design Studio inquiry useful enough for Locally Twisted to follow up?
- Should customers see any construction math, or should counts stay internal?
- Which first pieces are approved for the first prototype: classic arch, pair of classic columns, backdrop/photo wall, and later organic garland?
- Should pricing stay completely absent, show "quote needed," or show rough planning tiers?
- Should account save be part of first production, or should guest email save come first?

## Verification Before Production Integration

Before any implementation:

- Re-read active workstream and queue to confirm V1 launch risk.
- Confirm `hooks.py` has no conflicting route or asset changes from other agents.
- Confirm current Lead custom fields with bench/API before mapping payload fields.
- Confirm current `custom_event_type` service records before submission work.

Suggested checks once a hidden route exists:

```powershell
python scripts/dev/clear_website_cache.py
npm run test:layout-fit
python scripts/verify/nav_ia.py
```

Suggested backend checks once endpoints exist:

```powershell
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Lead'}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'LT Decor Design'}"
```

Add dedicated verification before production:

- Route loads at desktop and mobile.
- No console errors.
- Save draft succeeds for logged-in user.
- Guest save either works as designed or is visibly disabled.
- Share token opens the redacted view only.
- Expired/revoked token fails visibly.
- Submit creates exactly one Lead.
- Lead `custom_event_type` includes the intended service row.
- Lead Communication includes selected pieces, colors, dimensions, and pieces considered.
- Server rejects unknown color names, unknown piece types, oversized payloads, and invalid emails.
- Public share view has `noindex` and does not expose phone/email/address/internal notes.

## Approval State

Verified:

- Frappe-native implementation fits current app patterns.
- Existing public form and newsletter code provide examples for guest endpoints and loud failure behavior.
- Current workstream says this is V2 background planning, not V1 launch work.

Inferred:

- A future `LT Decor Design` DocType plus child rows is the cleanest production storage model.
- Direct API POST wrappers are safer than assuming `frappe.call` exists on all website pages.
- First prototype should stay in research until controller review.

Needs GL/Jeff approval:

- Public route timing.
- Guest share/account save rules.
- Customer-visible color approximations.
- CRM field labels and service tagging.
- Final first-piece scope.
- Whether any pricing or construction math appears to customers.
