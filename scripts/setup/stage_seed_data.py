#!/usr/bin/env python3
"""Stage local catalog reference data into the LT-owned app seed path.

This is a local-development/reference prep helper. It refreshes the ignored
duplicate at `apps/locally_twisted/locally_twisted/seed/lt_catalog_seed/` so
bench commands can use an LT/ERPNext-owned seed artifact path instead of
depending on `_resources/odoo-live` inside the runtime container.

Staging/bootstrap must receive a neutral LT-owned seed artifact. Do not use a
provider bind mount of `_resources/odoo-live` as the deployment fix.

Run:
  python scripts/setup/stage_seed_data.py
"""
from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "_resources" / "odoo-live"
TARGET = ROOT / "apps" / "locally_twisted" / "locally_twisted" / "seed" / "lt_catalog_seed"
PRICE_ENRICHMENT = (
    ROOT
    / "audits"
    / "odoo-erpnext-migration-audit-2026-05-08"
    / "21-product-page-price-enrichment-candidates.json"
)


def main() -> int:
    if not SOURCE.exists():
        raise SystemExit(f"missing source catalog directory: {SOURCE}")
    if not (SOURCE / "catalog.json").exists():
        raise SystemExit(f"missing required catalog file: {SOURCE / 'catalog.json'}")

    if TARGET.exists():
        shutil.rmtree(TARGET)
    shutil.copytree(SOURCE, TARGET)
    if PRICE_ENRICHMENT.exists():
        shutil.copy2(PRICE_ENRICHMENT, TARGET / "product_page_price_enrichment_candidates.json")
    print(f"staged seed data: {SOURCE} -> {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
