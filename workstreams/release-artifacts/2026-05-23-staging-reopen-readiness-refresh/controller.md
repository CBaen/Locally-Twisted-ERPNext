# Controller Artifact

target: locallytwisted-staging.frappe.cloud
state: NO-GO while forensic-freeze is active
evidence: `release_locks/locally-twisted-staging-forensic-freeze.json` blocks `app_mirror_sync`, `frappe_cloud_deploy`, `provider_poll`, `staging_bootstrap`, `site_migrate`, and `cache_clear`.

## Boundary

This controller artifact authorizes read-only forensics and local guard
verification only. It does not authorize app mirror sync or provider/staging
mutation.
