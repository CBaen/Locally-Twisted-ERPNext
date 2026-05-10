# Frappe Cloud Cutover Workstream

Status: prep-only, no deployment or DNS change made.
Owner lane: production hosting and final `locallytwisted.com` cutover.
Last verified: 2026-05-10.

## Purpose

Make the eventual owner-present Frappe Cloud launch look boring:

1. The app source is already acceptable to Frappe Cloud.
2. The production site is staged and verified under a temporary Frappe Cloud URL.
3. The domain is already known to be Cloudflare-controlled.
4. The final meeting only adds the custom domain, verifies SSL, makes it primary, and changes Cloudflare DNS.

No current-site DNS record should be changed until Jeff is present and the Frappe Cloud site has passed the launch checks.

## Current Verified Facts

- Repo branch rule: `main` only.
- Current remote: `https://github.com/CBaen/Locally-Twisted-ERPNext.git`.
- Current custom app root: `apps/locally_twisted`.
- Frappe Cloud app-root mirror: `https://github.com/CBaen/Locally-Twisted-Frappe-App.git`.
- App package name: `locally_twisted`.
- App metadata exists at `apps/locally_twisted/pyproject.toml`.
- App advertises Frappe v15 support with `frappe = ">=15.0.0,<16.0.0"`.
- App has no declared APT packages today: `[deploy.dependencies.apt] packages = []`.
- Frappe Cloud SSH key to add in the dashboard: `C:\Users\baenb\.ssh\id_ed25519.pub`.
- Frappe Cloud SSH key fingerprint: `SHA256:7xYKNfuUifwOSCXCVeZcb7YNk4/djsiwg49abG9j9uU`.
- Public domain is already delegated to Cloudflare:
  - `edward.ns.cloudflare.com`
  - `laura.ns.cloudflare.com`
- Current public records still point to the old site:
  - `locallytwisted.com A 162.241.218.247`
  - `www.locallytwisted.com CNAME locallytwisted.com`
- Frappe Cloud docs currently say custom domains using Cloudflare must be DNS-only during verification; proxied records do not work for the custom-domain add.

## Primary Architecture Decision

Use a Frappe Cloud private bench, not a public bench.

Reason: Locally Twisted is a custom ERPNext app with website route overrides, patches, fixtures, public assets, email/cascade hooks, and scheduler entries. Frappe Cloud private benches are the supported lane for custom apps, GitHub app sources, chosen app versions, SSH access, and controlled updates.

## App Source Decision

Do not use the full project repository as the Frappe Cloud custom app source.

This repo is a project repo. The Frappe app starts at `apps/locally_twisted`, and Frappe Cloud custom app validation expects app metadata such as `pyproject.toml` at the app root. The prepared app-root GitHub mirror has exactly the contents of `apps/locally_twisted` at repository root:

```text
https://github.com/CBaen/Locally-Twisted-Frappe-App.git
```

That mirror is private. Sync it from a reviewed commit of this repo, not from a dirty worktree.

## Data Migration Decision

This is not just an app-code deployment.

The local ERPNext database contains the actual site state: catalog records, Website Items, prices, print/email setup, policy pages, workspaces, and other ERPNext documents. Installing the app alone will not recreate every production record unless the import/seed path is deliberately run.

Preferred owner-present shape:

1. Before the meeting, stage a Frappe Cloud site under a temporary Frappe Cloud subdomain.
2. Install the standard apps plus `locally_twisted`.
3. Restore or migrate a scrubbed production-intended backup from the local site.
4. Re-enter environment-specific secrets in Frappe Cloud instead of carrying local `.env`, local site config, or dev SMTP/Stripe credentials across blindly.
5. Run launch verifiers against the temporary Frappe Cloud URL.
6. In the meeting, only perform domain and primary-domain steps.

Do not restore a local dev backup without a scrub pass. Local data may contain fake records, local admin assumptions, routed-email testing artifacts, and cutover-only credentials that should not become Jeff's production state.

## Preflight Command

Run this before any Frappe Cloud account work:

```powershell
python scripts/verify/frappe_cloud_preflight.py
```

The verifier is read-only. It checks branch, remote, dirty worktree state, app metadata, GitHub auth, SSH public key visibility, and current public DNS.

Current known preflight warnings:

- The worktree is dirty because several other LT feature lanes are active. Cutover should use a clean, reviewed, pushed commit.
- DNS still points to the current old site. That is correct until cutover.

Resolved prep warnings:

- `id_ed25519.pub` is now readable and is the key to paste into Frappe Cloud Settings > SSH Key.
- `ssh-agent` is not required for the current prep path; use the Frappe Cloud dashboard SSH certificate flow with the matching local private key.
- The app-root mirror exists at `CBaen/Locally-Twisted-Frappe-App` with `pyproject.toml` at repository root.

## Frappe Cloud Setup Path

Use the dashboard until there is a reason to automate.

1. Log into Frappe Cloud.
2. Add `C:\Users\baenb\.ssh\id_ed25519.pub` under Frappe Cloud account settings.
3. Create a private bench on Frappe/ERPNext v15 in the chosen region.
4. Add required apps to the private bench:
   - ERPNext
   - Payments
   - Webshop
   - Locally Twisted custom app from `https://github.com/CBaen/Locally-Twisted-Frappe-App.git`
5. Deploy the bench.
6. Create a staging site on that private bench.
7. Install apps on the site in this order:
   - `erpnext`
   - `payments`
   - `webshop`
   - `locally_twisted`
8. Restore/migrate the scrubbed site backup or run the approved production import path.
9. Confirm `installed_apps` keeps `locally_twisted` last so template overrides still win.
10. Re-enter production-only secrets in the Frappe Cloud dashboard/site config:
    - SMTP/email account credentials
    - Stripe live keys and webhook secret
    - Any future storage/payment/provider credentials
11. Run launch verification against the temporary Frappe Cloud URL before touching `locallytwisted.com`.

## DNS Cutover Path

Do this only after the Frappe Cloud staging URL passes verification.

1. In Frappe Cloud, open the site dashboard.
2. Add `www.locallytwisted.com` as a custom domain.
3. In Cloudflare DNS, create/update the `www` CNAME to the Frappe Cloud site target.
4. Keep the Cloudflare record DNS-only for verification.
5. Verify the domain in Frappe Cloud and wait for SSL.
6. Add `locallytwisted.com` as the apex custom domain.
7. Use the Frappe Cloud inbound IP or Cloudflare CNAME flattening pattern shown by Frappe Cloud for the apex.
8. Keep only one apex target record. Frappe Cloud explicitly warns against multiple A records for the same domain.
9. Set `locallytwisted.com` as the primary domain if that is the desired public address.
10. Enable redirect from the non-primary domain to the primary domain.
11. Verify:
    - `https://locallytwisted.com/`
    - `https://www.locallytwisted.com/`
    - `/event-balloons`
    - `/portfolio`
    - `/balloon-twisting-and-face-painting`
    - `/contact`
    - `/shop` plus cart/checkout testing route, unless a fresh GL decision re-enables the pause route

## Do Not Do

- Do not install the custom app over SSH with `bench get-app`; Frappe Cloud warns this will not persist correctly across bench updates.
- Do not edit production CSS/JS files over SSH as the deployment method.
- Do not change Cloudflare DNS before the Frappe Cloud site is already verified on a temporary URL.
- Do not proxy the Cloudflare custom-domain records during Frappe Cloud verification.
- Do not move the GoDaddy registrar setup unless the business owner explicitly decides to transfer registrar ownership. The practical DNS authority is already Cloudflare.
- Do not carry local `.env`, local `site_config.json`, or dev credentials into production as-is.
- Do not treat app installation as proof that catalog/content/customer workflows migrated. Verify records and forms directly.

## Launch Verification Stack

Run against the staging Frappe Cloud URL before domain cutover:

```powershell
python scripts/verify/frappe_cloud_preflight.py
python scripts/verify/nav_ia.py
npm run test:layout-fit
npm run test:interactive-layout
npm run test:portfolio-reel
python scripts/verify/contact_service_logic.py
python scripts/verify/contact_prefill.py
python scripts/verify/smoke_forms.py --base-url <frappe-cloud-url> --form-path /contact --skip-newsletter
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
python scripts/verify/payment_launch_readiness.py --mode live
```

`payment_launch_readiness.py --mode live` is intentionally cutover-only. It should not be used as a blocker for synthetic fake-data work, but it is required before real checkout/payment claims.

## Source Docs Checked

- Frappe Cloud private benches: https://docs.frappe.io/cloud/benches
- Frappe Cloud create bench: https://docs.frappe.io/cloud/benches/create-new
- Frappe Cloud install app on private bench and site: https://docs.frappe.io/cloud/installing-an-app
- Frappe Cloud custom domains: https://docs.frappe.io/cloud/sites/custom-domains
- Frappe Cloud SSH access: https://docs.frappe.io/cloud/benches/ssh
- Frappe Cloud debugging cautions: https://docs.frappe.io/cloud/benches/debugging
- Frappe Cloud restore/migrate site: https://docs.frappe.io/cloud/sites/migrate-an-existing-site
- Frappe Cloud APT dependencies: https://docs.frappe.io/cloud/faq/installing-app-apt-dependencies
- Frappe Cloud custom app fetch issues: https://docs.frappe.io/cloud/faq/custom_apps
