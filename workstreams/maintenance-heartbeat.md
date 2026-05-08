# Maintenance Heartbeat

Last updated: 2026-05-08 by Codex after verifying the sanitized heartbeat, setup sync, and Maintenance Admin boundary.

## Outcome

Provide automated checkups that fail loudly without exposing customer data, raw logs, communications, files, or finance records to a maintenance role.

## Current State

- `locally_twisted.maintenance.heartbeat.run` returns a sanitized client operations heartbeat.
- `hooks.py` schedules `scheduled_light_checkup` hourly and `scheduled_full_checkup` daily.
- `scheduled_full_checkup` writes compact Error Log evidence only when red events exist.
- `scripts/setup/sync_maintenance_package.py` ensures the `LT Maintenance Admin Access` role, `LT Maintenance Heartbeat` report, `LT Maintenance Home` workspace, and DocPerm boundary.
- `scripts/verify/maintenance_heartbeat.py --heavy` verifies public boot, scheduler, notification preferences, role boundary, business automation index, and paperwork digest events.
- `scripts/verify/maintenance_admin_boundary.py` verifies Maintenance Admin cannot read forbidden raw/customer/finance DocTypes.
- Business automation index treats `client_operations_heartbeat` as launch-required.

Latest published implementation commit: `125431d Add sanitized maintenance heartbeat`.
Latest documentation handoff commit: `170ad21 Document backend automation safety surfaces`.

## Boundaries

- This is not live customer delivery.
- This is not a broad admin role.
- This is not an auto-repair system yet.
- This is not permission to read raw Frappe/GitHub/provider logs through the
  Maintenance Admin role.
- Yellow owner-setup rows are allowed visible attention signals; red rows fail the verifier.
- Scheduled persisted rows must stay sanitized: safe summary, action needed, source, status, severity, and counts only.

## Agent Handoff Notes

- Treat this lane as a support surface for agents and owners, not as a general
  observability stack.
- If a future agent adds notification delivery, the change must start with
  owner-selected topic, recipient, channel, cadence, billable provider status,
  quiet-hours expectations, and immediate-vs-cadence thresholds.
- If a future agent adds auto-fix behavior, it must use the action tiers in
  `heartbeat.py`; explanation and audit rows are required, and live
  customer/money/data actions stay approval-gated.
- If a future agent needs raw `Error Log`, `Communication`, payment, customer,
  or file data, that is an owner/admin investigation path outside Maintenance
  Admin. Do not widen the maintenance role to make the investigation easier.

## Owner Files

- `apps/locally_twisted/locally_twisted/maintenance/heartbeat.py`
- `apps/locally_twisted/locally_twisted/seed/sync_maintenance_package.py`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_maintenance_run/`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_maintenance_health_event/`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_maintenance_action_request/`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_maintenance_action_log/`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_client_notification_preference/`
- `apps/locally_twisted/locally_twisted/locally_twisted/report/lt_maintenance_heartbeat/`
- `scripts/setup/sync_maintenance_package.py`
- `scripts/verify/maintenance_heartbeat.py`
- `scripts/verify/maintenance_admin_boundary.py`

## Verification

```powershell
python scripts/setup/sync_maintenance_package.py
python scripts/verify/maintenance_heartbeat.py
python scripts/verify/maintenance_heartbeat.py --heavy
python scripts/verify/maintenance_admin_boundary.py
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
```

Closeout verification on 2026-05-08 also ran `python scripts/verify/smoke_shop.py`
and `python scripts/verify/variant_media_contract.py` because the same session
had touched the public boot/product-page risk surface.

## Next Safe Slice

Add owner-approved notification preference seed rows only after GL/Jeff choose recipients, cadence, topics, and channel. Do not enable customer delivery or live repair actions from this lane without explicit approval.
