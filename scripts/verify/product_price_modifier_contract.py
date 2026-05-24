#!/usr/bin/env python3
"""Verify ERPNext variant prices match the LT-owned catalog seed artifact.

Run:
  python scripts/verify/product_price_modifier_contract.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = ROOT / "apps" / "locally_twisted"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from locally_twisted.catalog_variant_rules import (  # noqa: E402
    dedupe_required_variant_rows,
    normalize_variant_value,
)


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
PRICE_LIST = "Standard Selling"
SEED_ROOT = ROOT / "apps" / "locally_twisted" / "locally_twisted" / "seed" / "lt_catalog_seed"
REQUIRED_SOURCE_FILES = ("catalog.json", "value_normalize_map.json")


class ContractFail(Exception):
    pass


class SourceDataUnavailable(ContractFail):
    pass


def _money(value: Any) -> Decimal:
    return Decimal(str(value or "0")).quantize(Decimal("0.01"))


def _check_seed_packet() -> None:
    missing = [
        str((SEED_ROOT / filename).relative_to(ROOT))
        for filename in REQUIRED_SOURCE_FILES
        if not (SEED_ROOT / filename).exists()
    ]
    if missing:
        raise SourceDataUnavailable(
            "LT-owned catalog seed artifact is missing required file(s): "
            f"{', '.join(missing)}. Run `python scripts/setup/stage_seed_data.py` "
            "to refresh the local `lt_catalog_seed` artifact before checking prices."
        )


def _load_price_enrichment(base: Path) -> dict[str, dict[tuple[tuple[str, str], ...], Decimal]]:
    candidates = (
        base / "product_page_price_enrichment_candidates.json",
        base / "21-product-page-price-enrichment-candidates.json",
    )
    source = next((path for path in candidates if path.exists()), None)
    if not source:
        return {}
    artifact = json.loads(source.read_text(encoding="utf-8"))
    result: dict[str, dict[tuple[tuple[str, str], ...], Decimal]] = {}
    for product in artifact.get("products") or []:
        slug = str(product.get("slug") or "").strip()
        if not slug:
            continue
        prices: dict[tuple[tuple[str, str], ...], Decimal] = {}
        for unit in product.get("sale_units") or []:
            chosen = unit.get("chosen_price")
            if chosen in (None, ""):
                continue
            combo = unit.get("projected_required_combo") or {}
            prices[_combo_key(combo)] = _money(chosen)
        if prices:
            result[slug] = prices
    return result


def _combo_key(combo: dict[str, str] | None) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(axis), str(value)) for axis, value in (combo or {}).items()))


def _normalize_value(attr_name: str, raw_value: str, normalize_map: dict[str, dict[str, str]]) -> str:
    key = " ".join(str(raw_value or "").split()).lower()
    value = normalize_map.get(attr_name, {}).get(key, raw_value)
    return str(normalize_variant_value(attr_name, value) or "").strip()


def _load_expected_prices() -> dict[tuple[str, tuple[tuple[str, str], ...]], Decimal]:
    _check_seed_packet()
    catalog = json.loads((SEED_ROOT / "catalog.json").read_text(encoding="utf-8"))
    normalize_map = json.loads((SEED_ROOT / "value_normalize_map.json").read_text(encoding="utf-8"))
    enrichment = _load_price_enrichment(SEED_ROOT)
    expected: dict[tuple[str, tuple[tuple[str, str], ...]], Decimal] = {}
    for product in catalog.get("products") or []:
        slug = str(product.get("slug") or "").strip()
        if not slug:
            continue
        base_price = product.get("base_price")
        enriched_prices = enrichment.get(slug) or {}
        for row in dedupe_required_variant_rows(product.get("valid_variants") or []):
            combo = {
                attr_name: _normalize_value(attr_name, raw, normalize_map)
                for attr_name, raw in (row.get("combo") or {}).items()
            }
            key = _combo_key(combo)
            price = enriched_prices.get(key)
            if price is None:
                price = _money(row.get("erpnext_variant_price", row.get("price", base_price)))
            expected[(slug, key)] = price
    return expected


def mariadb(sql: str) -> list[dict[str, str]]:
    cmd = [
        "docker",
        "exec",
        "-i",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "mariadb",
        "--batch",
        "--raw",
    ]
    proc = subprocess.run(cmd, input=sql, text=True, capture_output=True, timeout=120)
    if proc.returncode != 0:
        raise ContractFail(f"mariadb query failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        return []
    headers = lines[0].split("\t")
    return [dict(zip(headers, line.split("\t"))) for line in lines[1:]]


def _load_actual_prices(template_codes: set[str]) -> dict[tuple[str, tuple[tuple[str, str], ...]], dict[str, Any]]:
    if not template_codes:
        return {}
    quoted = ", ".join("'" + code.replace("'", "''") + "'" for code in sorted(template_codes))
    rows = mariadb(
        f"""
        SELECT
            item.variant_of AS template_code,
            item.name AS item_code,
            attr.attribute,
            attr.attribute_value,
            price.price_list_rate
        FROM `tabItem` item
        JOIN `tabItem Variant Attribute` attr
            ON attr.parent = item.name
        LEFT JOIN `tabItem Price` price
            ON price.item_code = item.name
           AND price.price_list = '{PRICE_LIST}'
           AND price.selling = 1
        WHERE item.variant_of IN ({quoted})
          AND item.disabled = 0
        ORDER BY item.variant_of, item.name, attr.idx;
        """
    )
    by_item: dict[str, dict[str, Any]] = {}
    for row in rows:
        item = by_item.setdefault(
            row["item_code"],
            {
                "template_code": row["template_code"],
                "item_code": row["item_code"],
                "price_list_rate": row.get("price_list_rate"),
                "attributes": {},
            },
        )
        item["attributes"][str(row.get("attribute") or "")] = str(row.get("attribute_value") or "")

    actual: dict[tuple[str, tuple[tuple[str, str], ...]], dict[str, Any]] = {}
    for item in by_item.values():
        key = (item["template_code"], _combo_key(item["attributes"]))
        actual[key] = item
    return actual


def check_seed_price_parity() -> None:
    expected = _load_expected_prices()
    actual = _load_actual_prices({template for template, _combo in expected})
    failures: list[str] = []
    products_seen: set[str] = set()
    variants_checked = 0
    variants_that_would_change = 0
    missing_seed_expectations = 0
    samples: list[str] = []

    for key, item in actual.items():
        template, combo = key
        products_seen.add(template)
        expected_price = expected.get(key)
        if expected_price is None:
            missing_seed_expectations += 1
            if len(samples) < 20:
                samples.append(f"{item['item_code']} has no LT seed price for {dict(combo)}")
            continue
        variants_checked += 1
        actual_price = _money(item.get("price_list_rate"))
        if actual_price != expected_price:
            variants_that_would_change += 1
            if len(samples) < 20:
                samples.append(
                    f"{item['item_code']} expected ${expected_price}, found ${actual_price}"
                )

    if len(products_seen) < 45:
        failures.append(f"expected broad variant catalog coverage, checked only {len(products_seen)} products")
    if variants_checked < 10000:
        failures.append(f"expected 10k+ active variants checked, got {variants_checked}")
    if missing_seed_expectations:
        failures.append(
            f"{missing_seed_expectations} active variants did not resolve to LT seed prices: "
            + "; ".join(samples)
        )
    if variants_that_would_change:
        failures.append(
            f"{variants_that_would_change} variant prices differ from LT seed artifact: "
            + "; ".join(samples)
        )
    if failures:
        raise ContractFail("; ".join(failures))

    print(
        "[PASS] LT seed artifact prices match ERPNext Item Prices "
        f"for {len(products_seen)} products / {variants_checked} active variants"
    )


def main() -> int:
    parse_noop_args(__doc__)
    try:
        check_seed_price_parity()
    except SourceDataUnavailable as exc:
        print(f"[FAIL] lt_seed_price_source_data: {exc}")
        print("\n[PRODUCT PRICE MODIFIER CONTRACT] SOURCE DATA BLOCKED")
        return 1
    except Exception as exc:
        print(f"[FAIL] check_seed_price_parity: {exc}")
        print("\n[PRODUCT PRICE MODIFIER CONTRACT] FAIL")
        return 1

    print("\n[PRODUCT PRICE MODIFIER CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
