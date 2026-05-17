"""Price-readiness reporting for product-page template contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

from locally_twisted.catalog_variant_rules import normalize_variant_value
from locally_twisted.catalog_contract.source_builder import build_product_page_contract
from locally_twisted.product_page_labels import commerce_lane_label, product_page_type_label


@dataclass(frozen=True)
class PriceCoverageRow:
    slug: str
    product_page_type: str
    product_page_type_label: str
    commerce_lane: str
    commerce_lane_label: str
    current_product_page_type: str
    current_product_page_type_label: str
    current_commerce_lane: str
    current_commerce_lane_label: str
    required_axes: tuple[str, ...]
    expected_sale_units: int
    source_resolver_priced_units: int
    live_active_priced_units: int
    missing_live_units: tuple[str, ...] = field(default_factory=tuple)
    live_price_range: str = ""

    @property
    def live_ready(self) -> bool:
        return self.expected_sale_units > 0 and not self.missing_live_units

    @property
    def source_resolver_ready(self) -> bool:
        return self.expected_sale_units > 0 and self.source_resolver_priced_units >= self.expected_sale_units


@dataclass(frozen=True)
class PriceReadinessReport:
    rows: tuple[PriceCoverageRow, ...]
    failures: tuple[str, ...]

    def summary(self) -> dict[str, Any]:
        source_checkout_rows = [row for row in self.rows if row.commerce_lane == "checkout"]
        source_quote_rows = [row for row in self.rows if row.commerce_lane == "quote_first"]
        backend_checkout_rows = [row for row in self.rows if row.current_commerce_lane == "checkout"]
        backend_quote_rows = [row for row in self.rows if row.current_commerce_lane == "quote_first"]
        source_blocked = [row for row in self.rows if row.expected_sale_units and not row.source_resolver_ready]
        lane_drift = [
            row for row in self.rows
            if row.commerce_lane != row.current_commerce_lane
            or row.product_page_type != row.current_product_page_type
        ]
        return {
            "source_products": len(self.rows),
            "checkout_products": len(backend_checkout_rows),
            "quote_first_products": len(backend_quote_rows),
            "source_checkout_products": len(source_checkout_rows),
            "source_quote_first_products": len(source_quote_rows),
            "backend_checkout_products": len(backend_checkout_rows),
            "backend_quote_first_products": len(backend_quote_rows),
            "checkout_products_live_price_ready": sum(1 for row in backend_checkout_rows if row.live_ready),
            "checkout_expected_sale_units": sum(row.expected_sale_units for row in backend_checkout_rows),
            "checkout_live_priced_sale_units": sum(row.live_active_priced_units for row in backend_checkout_rows),
            "source_resolver_blocked_products": len(source_blocked),
            "source_backend_lane_differences": len(lane_drift),
        }

    def to_markdown(self) -> str:
        summary = self.summary()
        lane_drift = [
            row for row in self.rows
            if row.commerce_lane != row.current_commerce_lane
            or row.product_page_type != row.current_product_page_type
        ]
        lines = [
            "# Product Page Price Readiness Report",
            "",
            "This read-only report compares source product-page template classifications, current backend Website Item lanes, and live ERPNext Item Price coverage.",
            "It does not mutate ERPNext. It also does not declare the source artifact safe for destructive purge/import.",
            "",
            "## Summary",
            "",
            f"- Source products checked: {summary['source_products']}",
            f"- Source-template online checkout products: {summary['source_checkout_products']}",
            f"- Current backend online checkout products: {summary['backend_checkout_products']}",
            f"- Current backend quote-first products: {summary['backend_quote_first_products']}",
            f"- Source/backend lane differences: {summary['source_backend_lane_differences']}",
            f"- Backend checkout products with live ERPNext price coverage: {summary['checkout_products_live_price_ready']} / {summary['backend_checkout_products']}",
            f"- Checkout sale units with live ERPNext prices: {summary['checkout_live_priced_sale_units']} / {summary['checkout_expected_sale_units']}",
            f"- Products still blocked for source resolver-backed reimport prices: {summary['source_resolver_blocked_products']}",
            "",
            "## Checkout Price Gate",
            "",
        ]
        if self.failures:
            lines.append("**FAIL**")
            lines.append("")
            lines.extend(f"- {failure}" for failure in self.failures)
        else:
            lines.append("**PASS for current live ERPNext checkout price coverage.**")
            lines.append("")
            lines.append("This means the current live database has server-owned Item Price coverage for the backend checkout-classified Website Item rows.")
            lines.append("It does not mean source data can be purged/reimported safely; source resolver-backed prices remain a separate blocker.")

        lines.extend(["", "## Source / Backend Lane Differences", ""])
        if lane_drift:
            lines.extend(
                [
                    "| Slug | Source template | Source lane | Current backend template | Current backend lane |",
                    "|---|---|---|---|---|",
                ]
            )
            for row in lane_drift:
                lines.append(
                    f"| {row.slug} | {row.product_page_type_label} | {row.commerce_lane_label} | "
                    f"{row.current_product_page_type_label} | {row.current_commerce_lane_label} |"
                )
        else:
            lines.append("- None")

        lines.extend([
            "",
            "## Product Coverage",
            "",
            "| Slug | Source template | Source lane | Current backend template | Current backend lane | Required axes | Expected sale units | Source resolver-priced units | Live priced units | Live price range | Missing live units |",
            "|---|---|---|---|---|---|---:|---:|---:|---|---|",
        ])
        for row in self.rows:
            axes = ", ".join(row.required_axes) or "(single SKU)"
            missing = "<br>".join(row.missing_live_units) or ""
            lines.append(
                f"| {row.slug} | {row.product_page_type_label} | {row.commerce_lane_label} | "
                f"{row.current_product_page_type_label} | {row.current_commerce_lane_label} | "
                f"{axes} | {row.expected_sale_units} | {row.source_resolver_priced_units} | "
                f"{row.live_active_priced_units} | {row.live_price_range} | {missing} |"
            )
        return "\n".join(lines)


def build_price_readiness_report(
    products: list[dict[str, Any]],
    *,
    slug_to_group: dict[str, str],
    live_rows: list[dict[str, Any]],
) -> PriceReadinessReport:
    live_catalog = _LivePriceCatalog(live_rows)
    rows: list[PriceCoverageRow] = []
    failures: list[str] = []

    for product in products:
        contract = build_product_page_contract(
            product,
            category_hint=slug_to_group.get(str(product.get("slug") or ""), ""),
        )
        required_axes = tuple(axis.name for axis in contract.required_axes)
        expected = _expected_sale_units(product, required_axes)
        source_priced = _source_resolver_priced_units(product, expected, required_axes)
        live = live_catalog.coverage_for(str(product.get("slug") or ""), required_axes, expected)
        current_product_page_type = str(live.get("current_product_page_type") or contract.product_page_type)
        current_commerce_lane = str(live.get("current_commerce_lane") or contract.commerce_lane)
        row = PriceCoverageRow(
            slug=contract.slug,
            product_page_type=contract.product_page_type,
            product_page_type_label=contract.product_page_type_label,
            commerce_lane=contract.commerce_lane,
            commerce_lane_label=contract.commerce_lane_label,
            current_product_page_type=current_product_page_type,
            current_product_page_type_label=product_page_type_label(current_product_page_type),
            current_commerce_lane=current_commerce_lane,
            current_commerce_lane_label=commerce_lane_label(current_commerce_lane),
            required_axes=required_axes,
            expected_sale_units=len(expected),
            source_resolver_priced_units=source_priced,
            live_active_priced_units=live["priced_units"],
            missing_live_units=tuple(live["missing"]),
            live_price_range=live["price_range"],
        )
        rows.append(row)

        if current_commerce_lane == "checkout":
            if not expected:
                failures.append(f"{contract.slug} is backend checkout-classified but has no expected sale unit.")
            elif row.missing_live_units:
                failures.append(
                    f"{contract.slug} is backend checkout-classified but live ERPNext is missing prices for: "
                    + "; ".join(row.missing_live_units)
                )

    return PriceReadinessReport(rows=tuple(rows), failures=tuple(failures))


class _LivePriceCatalog:
    def __init__(self, rows: list[dict[str, Any]]):
        self._items: dict[str, dict[str, Any]] = {}
        self._website_items: dict[str, dict[str, str]] = {}
        for row in rows:
            item_code = _clean(row.get("item_code"))
            if not item_code:
                continue
            template_item = _clean(row.get("template_item")) or item_code
            if template_item:
                self._website_items.setdefault(
                    template_item,
                    {
                        "current_product_page_type": _clean(row.get("current_product_page_type")),
                        "current_commerce_lane": _clean(row.get("current_commerce_lane")),
                        "current_route": _clean(row.get("current_route")),
                        "current_published": _clean(row.get("current_published")),
                    },
                )
            item = self._items.setdefault(
                item_code,
                {
                    "template": template_item,
                    "variant_of": _clean(row.get("variant_of")),
                    "disabled": _clean(row.get("disabled")),
                    "price": _decimal_or_none(row.get("price_list_rate")),
                    "attributes": {},
                },
            )
            attribute = _clean(row.get("attribute"))
            value = _clean(row.get("attribute_value"))
            if attribute and value:
                item["attributes"][attribute] = normalize_variant_value(attribute, value)

    def coverage_for(
        self,
        slug: str,
        required_axes: tuple[str, ...],
        expected: dict[tuple[tuple[str, str], ...], str],
    ) -> dict[str, Any]:
        live_units: dict[tuple[tuple[str, str], ...], Decimal] = {}
        for item_code, item in self._items.items():
            if item.get("disabled") not in ("0", 0):
                continue
            if item.get("price") is None:
                continue

            if required_axes:
                if item.get("variant_of") != slug:
                    continue
                key = _combo_key(
                    {
                        axis: item["attributes"].get(axis)
                        for axis in required_axes
                        if item["attributes"].get(axis)
                    }
                )
                if key not in expected:
                    continue
            else:
                if item_code != slug and item.get("variant_of") != slug:
                    continue
                key = ()

            live_units.setdefault(key, item["price"])

        missing = [
            expected[key]
            for key in expected
            if key not in live_units
        ]
        prices = sorted(live_units.values())
        return {
            "priced_units": len(live_units),
            "missing": missing,
            "price_range": _price_range(prices),
            **self._website_items.get(slug, {}),
        }


def _expected_sale_units(product: dict[str, Any], required_axes: tuple[str, ...]) -> dict[tuple[tuple[str, str], ...], str]:
    if not required_axes:
        return {(): "single SKU"}

    units: dict[tuple[tuple[str, str], ...], str] = {}
    for row in product.get("valid_variants") or []:
        combo = row.get("combo") if isinstance(row, dict) else None
        if not isinstance(combo, dict):
            continue
        projected = {}
        for axis in required_axes:
            value = combo.get(axis)
            if value in (None, ""):
                projected = {}
                break
            projected[axis] = normalize_variant_value(axis, str(value))
        if not projected:
            continue
        key = _combo_key(projected)
        units.setdefault(key, _combo_label(projected))
    return units


def _source_resolver_priced_units(
    product: dict[str, Any],
    expected: dict[tuple[tuple[str, str], ...], str],
    required_axes: tuple[str, ...],
) -> int:
    if not expected:
        return 0
    if set(expected.keys()) == {()}:
        if product.get("base_price") is not None:
            return 1
        for row in product.get("valid_variants") or []:
            if row.get("erpnext_variant_price") is not None or row.get("price") is not None:
                return 1
        return 0

    priced: set[tuple[tuple[str, str], ...]] = set()
    for row in product.get("valid_variants") or []:
        if row.get("erpnext_variant_price") is None:
            continue
        combo = row.get("combo") or {}
        key = _combo_key(
            {
                axis: normalize_variant_value(axis, str(combo.get(axis)))
                for axis in required_axes
                if combo.get(axis) not in (None, "")
            }
        )
        if key in expected:
            priced.add(key)
    return len(priced)


def _combo_key(combo: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(axis), _canonical_value(value)) for axis, value in combo.items() if value not in (None, "")))


def _combo_label(combo: dict[str, Any]) -> str:
    return ", ".join(f"{axis}: {value}" for axis, value in sorted(combo.items()))


def _decimal_or_none(value: Any) -> Decimal | None:
    text = _clean(value)
    if not text:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def _price_range(prices: list[Decimal]) -> str:
    if not prices:
        return ""
    low = prices[0].quantize(Decimal("0.01"))
    high = prices[-1].quantize(Decimal("0.01"))
    if low == high:
        return f"${low}"
    return f"${low} - ${high}"


def _clean(value: Any) -> str:
    if value in (None, "NULL"):
        return ""
    return str(value).strip()


def _canonical_value(value: Any) -> str:
    text = str(value)
    replacements = {
        "\xe2\u20ac\u201d": "\u2014",
        "\xe2\u20ac\u201c": "\u201c",
        "\xe2\u20ac\u2122": "\u2019",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return " ".join(text.split())
