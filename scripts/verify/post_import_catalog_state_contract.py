#!/usr/bin/env python3
"""Contract checks for pure post-import catalog-state evaluation.

Run:
  python scripts/verify/post_import_catalog_state_contract.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))


def _catalog_state_module():
    from locally_twisted.verify import post_import_catalog_state

    return post_import_catalog_state


def _ready_status(slug: str) -> dict[str, Any]:
    return {
        "website_item": {"item_code": slug, "published": 1},
        "item": {"name": slug, "disabled": 0},
        "variant_count": 0,
        "price_count": 1,
        "price_min": 25,
        "price_max": 25,
        "ready": True,
    }


class PostImportCatalogStateContract(unittest.TestCase):
    def test_missing_unpriced_included_slug_fails_loudly(self) -> None:
        result = _catalog_state_module().evaluate_catalog_state(
            included_slugs=["fake-missing"],
            excluded_slugs=[],
            statuses_by_slug={
                "fake-missing": {
                    "website_item": None,
                    "item": None,
                    "variant_count": 0,
                    "price_count": 0,
                    "price_min": None,
                    "price_max": None,
                    "ready": False,
                }
            },
            counts={
                "website_items_included": 0,
                "item_templates_included": 0,
                "item_variants_included": 0,
                "item_prices_included": 0,
                "distinct_priced_item_codes_included": 0,
                "manifest_source_ready_sale_units": 1,
            },
            priority_slugs=[],
        )

        self.assertFalse(result["ok"])
        self.assertIn("fake-missing", result["missing_website_item_slugs"])
        self.assertIn("fake-missing", result["missing_item_slugs"])
        self.assertIn("fake-missing", result["unpriced_slugs"])
        self.assertTrue(result["blockers"])
        self.assertEqual(result["included_count"], 1)
        self.assertEqual(result["excluded_count"], 0)
        self.assertEqual(result["explicit_excluded_slugs"], [])

    def test_all_ready_fake_state_passes(self) -> None:
        result = _catalog_state_module().evaluate_catalog_state(
            included_slugs=["ready-slug"],
            excluded_slugs=["held-out-slug"],
            statuses_by_slug={"ready-slug": _ready_status("ready-slug")},
            counts={
                "website_items_included": 1,
                "item_templates_included": 1,
                "item_variants_included": 0,
                "item_prices_included": 1,
                "distinct_priced_item_codes_included": 1,
                "manifest_source_ready_sale_units": 1,
            },
            priority_slugs=["ready-slug"],
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["missing_website_item_slugs"], [])
        self.assertEqual(result["unpublished_website_item_slugs"], [])
        self.assertEqual(result["missing_item_slugs"], [])
        self.assertEqual(result["disabled_item_slugs"], [])
        self.assertEqual(result["unpriced_slugs"], [])
        self.assertEqual(result["unready_priority_products"], [])
        self.assertEqual(result["included_count"], 1)
        self.assertEqual(result["excluded_count"], 1)
        self.assertEqual(result["explicit_excluded_slugs"], ["held-out-slug"])
        self.assertTrue(result["priority_products"]["ready-slug"]["ready"])


def main() -> int:
    parse_noop_args(__doc__)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PostImportCatalogStateContract)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
