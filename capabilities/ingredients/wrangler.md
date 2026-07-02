---
id: wrangler
name: Wrangler
schema_version: 2.1
profile: foundation
level: ingredient
maturity: candidate
scope: local or project environments using Cloudflare Workers or Pages
currently_true: unknown
last_verified: unknown
tags:
  - cloudflare
  - wrangler
  - pages
  - workers
  - deploy
---

## What it does

Provides Cloudflare's `wrangler` command for Workers, Pages, D1, R2, KV, and
other Cloudflare deployment and management tasks.

## When to reach for it

- A static site needs a direct Cloudflare Pages upload.
- A Cloudflare Worker or Pages project needs deploy or environment checks.
- A workflow needs to inspect Cloudflare account or project state from the CLI.

## How to use it

Check availability and identity before relying on it:

```bash
npx wrangler --version
npx wrangler whoami
```

Use the project's documented Cloudflare account and environment. Do not assume
the currently authenticated account is the right target.

## What it depends on

Node/npm or an installed Wrangler binary, plus Cloudflare authentication for the
intended account.

## Failure modes

- Browser-based login can hang in headless or SSH-only environments.
- The active Cloudflare account may be wrong for the domain or project.
- A direct deploy can succeed while custom-domain DNS is still pending.
