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

## Boundaries

- This is not live customer delivery.
- This is not a broad admin role.
- This is not an auto-repair system yet.
- Yellow owner-setup rows are allowed visible attention signals; red rows fail the verifier.
- Scheduled persisted rows must stay sanitized: safe summary, action needed, source, status, severity, and counts only.

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
python scripts/verify/maintenance_heartbeat.py --heavy
python scripts/verify/maintenance_admin_boundary.py
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
```

## Next Safe Slice

Add owner-approved notification preference seed rows only after GL/Jeff choose recipients, cadence, topics, and channel. Do not enable customer delivery or live repair actions from this lane without explicit approval.
