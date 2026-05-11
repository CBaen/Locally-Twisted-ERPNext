---
id: frappe-public-storefront-security
name: Frappe Public Storefront Security
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe public storefront security review and hardening
currently_true: false
verification_level: 2
last_verified: 2026-05-11
evidence_quality: direct
successful_uses: 2
failed_uses: 1
regressions: 1
depends_on:
  - fail-loud-operating-law
  - erpnext-checkout-commerce-rules
  - erpnext-intake-form-parity
used_by:
  - website-launch
  - shop
  - commerce-rules-checkout
tags:
  - Locally Twisted
  - Frappe
  - Webshop
  - security
  - checkout
  - uploads
  - XSS
---

# Frappe Public Storefront Security

Use this recipe when reviewing or changing public LT routes, guest whitelisted methods, checkout/payment return pages, product templates, contact uploads, internal preview routes, or customer-visible records.

## Contract

Public routes must not treat Frappe/ERPNext document names, template strings, local preview ports, or customer-supplied files as safe proof of identity.

## Required Checks

- Escape every customer-controlled string rendered into Jinja output. Do not assume Frappe page templates autoescape.
- Do not build DOM/HTML strings from database or URL values. Use text nodes, `textContent`, jQuery attribute objects, or equivalent safe APIs.
- Store customer-submitted files as private unless GL explicitly approves public publication.
- Customer portal file-registration methods must prove the `File` belongs to
  the current customer and the same source record before creating visibility or
  uploaded-by-customer metadata.
- Do not show Sales Orders, Payment Requests, invoices, file URLs, customer details, or line items from a public page unless the request carries a nonce/token/session proof that was issued for that customer flow.
- Do not perform final CRM, customer, invoice, or receipt-state mutations before the money/status boundary that justifies them.
- Gate internal preview bridges and local-dev helpers away from unauthenticated public routes.
- Treat tracked credentials in docs as an operational security finding even when they are local-dev credentials.

## Verification Pattern

1. Identify the public source: query string, form field, upload, route param, Stripe return param, localStorage payload, or database field reachable from a public route.
2. Trace the sink: Jinja output, raw HTML string, Frappe `File`, ERPNext document mutation, redirect URL, iframe, or email/customer record.
3. Reproduce through the real local route when bounded and non-destructive.
4. Prefer rollback-safe or static validation for CRM/payment mutations that would alter records.
5. Write the exact symptom into the route/workstream verifier before closing the issue.

## 2026-05-08 Receipt

Parallel Codex Security review found and reproduced `/shop?q=` reflected XSS, public Lead file exposure, unauthenticated order-summary exposure on `/thank-you?order=...`, tracked local credentials, pre-payment Lead conversion by guest checkout email, and an unauthenticated internal Event Playground preview bridge.

The first safe patch escaped `/shop` search output, hardened the product gallery image rendering path, and made new inquiry uploads private. The follow-up patch moved final inquiry Lead conversion from guest checkout into the paid-order cascade and gated `/event-playground` behind login plus Administrator/System Manager access.

GL clarified the current data/files are fake and this is a balloon business, so the unauthenticated order-summary and existing fake public-file findings are hardening/cleanup items rather than immediate launch blockers in the current fake-data state. Credential rotation/doc cleanup remains GL-owned before broader sharing or real customer cutover. Token-bound receipt proof remains the stronger production pattern if real customer data or higher-sensitivity order context enters the site.

## 2026-05-11 Receipt

External review found the customer portal file-registration method accepted any
existing `File` name after source access passed. The fix requires the File row
to be owned by the logged-in customer and already attached to the same source
record before `LT Customer Portal File` is created. The portal V1 contract now
proves one valid customer-owned source file registers and that staff-owned or
wrong-source files fail without creating portal metadata.
