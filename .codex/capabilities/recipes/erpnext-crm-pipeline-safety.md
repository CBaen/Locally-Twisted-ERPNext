---
name: ERPNext CRM pipeline safety
level: recipe
last_verified: 2026-05-02
---

## What it does

Keeps a client-friendly CRM/Kanban pipeline from corrupting ERPNext's native status, conversion, finance, or reporting behavior.

## When to reach for it

Use this when translating a client's approved sales stages into ERPNext, especially when the source system had stages such as `Won`, `Lost`, `Archive`, `Booked`, or other labels that might affect revenue, win rate, or workflow automation.

## How to use it

1. Separate the business board from ERPNext internals.

   Keep native fields such as `Lead.status` available for ERPNext. Put the client-facing board on a dedicated custom Select field when stage names are business language rather than ERPNext status language.

2. Define stage meaning before wiring triggers.

   Write down which stage means "off the active board" versus "won", "lost", "ready to invoice", "ready to schedule", or "needs follow-up". Do not infer those from the old system's archive/fold settings.

3. Make archive non-financial unless explicitly approved.

   If the goal is "remove from active Kanban", implement `Archive` as a custom stage and archived Kanban column. Do not connect it to Sales Order, Sales Invoice, Payment Request, or win-rate logic unless the user explicitly confirms that business meaning.

4. Sync idempotently.

   Use setup code to create/update the custom field, normalize existing records, recreate the Kanban board, and preserve useful card order where possible.

5. Verify the guardrails.

   A verifier should confirm the custom field exists, the Kanban board points at that custom field, stale native-status columns are gone, existing records have valid values, and no Property Setter repurposes `Lead.status` with the custom pipeline values.

## LT verification commands

```powershell
python scripts/setup/sync_crm_pipeline.py
python scripts/verify/crm_pipeline_parity.py
python scripts/setup/sync_backend_workspaces.py
python scripts/verify/backend_workspace_parity.py
```

## Failure modes

- Reusing `Lead.status` for client-friendly stage names can fight ERPNext's conversion logic and distort reporting.
- Treating an old `Archive` or folded stage as a win can inflate win rate or trigger the wrong cascade.
- A Kanban board can visually look right while still pointing at the wrong field.
- Updating only the board leaves new website Leads without the correct business stage.
