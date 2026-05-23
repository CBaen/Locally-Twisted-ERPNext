# LT Staging Freeze Artifact Packet Template

Status: template only. Copy this structure into a new dated release packet when
release execution is explicitly reopened. Do not put secrets in this folder.

## Required Files

- `controller.md`
- `provider-witness.md`
- `gate-fixer.md`
- `recorder.md`
- `read-receipt.json`
- `sanitized-payload.json`
- `provider-snapshot.json`
- `failure-ledger.json`

## Read Receipt Shape

```json
{
  "agent": "name-or-session-id",
  "created_at": "YYYY-MM-DDTHH:MM:SS-06:00",
  "read_documents": [
    "workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md",
    "workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md",
    "workstreams/frappe-cloud-staging-owner-review-2026-05-22.md",
    "capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md",
    "locally-twisted-queue.md"
  ]
}
```

## Provider Snapshot Shape

```json
{
  "team": "sanitized team id/name",
  "site": "locallytwisted-staging.frappe.cloud",
  "bench_group": "current staging bench group",
  "bench": "current staging bench",
  "installed_app_hash": "current installed locally_twisted hash",
  "target_app_hash": "target app mirror hash",
  "release_id": "candidate/release id or none",
  "running_jobs": [],
  "app_order": ["frappe", "erpnext", "payments", "webshop", "locally_twisted"],
  "site_status": "Active",
  "rollback_hash": "known rollback hash",
  "staging_live_separation": true
}
```

## Sanitized Payload Shape

```json
{
  "content_type": "application/json",
  "body": {
    "apps": [
      {
        "app": "locally_twisted",
        "repository": "https://github.com/CBaen/Locally-Twisted-Frappe-App.git",
        "hash": "full-target-hash"
      }
    ],
    "sites": [
      {
        "name": "locallytwisted-staging.frappe.cloud"
      }
    ]
  }
}
```

## Failure Ledger Shape

```json
{
  "fresh_release_plan_approved": false,
  "failures": [
    {
      "class": "payload_shape",
      "guard_written": true,
      "evidence": "capabilities/failures/frappe-cloud-api-payload-shape-drift.md"
    }
  ]
}
```
