---
name: ERPNext maintenance heartbeat boundary
level: recipe
last_verified: 2026-05-08
---

## What It Does

Documents the Locally Twisted implementation of the agency maintenance
heartbeat standard at
`C:\Users\baenb\projects\Built_by_Cameron\.codex\capabilities\recipes\erpnext-maintenance-heartbeat-boundary.md`.
This file is the client receipt layer: exact LT role names, DocTypes, scripts,
verification commands, and expected current states live here.

Do not use this file as the reusable template for another client. Promote
cross-client rules back to the agency recipe and keep LT-specific wiring here.

## Contract

The heartbeat can report:

- system and scheduler health;
- business automation index status;
- paperwork/reporting digest status;
- notification preference readiness;
- approval-tier vocabulary for future maintenance actions;
- safe action-needed text for owners, operators, and agents.

The heartbeat must not expose:

- raw `Error Log`, `Activity Log`, `Access Log`, `Version`, `Communication`,
  `Comment`, `Email Queue`, or `File` rows;
- Lead, Customer, Contact, Address, Sales Order, Sales Invoice, Payment Request,
  Payment Entry, or other customer/money records;
- raw tracebacks, request payloads, document IDs, customer names, emails, phone
  numbers, addresses, IPs, payment references, or private files.

## Permission Model

Maintenance access is a role, not a role profile.

LT uses the narrow `LT Maintenance Admin Access` role and exposes only sanitized
maintenance DocTypes, reports, and workspaces. Do not grant System Manager,
Website Manager, Accounts, Sales, Inbox, Item Manager, owner, or accountant
roles to the maintenance actor by default.

## Action Tiers

1. Tier 0: observe/report only.
2. Tier 1: draft/internal review only.
3. Tier 2: safe metadata or blocker repair, approval required.
4. Tier 3: idempotent app-owned setup repair, approval required.
5. Tier 4: live customer/money/data action, approval required.

Explanation and audit evidence are mandatory for every maintenance action.
Tier 4 cannot run automatically from the heartbeat.

## LT Implementation

Source:

```text
apps/locally_twisted/locally_twisted/maintenance/heartbeat.py
apps/locally_twisted/locally_twisted/seed/sync_maintenance_package.py
apps/locally_twisted/locally_twisted/locally_twisted/report/lt_maintenance_heartbeat/
```

Verifier commands:

```powershell
python scripts/setup/sync_maintenance_package.py
python scripts/verify/maintenance_heartbeat.py
python scripts/verify/maintenance_admin_boundary.py
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
```

Current expected status:

- light heartbeat passes with `client_notification_preferences` yellow until
  the owner chooses recipient, cadence, topic, and channel;
- heavy heartbeat passes and includes business automation index plus paperwork
  digest status;
- boundary verifier passes only when Maintenance Admin can read sanitized
  maintenance surfaces and cannot read forbidden raw/customer/finance DocTypes.

## Failure Modes

- Giving the maintenance actor System Manager because the report is easier to
  build that way.
- Treating Error Log as the client-facing heartbeat source.
- Sending cadence notifications before the owner chooses topics, channel, and
  billing/retainer expectations.
- Letting a "fix immediately" mode skip explanation or audit rows.
- Writing customer data into a supposedly sanitized run/event record.
- Marking the heartbeat green when the scheduler hook, setup records, report
  roles, or forbidden-DocType boundary is broken.
