# Live Indexing Provider Source Recovery Plan - 2026-05-29

## Current State

Superseded by successful redirect-aware recovery and live deployment.

The approved hotfix branch exists and is visible to Frappe Cloud, but the API
call used to change the live release group source returned `308 Permanent
Redirect` twice and did not apply the change.

Later recovery proved the redirect target was `cloud.frappe.io`. Calling the
same provider methods directly against `cloud.frappe.io`, then fetching the
latest app update, made approved commit `5bbdc48` deployable and live.

Live Frappe Cloud state after both attempts:

- Site: `locallytwisted.v.frappe.cloud`
- Release group: `bench-39776`
- App: `locally_twisted`
- Current source branch: `main`
- Current live app hash: `b4b3bf80108234c12051b572ac9b9cd4728f0efc`
- Current next release hash: `ad0a408c2df5ecb711062f35887b94520220b2c8`
- Approved hotfix hash: `5bbdc484d86729c4f2afdf7776e9f6649b02c080`

## Recovery Options

Preferred next path:

1. Use a redirect-aware Frappe Cloud API client for the source correction call.
2. First run only read-only calls:
   - prove `live-seo-indexing-20260528` remains visible in branch list;
   - prove live remains on `main`;
   - prove no deploy is in progress.
3. Run one source correction call.
4. Poll deploy information.
5. Stop unless Frappe Cloud proves:
   - branch is `live-seo-indexing-20260528`;
   - next release hash is exactly
     `5bbdc484d86729c4f2afdf7776e9f6649b02c080`.
6. Deploy/update live only after that proof.

Fallback path:

Use authenticated provider UI automation to change the app source branch, with
screenshot/API proof before deployment. This should be used only if the
redirect-aware API path cannot be proven.

## Hard Stops

Stop before deployment if:

- the next hash remains `ad0a408c2df5ecb711062f35887b94520220b2c8`;
- the provider source changes to any branch other than
  `live-seo-indexing-20260528`;
- Frappe Cloud starts a deploy job that was not explicitly requested;
- any provider call returns an unexplained redirect, auth error, permission
  error, validation error, or truncated response.

## Approval Needed

Resolved. The redirect-aware recovery was executed and verified under the live
indexing release boundary.

Suggested approval wording:

```text
I approve one fresh Locally Twisted live indexing provider-source recovery
attempt using a redirect-aware Frappe Cloud API client for bench-39776 only.
This approval is only to change locally_twisted from main to
live-seo-indexing-20260528, prove the next release hash is exactly 5bbdc48, and
deploy only if that proof passes. This does not approve ad0a408, live checkout,
Stripe, DNS, Search Console, product/catalog changes, production data mutation,
ERPNext record mutation, email sending, or repeated retries after another
provider failure.
```
