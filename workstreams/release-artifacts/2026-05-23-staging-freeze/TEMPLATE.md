# LT Staging Freeze Artifact Packet Template

Status: template only. Copy this structure into a new dated release packet when
release execution is explicitly reopened. Do not put secrets in this folder.

## Required Files

- `controller.md`
- `provider-witness.md`
- `gate-fixer.md`
- `recorder.md`
- `read-receipt.json`
- `freeze-reopen-approval.json`
- `app-mirror-sync-plan.json`
- `sanitized-payload.json`
- `app-mirror-freshness.json`
- `deploy-completion.json`
- `hosted-bootstrap-preflight.json`
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

## Freeze Reopen Approval Shape

Template only. This file is the explicit local transition out of forensic
freeze for staging-only actions. It must be current, bounded to the active lock,
and must not include live/DNS/Stripe/Search Console/indexing/checkout exposure.

```json
{
  "ok": true,
  "approval_type": "forensic_freeze_reopen",
  "lock_id": "lt-staging-forensic-freeze-2026-05-23",
  "approved_by": "Guiding Light",
  "approved_at": "YYYY-MM-DDTHH:MM:SS-06:00",
  "expires_at": "YYYY-MM-DDTHH:MM:SS-06:00",
  "target_site": "locallytwisted-staging.frappe.cloud",
  "source_commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "approved_actions": [
    "app_mirror_sync",
    "frappe_cloud_deploy",
    "provider_poll",
    "staging_bootstrap",
    "site_migrate",
    "cache_clear"
  ],
  "live_dns_stripe_search_console_blocked": true,
  "provider_mutation_executed": false
}
```

Run through the controller with `--reopen-approval`; do not treat chat approval
or a commit message as this artifact.

## App Mirror Sync Plan Shape

This is a pre-sync plan, not post-sync proof. It allows the controlled app-root
mirror sync path to start without deadlocking on freshness that can only exist
after sync. After sync, a fresh `app-mirror-freshness.json` with `ok=true` is
still required before provider deploy/update, hosted preflight, bootstrap,
site migrate, or cache work.

```json
{
  "ok": true,
  "source_commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "mirror_url": "https://github.com/CBaen/Locally-Twisted-Frappe-App.git",
  "mirror_ref": "main",
  "target_site": "locallytwisted-staging.frappe.cloud",
  "rollback_hash": "cccccccccccccccccccccccccccccccccccccccc",
  "reviewed_source": true,
  "required_files": [
    "locally_twisted/staging_owner_review_preflight.py",
    "locally_twisted/staging_owner_review_bootstrap.py"
  ],
  "post_sync_required": ["app-mirror-freshness.json"],
  "no_provider_deploy_until_post_sync_freshness": true,
  "provider_mutation_executed": false
}
```

## Provider Snapshot Shape

```json
{
  "team": "sanitized team id/name",
  "site": "locallytwisted-staging.frappe.cloud",
  "bench_group": "current staging bench group",
  "bench": "current staging bench",
  "installed_app_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "target_app_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "release_id": "none",
  "running_jobs": [],
  "app_order": ["frappe", "erpnext", "payments", "webshop", "locally_twisted"],
  "site_status": "Active",
  "rollback_hash": "cccccccccccccccccccccccccccccccccccccccc",
  "staging_live_separation": true
}
```

## App Mirror Freshness Shape

```json
{
  "ok": true,
  "source_commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "mirror_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "provider_mutation_executed": false,
  "required_files": [
    {
      "path": "locally_twisted/staging_owner_review_preflight.py",
      "source_exists": true,
      "mirror_exists": true,
      "matches": true
    },
    {
      "path": "locally_twisted/staging_owner_review_bootstrap.py",
      "source_exists": true,
      "mirror_exists": true,
      "matches": true
    }
  ]
}
```

This artifact must be fresh after the reviewed app-root mirror sync and before
hosted preflight, bootstrap/import, deploy/update, or cache action.

## Hosted Bootstrap Preflight Shape

```json
{
  "ok": true,
  "site": "locallytwisted-staging.frappe.cloud",
  "method": "locally_twisted.staging_owner_review_bootstrap.preflight_staging_owner_review_bootstrap",
  "expected_app_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "preflight": {
    "ok": true,
    "target_site": "locallytwisted-staging.frappe.cloud",
    "expected_app_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "failures": [],
    "required_checks": [
      "standard_report",
      "roles",
      "settings",
      "app_hooks",
      "app_order",
      "target_hash",
      "baseline_counts",
      "destructive_seed_evidence"
    ],
    "checks": {
      "standard_report": {"ok": true, "failures": []},
      "roles": {"ok": true, "failures": []},
      "settings": {"ok": true, "failures": []},
      "app_hooks": {"ok": true, "failures": []},
      "app_order": {"ok": true, "failures": []},
      "target_hash": {
        "ok": true,
        "expected_app_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "current_app_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "failures": []
      },
      "baseline_counts": {"ok": true, "failures": []},
      "destructive_seed_evidence": {"ok": true, "failures": []}
    }
  },
  "provider_mutation_executed": false
}
```

This artifact must be generated from the actual staging target and match the
same site/hash as `provider-snapshot.json` and `app-mirror-freshness.json`.
The real `preflight` object must include the full `required_checks` and
`checks` payload from the hosted `build_bootstrap_preflight` response; a
minimal hand-authored `ok=true` object is not valid release proof.

## Deploy Completion Shape

This artifact is produced only after the controlled Frappe Cloud deploy/update
or site update job completes. It is not a pre-provider approval artifact and
must never be fabricated before the provider job exists.

```json
{
  "ok": true,
  "site": "locallytwisted-staging.frappe.cloud",
  "action": "frappe_cloud_deploy",
  "expected_app_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "target_app_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "installed_app_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "provider_job": {
    "name": "sanitized-provider-job-id",
    "status": "Success",
    "method": "press.api.site.update"
  },
  "running_jobs": [],
  "app_order": ["frappe", "erpnext", "payments", "webshop", "locally_twisted"],
  "site_status": "Active",
  "site_config": {
    "lt_ecommerce_paused": "1",
    "lt_public_indexing_enabled": "0"
  },
  "provider_mutation_executed": true
}
```

Validate with:

```powershell
$packet = "workstreams\release-artifacts\YYYY-MM-DD-staging-packet"
python scripts/verify/frappe_cloud_deploy_completion_contract.py `
  --artifact-file "$packet\deploy-completion.json" `
  --provider-snapshot "$packet\provider-snapshot.json" `
  --app-mirror-freshness "$packet\app-mirror-freshness.json"
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
        "hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
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
