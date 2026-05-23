# Provider Witness Artifact

target: locallytwisted-staging.frappe.cloud
state: NO-GO READ-ONLY SNAPSHOT ONLY
evidence: `provider-snapshot.json` shows staging is `Active`, app order is correct, running jobs are empty, ecommerce is paused, public indexing is disabled, and installed/target/rollback app hash remains `181076c239b2d1d3d508a41ac471c71f9d2b5158`.

## Boundary

Provider witness work may inspect current staging/provider state through
read-only Frappe Cloud/Press calls. It may not deploy, update, bootstrap,
migrate, cache clear, poll a running mutation, touch live, DNS, Stripe, Search
Console, production indexing, checkout exposure, or sync the app-root mirror
while the forensic-freeze lock remains active.
