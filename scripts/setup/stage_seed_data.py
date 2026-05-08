#!/usr/bin/env python3
"""Stage Odoo catalog seed data into the ignored app-local container path.

The source of truth remains `_resources/odoo-live/`. This script refreshes the
ignored duplicate at `apps/locally_twisted/locally_twisted/seed/_data/` for
bench commands that run inside the locally_twisted app container.

Run:
  python scripts/setup/stage_seed_data.py
"""
from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "_resources" / "odoo-live"
TARGET = ROOT / "apps" / "locally_twisted" / "locally_twisted" / "seed" / "_data"


def main() -> int:
    if not SOURCE.exists():
        raise SystemExit(f"missing source catalog directory: {SOURCE}")
    if not (SOURCE / "catalog.json").exists():
        raise SystemExit(f"missing required catalog file: {SOURCE / 'catalog.json'}")

    if TARGET.exists():
        shutil.rmtree(TARGET)
    shutil.copytree(SOURCE, TARGET)
    print(f"staged seed data: {SOURCE} -> {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
