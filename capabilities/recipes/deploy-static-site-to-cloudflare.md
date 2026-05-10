---
name: Deploy Static Site to Cloudflare Pages
level: recipe
last_verified: 2026-04-25
---

## What it does

Takes a built static site (Hugo, Astro, Next static export, plain HTML) and gets it live on a custom domain via Cloudflare Pages, with HTTPS, in one workflow.

## When to reach for it

- A static site is built locally and needs to be online.
- You want a custom domain attached, not the default `*.pages.dev` URL.
- You don't want to manage a server.

## How to use it

1. **Verify the build output exists.** Confirm the `dist/` (or `public/`, or `out/`) directory contains an `index.html`. No build output, no deploy.
2. **Authenticate `wrangler`.** `npx wrangler login` opens a browser; user approves. Confirm with `npx wrangler whoami`.
3. **Create the Pages project.** `npx wrangler pages project create <project-name> --production-branch main`.
4. **Deploy the build directory.** `npx wrangler pages deploy <build-dir> --project-name <project-name>`.
5. **Attach a custom domain.** In the Cloudflare dashboard: Pages → project → Custom domains → Set up. Cloudflare auto-creates the CNAME if the domain is on Cloudflare DNS; otherwise it tells you the CNAME to add manually.
6. **Verify HTTPS.** Wait ~1–5 minutes. `curl -I https://<your-domain>` should return 200 with a valid certificate.

## What it depends on

- [gh-cli](../ingredients/gh-cli.md) — only if you're also pushing source to GitHub for CI deploys (when added).
- [wrangler](../ingredients/wrangler.md) — the Cloudflare CLI (when added).

## Failure modes

- **`wrangler login` hangs in headless environments.** It needs a browser. SSH-only sessions: use `wrangler login --api-token` with a token created in the dashboard.
- **Custom domain stays "Pending" forever.** The CNAME wasn't propagated, or it points to the wrong target. `dig <domain> CNAME` to verify.
- **404 on every page after deploy.** The build directory was wrong (deployed the source, not the output). Re-check step 1.
- **Cloudflare's free plan limits build minutes.** Big sites with frequent deploys can hit the cap. Switch to direct upload (above) instead of CI builds.

## Examples

Deployed a 200-page Hugo site (calming-engine.com) in ~8 minutes from "build is done" to "HTTPS responds on the custom domain." Most of that was DNS propagation.
