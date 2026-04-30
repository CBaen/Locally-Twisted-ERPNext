# Locally Twisted - Agent Instructions

This is the agent-neutral entrypoint for Codex / ChatGPT / other coding agents working in this repo.

Do not treat old handoff files as truth. Treat them as claims, then verify important facts against git, files, and the running ERPNext database before relying on them.

## Project Reality

- Client: Locally Twisted, owned by Jeff Kimber.
- Business: custom balloon decor, balloon twisting, and face painting on the Wasatch Front, Utah.
- Build: Locally Twisted's first professional business management system on ERPNext v15.
- This is a new ERPNext build, not an Odoo migration.
- The failed Odoo test deployment is reference material only. It never served customers.
- The live Odoo test shop at `http://5.78.136.133/shop` was the catalog source/reference for the 2026-04-30 catalog port.
- Do not modify `C:\Users\baenb\projects\locally-twisted-odoo\` from this project.

## Current Verified State

Verified against the ERPNext database on 2026-04-30:

| Record | Count |
|---|---:|
| Website Items | 53 |
| Items total | 10,631 |
| Variant templates | 49 |
| Single-SKU templates | 4 |
| Variants | 10,578 |
| Item Prices | 10,613 |
| Item Variant Attribute rows | 32,002 |
| Item Attributes | 26 |

Important correction: older files may claim `10,613 Items`, `8,925 Item Prices`, or `10,560 variants`. Those counts are stale. Re-check DB before changing catalog docs or seed logic.

## Local Stack

| Item | Value |
|---|---|
| Compose project | `locally-twisted-erpnext-v15` |
| Host URL | `http://localhost:8081` |
| Stack dir | `Locally-Twisted-Backend/frappe_docker/` |
| ERPNext image | `frappe/erpnext:v15.105.0` |
| Frappe site | `frontend` |
| Admin login | `Administrator` / `admin` |
| Dev login | `cameron@builtbycameron.com` / `LocalDev2026!` |

Installed app order must keep `locally_twisted` last:

```python
["frappe", "erpnext", "payments", "webshop", "locally_twisted"]
```

If another app is installed, re-set `installed_apps` so LT template overrides still win Frappe's reversed app order.

## Read First

1. `CODING-HANDOFF.md` - compact verified state and next work.
2. `.planning/PROJECT.md` - project frame and requirements.
3. `locally-twisted-queue.md` - active queue, but verify because it can drift.
4. `locally-twisted-decisions.md` - decision log; read newest entries first.
5. `_resources/STYLE-GUIDE.md` - brand, voice, accessibility.
6. `_resources/design-guide/README.md` plus `synthesis/voice.md`, `synthesis/mood.md`, `synthesis/rationale.md` before frontend work.
7. `git log --oneline -20`.

Claude-era files such as `CLAUDE.md`, `HANDOFF.md`, and `PROJECT-STATUS.md` may contain useful operational history, but they are not authoritative unless verified.

## Frappe / ERPNext Rules

Work within Frappe and ERPNext.

- Theme CSS lives in the app and is registered through `web_include_css`.
- Header/footer customization should use Jinja partial overrides.
- Static/portal pages should live under `apps/locally_twisted/locally_twisted/www/<route>.html` with a same-name controller when needed.
- Webshop pages should use Webshop/Frappe override hooks and templates instead of replacing the cart pipeline.
- Avoid `head_html` CSS injection and avoid `!important` chains. The known exception is the contained `.product-code` hide for Webshop's compiled product-card JS.
- After Jinja/CSS/Web Page edits, run `python scripts/dev/clear_website_cache.py`.
- Before declaring visual work done, verify with browser screenshots at desktop and mobile widths.

## Voice And UI Language

Jeff is not a technical operator. Customer and backend UI copy should be plain.

Avoid:

- "Qualification Status"
- "Qualified By"
- "Qualified On"
- "Lead Owner"
- "Pipeline Stage"
- "Opportunity"

Prefer:

- "Status of Inquiry"
- "Reviewed and First Contact By"
- "Reviewed On"
- "Who's Handling This"
- "Where We Are" / "What Stage"
- "Booking" where a customer-facing label is needed

Do not invent business facts, policy terms, product details, or legal language. Use `_resources/` sources or ask.

## Canonical Resources

- Style guide: `_resources/STYLE-GUIDE.md`
- Design guide: `_resources/design-guide/`
- Business policies: `_resources/policies/`
- Utah tax research: `_resources/utah-tax-rates-2026q2.md`
- Live Odoo catalog scrape output: `_resources/odoo-live/`
- `/book` and `/contact` snapshots: `_resources/odoo-live-snapshot/hetzner-book.html` and `hetzner-contact.html`

The Odoo snapshots are canonical for the rebuilt `/book` and `/contact` form shape where explicitly stated. They are not blanket authority for the rest of the system.

## Current P0 Work

As of 2026-04-30, the next safest implementation slices are:

1. `/book` form page: primary inquiry conversion path, currently expected to be missing/404, backed by the existing Lead schema.
2. `/privacy` and `/terms-of-service`: required for Stripe live-mode readiness.
3. Fix stale documentation counts so future agents stop repeating catalog errors.

For `/book`, verify the existing Lead schema before building. The intended source is the Hetzner `/book` snapshot and live source if reachable, with native ERPNext Lead field names.

## Trust Rules

- Never claim a route, form, count, or visual state is working without verification.
- Say when something is unverified.
- Prefer small complete slices over broad rewrites.
- If prior docs conflict, verify against the running system and tell GL what changed.
- Do not hide errors behind "probably" or "should".
