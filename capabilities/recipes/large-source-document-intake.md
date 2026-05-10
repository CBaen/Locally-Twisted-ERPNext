---
id: large-source-document-intake
name: Large Source Document Intake
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted source documents, exports, handoffs, policy packets, and legacy reference captures
currently_true: unknown
verification_level: 1
last_verified: 2026-05-08
evidence_quality: direct
successful_uses: 0
failed_uses: 0
regressions: 0
depends_on:
  - fail-loud-operating-law
used_by: []
tags:
  - Locally Twisted
  - source documents
  - Odoo reference
  - ERPNext
  - truncation
---

## What it does

Protects Locally Twisted work from partial reads of large source material by
forcing chunked intake and exact source spans before an agent summarizes,
migrates, or implements from the material.

## When to reach for it

Use for Odoo scrapes, Hetzner snapshots, policy files, catalog exports,
QuickBooks/accounting packets, long handoffs, logs, PDFs, spreadsheets, HTML
captures, and any terminal/tool output likely to truncate.

## How to use it

1. Verify the current lane and source of truth first. For live ERPNext facts,
   the running site/database still wins over old documents.
2. Use the global Codex skill:
   `C:\Users\baenb\.codex\skills\large-document-intake\SKILL.md`
3. Put generated intake output in a temporary working directory unless GL
   explicitly asks to preserve it.
4. For catalog, policy, checkout, payment, form, or customer-facing claims,
   cite the chunk and source span that supports the claim.
5. If extraction is blocked, especially scanned/OCR-only PDFs, report the
   blocker and do not backfill from stale handoffs or memory.

## What it depends on

- [fail-loud-operating-law](fail-loud-operating-law.md)

## Failure modes

- Treating an old Odoo/Hetzner artifact as current ERPNext proof.
- Trusting a stale handoff because it was readable in the first terminal page.
- Missing rows in catalog/accounting exports due to truncation.
- Committing generated chunk output as a second source of truth.
