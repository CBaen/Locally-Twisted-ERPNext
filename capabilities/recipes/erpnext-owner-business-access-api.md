---
name: ERPNext owner business access API
level: recipe
last_verified: 2026-05-15
---

## What It Does

Builds owner-facing ERPNext access as a provider-neutral business DTO boundary before any ChatGPT, OAuth, MCP, mobile, or external assistant adapter is allowed to touch the system.

## When To Reach For It

Use this when Jeff/business-owner access needs fewer taps, mobile-friendly contact actions, assistant integration, or backend visibility without exposing raw ERPNext Desk objects. Use [erpnext-simplified-role-verification](erpnext-simplified-role-verification.md) for Desk/workspace-only changes.

## Contract

- Owner/support access is the primary lane. Do not widen this into Manager, Employee, Accountant, Customer, Supplier, Marketing, or Maintenance tracks unless that protects owner/support use.
- The DTO layer is the source for assistant/mobile clients. Adapters consume it; they do not query arbitrary ERPNext records directly.
- ChatGPT is one future adapter, not the architecture. Future adapters may be OAuth, API-key, MCP, OpenAPI, or another assistant provider.
- External assistant auth is not local-session proof. Local Frappe session auth may prove the page and DTOs, but external provider access needs a separate token-verifier/OAuth gate before exposure.
- Read first. Writes start with `log_contact_attempt` only. No automated customer send, call, text, invoice, payment, quote approval, or status mutation is allowed from the assistant lane without a later explicit gate.
- Human tap stays required for phone calls and texts. The system may generate `tel:`, `sms:`, and message drafts; it must not silently send.
- Fake data is allowed locally when it is clearly marked, synthetic, and removable by its owning setup script.

## Current LT Implementation

- DTO source: `apps/locally_twisted/locally_twisted/owner_business_access.py`
- API adapter: `apps/locally_twisted/locally_twisted/api/owner_business.py`
- Phone page: `/owner-actions`
- Workspace entry: `LT Owner Home` shortcut `Call or Text`
- Local fake-data seed: `python scripts/setup/sync_owner_demo_data.py`
- Cleanup: `python scripts/setup/sync_owner_demo_data.py --cleanup`
- Contract: `python scripts/verify/owner_business_access_contract.py`
- Browser proof: `npm run test:owner-actions`

## Verification

Run the focused owner gate after touching this lane:

```bash
export LT_DESK_TEST_USER='locallytwisted@gmail.com'
export LT_DESK_TEST_PASSWORD='LocalTemp2026!'
npm run test:owner-actions
python scripts/verify/backend_workspace_parity.py
npm run test:desk-owner
```

Use the broader synthetic pipeline when fake-data or Lead/Contact/Sales Order creation changed:

```bash
python scripts/verify/synthetic_business_pipeline.py
```

## Failure Modes

- Treating ChatGPT-specific auth or schema as the durable business contract.
- Letting an assistant adapter read raw ERPNext records instead of owner-safe DTOs.
- Adding a write method that changes customer, money, quote, payment, or send state without a dedicated verifier.
- Creating local fake records without a marker and cleanup command.
- Proving the page with Administrator instead of the real owner/support account.
