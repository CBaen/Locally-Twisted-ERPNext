# Contact Form UX Readiness - 2026-05-14

Source issue: [LOC-8](/LOC/issues/LOC-8)
Parent issue: [LOC-6](/LOC/issues/LOC-6)

## 2026-05-15 Implemented Form / Spam Closeout

Active implementation handoff:
[inquiry-form-spam-sales-filter-2026-05-15.md](inquiry-form-spam-sales-filter-2026-05-15.md).

Current state:

- Contact Details now sits first on the public inquiry form.
- Preferred contact method sits beside name on desktop and directly under name
  on mobile.
- Email replaces the prior preferred-contact position in the next row.
- Preferred-contact helper copy was removed.
- Event Basics follows Contact Details and uses `#F6F7F8`; Contact Details and
  Timing and Scale remain white.
- `What are you celebrating?` is optional in the browser and backend submit
  path.
- Timing and Scale uses title case, removes visible "optional" labels, and adds
  `Even Estimates Help` under event start/end time.
- AM/PM controls were widened so the text fits.
- The public form now renders a signed `lt_form_token` plus an invisible
  `website` honeypot.
- Backend submit rejects missing/too-fast/stale/honeypot posts before Lead
  creation, emails, or file handling.
- High-confidence sales solicitations are soft-filtered: a Lead still exists
  for audit/review, customer-safe confirmation still follows the normal path,
  but the owner "New website inquiry" email is suppressed.

Local proof passed on 2026-05-15:

```bash
python scripts/verify/inquiry_sales_solicitation_filter.py --base-url http://localhost:8081
python scripts/verify/inquiry_spam_gate.py --base-url http://localhost:8081
npm run test:form-experience
python scripts/verify/lead_backend_intake_parity.py
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
python scripts/verify/customer_email_policy_contract.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.inquiry_upload_failure_contract.run
```

The live site still needs a Frappe Cloud app release/site update plus live spam,
sales-filter, smoke, and repeat-email/photo proof before this is claimed as
production protection.

## 2026-05-15 Form-First Copy Closeout

Current directive: keep the contact form as its own individual slice and do not
mix it with non-form dirty-file cleanup.

Local copy update resolved:

- `apps/locally_twisted/locally_twisted/www/contact.html`
- `apps/locally_twisted/locally_twisted/www/contact.py`

The form changes are copy-only:

- form heading changed from `Free Event Quote` to
  `Tell us what you're planning`;
- page title/meta/intro changed from free-quote language to
  tell-us-about-your-event language.

Superseded context from the earlier form audit: the larger form behavior changes
had already added phone, preferred contact method, structured time controls,
email typo warning, louder frontend validation, and backend Lead mapping. The
latest closeout above corrects the occasion field back to optional and adds the
spam/sales-filter gates.

Latest local verification passed on 2026-05-15 against
`http://localhost:8081/contact`:

```bash
python -m py_compile apps/locally_twisted/locally_twisted/www/contact.py scripts/verify/contact_service_logic.py scripts/verify/lead_backend_intake_parity.py
python scripts/dev/clear_website_cache.py
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/lead_backend_intake_parity.py
npm run test:form-experience
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter
python scripts/verify/customer_email_policy_contract.py
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
```

Observed local/live gap on 2026-05-15:

- local has preferred contact method, email typo hint, structured visible time
  controls, and newer JS/CSS asset versions;
- live `https://locallytwisted.com/contact` is still the older release and does
  not show those newer form features.

Do not mix non-form Paperclip changes into this slice. The separate review
packet is `workstreams/paperclip-change-audit-2026-05-15.md`.

## Recommendation

Conditional go for scoped engineering planning. No-go for live release until:

- The requested [LOC-6](/LOC/issues/LOC-6) form changes are attached.
- Legal counsel is available for any change that touches policy, privacy, terms,
  payment, refunds, customer obligations, data collection, or customer-facing
  promises.
- ERPNext v15 architect/CTO coverage is available for any change touching
  Frappe/ERPNext form routing, Lead mapping, email queue proof, app ordering,
  or version-specific behavior.
- Local, staging, and live verification gates pass.

Latest human direction on [LOC-8](/LOC/issues/LOC-8): if the company does not
have legal counsel, it is not prepared. This changes the readiness answer from
"engineering can handle this with gates" to "engineering/UX can prepare and
test, but live release is not prepared without legal coverage where the change
has legal or policy impact."

## Evidence This Run

Rendered surface: `/contact` on local ERPNext at `http://localhost:8081`.

Visual evidence captured:

- `output/ux/loc-11-contact-mobile-390-20260514.png`
- `output/ux/loc-11-contact-desktop-1366-20260514.png`
- `output/ux/loc-11-contact-render-summary-20260514.json`

Rendered summary:

- Viewports: 390x900 mobile and 1366x900 desktop.
- H1: `Request a free event quote`.
- Shared `inquiry-v1` form visible.
- 45 inquiry form fields/controls counted, including the submit button.
- No document-width overflow at 390px or 1366px.

Verification results:

- Focused contact browser gate passed 14/14: container contract at 320/820/1366,
  compact hero at mobile/tablet/desktop, generated hero crop/readability
  overlay, white-label visible text, and expanded conditionals at
  320/414/820/1200.
- `npm run test:form-experience`: 5 passed.
- `python scripts/verify/contact_prefill.py --base-url http://localhost:8081`:
  PASS.
- `python scripts/verify/contact_service_logic.py --base-url http://localhost:8081`:
  PASS.

Not repeated in this heartbeat: backend Lead smoke, strict email proof, staging,
or live verification. Those remain release gates for an implemented change.

## UX Impact Map

### Fields And Backend Mapping

Current required fields are customer name and email. Phone, company, occasion,
event date/time, city/location, estimated guests, service choices, conditional
service details, inspiration photos, and free-form notes are optional or
conditional.

Any field addition/removal can affect the shared form partial,
`submit_book_inquiry`, Lead custom-field mapping, customer confirmation email
details, owner notification details, Communication timeline summary, smoke
cleanup, and Desk operator readability.

UX guard: do not add optional fields that look required, and do not collect data
that is not needed for first contact.

Design lenses: Data Minimization, Cognitive Load, Plain Language.

### Intent Routing And Prefill

`/contact` is canonical. `/book` is legacy and redirects to
`/contact?intent=quick`.

Query and session paths already prefill the form from:

- `service`
- `item`
- Checkout delivery quote handoff
- Product-page quote handoff
- Event Playground handoff

BTFP embeds the same `inquiry-v1` partial with a restricted service set.
Changes to service taxonomy can break both `/contact` and
`/balloon-twisting-and-face-painting`.

UX guard: keep prefilled choices visible and editable.

Design lenses: Recognition over Recall, Mental Models, Information Scent.

### Validation And Conditional Logic

Client validation covers name/email and photo count/size. Backend validation
must remain authoritative.

Conditional panels are progressive disclosure. Changing service labels,
checkbox values, or condition names can silently hide fields or drop submitted
data.

Disabled hidden fields must not submit stale values.

Design lenses: Progressive Disclosure, Nielsen Visibility of System Status,
Forgiveness.

### Success And Failure Messaging

Success may appear only when the backend returns `message.ok`.

Backend `message.ok` depends on current Lead creation plus customer confirmation
queue and owner/business notification queue proof. Stale Email Queue or
Communication rows are not proof.

Failure copy must stay calm, specific, and non-technical, with phone/email
fallback. Operator/developer evidence still needs exact failure records or logs.

Do not add a fake `#received`, localStorage success, optimistic success toast,
or redirect-only success path.

Design lenses: Trust Signals, Loss Aversion, Peak-End Rule, Fail Loud.

### Mobile, Layout, And Accessibility

The contact hero is under the compact hero contract. Form and location sections
are under the public container contract.

Mobile layout must keep the full form usable at 320/390/414px without hidden
horizontal scroll, clipped labels, covered submit button, or cookie notice
overlap.

Modal, status, fields, checkboxes, and submit controls need visible focus,
44px touch targets, accessible labels, and color-independent errors.

Design lenses: WCAG POUR, Fitts's Law, Gestalt Proximity, Gestalt Common Region.

### Content, Brand, And Legal

Keep labels concrete: service, timing, location, photos, notes. Avoid
CRM/backend terms in public UI.

Events Inquiry copy needs a single source of truth before any client change is
layered on top. The current verifier passes; future copy changes should update
the rendered label, customer-facing copy review, and verifier contract together.

If the requested change is mostly messaging, CMO should review public copy
before CTO implements. If it changes field meaning, UX and CTO should approve
the IA/record mapping first. If it touches policy, privacy, terms, money,
refunds, data use, customer obligations, or response promises, legal counsel
approval is required before live release.

Design lenses: Information Scent, Plain Language, Trust Signals, Ethics.

## Minimum Acceptance Checklist

### Local Gate

- Specific requested form changes are attached to [LOC-6](/LOC/issues/LOC-6) or
  a linked child issue.
- UX confirms the field, conditional, intent, and public failure-copy map.
- CMO reviews public messaging if the change is copy-heavy.
- Legal counsel reviews the change if it affects policy, privacy, terms,
  payment, refunds, customer obligations, data collection, or customer promises.
- ERPNext v15 architect/CTO reviews implementation scope if the change touches
  Frappe/ERPNext routing, app hooks, Lead mapping, Email Queue proof, or
  version-specific behavior.
- CTO updates source, backend mapping, verifiers, and email/Communication detail
  rendering together.
- `python scripts/verify/contact_service_logic.py --base-url http://localhost:8081`
  passes.
- `python scripts/verify/contact_prefill.py --base-url http://localhost:8081`
  passes.
- `npm run test:form-experience` passes.
- `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter`
  passes with backend proof and cleanup.
- If uploads, repeat email, success copy, or email proof changes:
  `python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081`
  passes.
- If customer/owner email details change:
  `python scripts/verify/customer_email_policy_contract.py` passes.
- Focused layout passes: contact container contract, contact expanded
  conditionals, compact hero, and at least mobile plus desktop screenshots
  reviewed.
- Accessibility passes for the touched route/state, including modal/focus if
  submit behavior changes.

### Staging Gate

- Deploy the app to the Frappe Cloud temporary/staging URL with
  `locally_twisted` still installed last.
- Keep `lt_ecommerce_paused=1` unless the separate checkout gate is explicitly
  reopened.
- Repeat the local contact smoke, prefill, and form-experience gates against
  staging.
- Run strict customer plus owner email proof against staging/admin access if
  success, email, upload, repeat-email, or Lead handling changed.
- Inspect `/contact` at mobile and desktop widths on staging, including at
  least one expanded conditional service path.
- Confirm Cloudflare/Frappe Cloud cache does not cache dynamic contact/API
  paths.

### Live Gate

- Legal approval is recorded when the change requires legal review.
- Re-run live `/contact` smoke with backend proof and cleanup.
- If the submit path changed, run the strict live repeat-email/five-photo
  verifier with customer and owner Email Queue body/recipient proof.
- Verify a real rendered live `/contact` mobile and desktop surface after cache
  settles.
- Check Frappe Error Log/report rows for public-contact failures created during
  verification.
- Do not mark customer-facing success ready if either customer confirmation or
  owner notification proof is missing.

## Needed Follow-Up

Guiding Light/UMA should confirm whether legal counsel is available before any
legal-impact form change proceeds. If counsel is not available, the live release
recommendation is no-go for those changes.

CTO or an ERPNext v15 architect should own implementation readiness for any
form logic, Frappe route, Lead mapping, Email Queue, or version-specific change.
UX can approve usability only after the exact requested change is attached and
the local rendered/form gates pass.
