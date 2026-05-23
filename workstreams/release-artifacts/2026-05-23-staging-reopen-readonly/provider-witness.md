# Provider Witness Artifact

Target: `locallytwisted-staging.frappe.cloud` on Frappe Cloud.

Evidence:

- `provider-snapshot.json` was produced by `scripts/verify/frappe_cloud_provider_snapshot.py` in real read-only mode.
- Staging site status is `Active`.
- Staging bench group is `bench-40102`.
- Installed `locally_twisted` app hash is `181076c239b2d1d3d508a41ac471c71f9d2b5158`.
- App order is `frappe`, `erpnext`, `payments`, `webshop`, `locally_twisted`.
- Running jobs are empty.
- Staging has `lt_ecommerce_paused=1` and `lt_public_indexing_enabled=0`.
- App mirror HEAD is also `181076c239b2d1d3d508a41ac471c71f9d2b5158`.

BLOCK:

Provider state is stable enough for read-only analysis, but it is not owner-review ready and it is not current with the full source repo. The app-root mirror does not contain `locally_twisted/staging_owner_review_preflight.py`, so the deployed staging app cannot expose the new hosted bootstrap preflight.

Next safe provider action:

No provider deploy/update/bootstrap/cache action while the forensic-freeze lock is active. If release execution is explicitly reopened, first update the app-root mirror from reviewed source, then take a fresh read-only provider snapshot before any mutation.
