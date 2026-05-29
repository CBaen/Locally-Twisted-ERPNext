# Staging Release Controller Packet - 2026-05-29

Status: draft release-controller packet, not deployment approval
Branch: `codex/lt-staging-release-controller-packet`
Worktree: `C:\Users\baenb\agent-worktrees\builtbycameron-lt\release-packet`

## Plain Meaning

The professional next step is to build this release packet, not to deploy
staging and not to wait.

This packet freezes what is known, what is not yet safe, and what a future
staging release controller must prove before any Frappe Cloud mutation. It does
not approve staging deployment, provider changes, live checkout, live Stripe,
DNS, Search Console, product data changes, ERPNext record mutation, email
sending, app-mirror update, migrate, cache clear, or remediation.

## Controller Decision

Decision: proceed with a release freeze packet.

Do not deploy staging yet. Do not treat packet completion as deploy approval.
Do not wait without writing down the source state, because the approved work is
spread across multiple branches and the main checkout has unrelated local
changes.

Professional term: source freeze. Plain meaning: name the exact commits that
would be considered for release before any system changes.

## Triad Result

Three read-only witness lenses reviewed the next-step decision.

| Lens | Recommendation | Main Reason |
|---|---|---|
| Release boundary / adversarial | Build the larger packet | Deploying now would skip source-freeze control; waiting would leave context scattered. |
| Customer / money / operator | Build the larger packet | Checkout, email, money, and operator proof are strong enough to organize, not strong enough to mutate staging without a fresh deploy approval. |
| Source identity / worktree integration | Build the larger packet | Main is dirty, `origin/main` is stale, and multiple branch tips must be named exactly. |

Integrated recommendation: build this packet now, then ask separately before
staging deployment.

## Current Source State

| Surface | Current Evidence | Release Meaning |
|---|---|---|
| Local committed `main` | `82c86f4` (`Document catalog scope authority rule`) | This is the committed local base used for this packet branch. |
| `origin/main` | `2a39109` (`Document delivery-only staging update`) | Stale compared with local `main`; do not use as the release source by habit. |
| Main checkout working tree | dirty with capability changes | Not a release source until classified and either excluded or intentionally included. |
| This packet branch | `codex/lt-staging-release-controller-packet` at local base `82c86f4` before this packet commit | Documentation/control branch only. |
| Checkout audit chain | `origin/codex/item5-staging-release-packet-scope` at `86d6908` | Includes item 2 through item 5 packet work; packet readiness approved only. |
| Graduation support packet | `origin/codex/lt-graduation-support-packet` at `4147dcb` | Repo-level capability support proof; not staging deployment approval. |
| Current hosted staging app/source identity | Recorded by item 5 packet as app mirror commit `35ac2b12c3cee96a611e5193b024c0ddf8c95b7b` | Accepted as packet evidence; not independently rerun by this controller lane. |

## Branch Relationship Findings

The checkout audit branches are chained:

- item 2 is an ancestor of item 5;
- item 3 is an ancestor of item 5;
- item 4 is an ancestor of item 5.

Local committed `main` is not an ancestor of item 5. This matters because a
future release candidate cannot blindly mean "take item 5" or "take main." It
must intentionally integrate the checkout audit chain with the current local
main base and preserve the capability/verifier work that belongs.

Observed divergence between local `main` and item 5 includes checkout runtime
files, proof docs, capability/index files, verifier script docs, and
`verifier-manifest.json`. That is a release-integration item, not a reason to
deploy directly.

## Recommended Inclusion Split

Default staging release candidate:

- include the checkout audit chain only after a clean integration branch proves
  exact source, tests, app mirror target, and hosted staging identity;
- include item 2 penny parity source behavior;
- include item 3 and item 4 evidence docs if they are part of the release
  packet;
- include item 5 packet evidence and approval boundary.

Default repo-level support lane:

- keep `codex/lt-graduation-support-packet` separate from the staging deploy
  candidate unless the release controller explicitly includes it;
- it can be reviewed or landed as repo/process support, but it does not need to
  be mixed into a customer checkout staging mutation by default.

Plain meaning: checkout changes and capability documentation are both valuable,
but they should not be blended just because they happened on the same day.

## Required Next Packet Before Deploy

Before asking for staging deployment approval, create a fresh staging execution
packet that includes:

- exact integration branch name and commit hash;
- exact checkout audit source commit chain included;
- whether graduation support is included or explicitly separate;
- exact app mirror target commit to be deployed;
- current provider-backed hosted staging app/source identity;
- release identity proof;
- freeze/reopen approval proof;
- required-doc read receipt;
- failure ledger and triad artifacts;
- local proof commands and results;
- hosted preflight and owner-review route/data proof required after deploy;
- rollback target and stop condition.

## Current Non-Approvals

This packet does not approve:

- staging deployment;
- Frappe Cloud provider mutation;
- app mirror update;
- migrate or cache clear;
- live checkout;
- live Stripe;
- DNS;
- Search Console;
- product data mutation;
- ERPNext record mutation;
- email sending;
- remediation outside the approved item packets.

## Stop Conditions

Stop before deployment if:

- the exact source commits are not frozen;
- a proposed release branch is dirty;
- a branch that must be remote-backed has no confirmed upstream;
- current staging source identity and intended target source identity are not
  both named;
- source commit, app mirror commit, hosted staging behavior, or packet inclusion
  list disagree;
- checkout totals, Stripe/test amount, thank-you page, receipt, internal
  notification, ERPNext record, or email proof differs by one cent;
- quote-first products can enter paid checkout;
- provider credentials, `.env`, Desk credentials, Stripe, email sending,
  ERPNext mutation, or provider mutation are required before explicit approval;
- graduation support, checkout work, product data, provider work, or live-system
  work are blended without explicit inclusion.

## Verification Notes

Verified in this controller lane:

- `origin/main` is behind local committed `main` by three commits.
- Packet branch was fast-forwarded to local committed `main` at `82c86f4`.
- `origin/codex/item5-staging-release-packet-scope` is at `86d6908`.
- `origin/codex/lt-graduation-support-packet` is remote-backed at `4147dcb`.
- Triad witnesses converged on "build packet, do not deploy, do not wait."

Not verified in this controller lane:

- Frappe Cloud API source identity was not independently rerun.
- No `.env` credential was read.
- No Desk credential was used.
- No hosted staging mutation was performed.
- No app mirror sync, migrate, cache clear, provider change, email sending,
  product-data change, ERPNext record mutation, live Stripe, DNS, or Search
  Console action was performed.

## Next Safe Step

After this packet is reviewed, create an integration release-candidate branch
only if the release controller can name exactly what it will include. That
branch should be verified locally and then brought back for explicit staging
deployment approval.
