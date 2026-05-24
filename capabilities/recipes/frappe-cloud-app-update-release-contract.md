# Frappe Cloud App Update Release Contract

Status: `active`
Last verified: 2026-05-23

## Purpose

Use this for routine Locally Twisted ERPNext/Frappe app updates on Frappe
Cloud. The release shape is:

source/app update -> staging owner review -> explicit approval -> live
code/app-only promotion.

Staging is the owner approval gate. It is not the final outcome.

## Required Skill

Use the canonical skill before execution:

`C:\Users\baenb\projects\codex-framework-backup\skills\frappe-cloud-app-update-release\SKILL.md`

Use the staging leg skill when staging is the active phase:

`C:\Users\baenb\projects\codex-framework-backup\skills\frappe-cloud-staging-release-gate\SKILL.md`

## LT Boundaries

Protect live production data and provider state unless separately approved:

- products and catalog records;
- customers, clients, orders, invoices, payments, and financial records;
- private files and customer uploads;
- production site settings;
- checkout/payment mode;
- DNS, Stripe, Search Console, and public indexing.

Do not copy staging data over live as a normal release path. Live promotion is
code/app promotion unless a separate written data/settings migration is
approved with rollback proof.

## P0 Proof

Before staging mutation:

- source freeze;
- fresh release packet;
- account/site identity proof;
- release status not `NO-GO`;
- app mirror/sync plan;
- provider snapshot;
- complete Frappe Cloud site object payload proof;
- rollback path.

Before owner link:

- hosted preflight on actual staging;
- LT-owned seed/data source present when bootstrap/import is needed;
- bootstrap/RQ terminal success;
- staging owner-review gate passes against hosted staging.

Before live:

- owner approval artifact;
- reviewed staging URL and hash bound to live target;
- live-before snapshot;
- live code/app-only promotion protector;
- live-after proof and monitor window.

## Guard Vocabulary

Do not collapse these states:

- local guard pass;
- GitHub archive;
- app mirror freshness;
- Frappe Cloud deploy/update completion;
- hosted preflight;
- staging owner-review pass;
- owner approval;
- live code/app promotion;
- live verified.

Each label requires its own proof.

## Current LT Blockers

As of 2026-05-23:

- staging is NO-GO for Jeff because catalog counts remain zero;
- catalog seeding must use an LT-owned seed source, not `_resources/odoo-live`;
- owner approval artifact for live promotion still needs to be built;
- live code/app-only promotion protector still needs to be built.

Receipts:

- `workstreams/frappe-cloud-app-update-release-process-2026-05-23.md`
- `workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
- `workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`
