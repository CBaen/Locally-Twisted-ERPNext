"""Source price enrichment candidates for product-page imports.

This module is pure/reporting code. It does not mutate ERPNext or the saved
legacy_source scrape. Its job is to make price provenance explicit before any catalog
purge/reimport can use the source artifact.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

from locally_twisted.catalog_variant_rules import normalize_variant_value
from locally_twisted.catalog_contract.source_builder import REVIEW_WARNING_PREFIX, build_product_page_contract


SOURCE_RESOLVER = "source_resolver"
SOURCE_BASE_PRICE = "source_base_price"
LIVE_ERPNEXT_SNAPSHOT = "live_erpnext_snapshot"
PASS_PRICE_ENRICHMENT = "PASS_PRICE_ENRICHMENT"
BLOCKED_PRICE_ENRICHMENT = "BLOCKED_PRICE_ENRICHMENT"
PRICE_ENRICHABLE_BUT_PURGE_BLOCKED = "PRICE_ENRICHABLE_BUT_PURGE_BLOCKED"
PASS_PURGE_REIMPORT_PRICE_GATE = "PASS_PURGE_REIMPORT_PRICE_GATE"


@dataclass(frozen=True)
class SourceRowEvidence:
    source_row_index: int
    ptav_ids: tuple[int, ...]
    source_combo: dict[str, Any]
    source_price: Decimal | None
    projected_required_combo: dict[str, str]
    dropped_axes: dict[str, Any]
    sale_unit_key: str
    live_match_status: str
    live_item_codes: tuple[str, ...] = field(default_factory=tuple)
    live_item_code_count: int = 0
    live_price: Decimal | None = None
    blockers: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_row_index": self.source_row_index,
            "ptav_ids": list(self.ptav_ids),
            "source_combo": self.source_combo,
            "source_price": _money_or_none(self.source_price),
            "projected_required_combo": self.projected_required_combo,
            "dropped_axes": self.dropped_axes,
            "sale_unit_key": self.sale_unit_key,
            "live_match_status": self.live_match_status,
            "live_item_codes": list(self.live_item_codes),
            "live_item_code_count": self.live_item_code_count,
            "live_price": _money_or_none(self.live_price),
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True)
class SaleUnitEvidence:
    sale_unit_key: str
    projected_required_combo: dict[str, str]
    source_row_count: int
    live_active_match_count: int
    live_priced_match_count: int
    distinct_live_prices: tuple[Decimal, ...]
    chosen_price: Decimal | None
    price_source_kind: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "sale_unit_key": self.sale_unit_key,
            "projected_required_combo": self.projected_required_combo,
            "source_row_count": self.source_row_count,
            "live_active_match_count": self.live_active_match_count,
            "live_priced_match_count": self.live_priced_match_count,
            "distinct_live_prices": [_money(price) for price in self.distinct_live_prices],
            "chosen_price": _money_or_none(self.chosen_price),
            "price_source_kind": self.price_source_kind,
        }


@dataclass(frozen=True)
class PriceCandidate:
    slug: str
    combo_key: tuple[tuple[str, str], ...]
    combo_label: str
    price: Decimal
    source: str
    live_item_codes: tuple[str, ...] = field(default_factory=tuple)
    review_notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "combo": {axis: value for axis, value in self.combo_key},
            "label": self.combo_label,
            "price": _money(self.price),
            "source": self.source,
            "live_item_codes": list(self.live_item_codes),
            "review_notes": list(self.review_notes),
        }


@dataclass(frozen=True)
class PriceEnrichmentRow:
    slug: str
    legacy_source_id: str
    name: str
    source_url: str
    product_page_type: str
    product_page_type_label: str
    commerce_lane: str
    commerce_lane_label: str
    required_axes: tuple[str, ...]
    customization_axes: tuple[str, ...]
    add_ons: tuple[str, ...]
    axis_review_warnings: tuple[str, ...]
    expected_units: int
    candidates: tuple[PriceCandidate, ...]
    source_rows: tuple[SourceRowEvidence, ...] = field(default_factory=tuple)
    sale_units: tuple[SaleUnitEvidence, ...] = field(default_factory=tuple)
    blockers: tuple[str, ...] = field(default_factory=tuple)

    @property
    def source_resolver_units(self) -> int:
        return sum(1 for candidate in self.candidates if candidate.source == SOURCE_RESOLVER)

    @property
    def source_base_units(self) -> int:
        return sum(1 for candidate in self.candidates if candidate.source == SOURCE_BASE_PRICE)

    @property
    def live_snapshot_units(self) -> int:
        return sum(1 for candidate in self.candidates if candidate.source == LIVE_ERPNEXT_SNAPSHOT)

    @property
    def review_units(self) -> int:
        return sum(1 for candidate in self.candidates if candidate.review_notes)

    @property
    def ready(self) -> bool:
        return self.expected_units > 0 and len(self.candidates) == self.expected_units and not self.blockers

    @property
    def price_status(self) -> str:
        return PASS_PRICE_ENRICHMENT if not self.blockers else BLOCKED_PRICE_ENRICHMENT

    @property
    def purge_reimport_status(self) -> str:
        if self.blockers:
            return BLOCKED_PRICE_ENRICHMENT
        if self.axis_review_warnings or self.customization_axes or self.review_units:
            return PRICE_ENRICHABLE_BUT_PURGE_BLOCKED
        return PASS_PURGE_REIMPORT_PRICE_GATE

    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "legacy_source_id": self.legacy_source_id,
            "name": self.name,
            "source_url": self.source_url,
            "product_page_type": self.product_page_type,
            "commerce_lane": self.commerce_lane,
            "required_axes": list(self.required_axes),
            "customization_axes": list(self.customization_axes),
            "add_ons": list(self.add_ons),
            "axis_review_warnings": list(self.axis_review_warnings),
            "price_status": self.price_status,
            "purge_reimport_status": self.purge_reimport_status,
            "expected_units": self.expected_units,
            "candidate_units": len(self.candidates),
            "source_resolver_units": self.source_resolver_units,
            "source_base_units": self.source_base_units,
            "live_snapshot_units": self.live_snapshot_units,
            "review_units": self.review_units,
            "blockers": list(self.blockers),
            "source_rows": [row.to_dict() for row in self.source_rows],
            "sale_units": [row.to_dict() for row in self.sale_units],
            "candidates": [candidate.to_dict() for candidate in self.candidates],
        }


@dataclass(frozen=True)
class PriceEnrichmentReport:
    rows: tuple[PriceEnrichmentRow, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def blockers(self) -> tuple[str, ...]:
        return tuple(blocker for row in self.rows for blocker in row.blockers)

    def summary(self) -> dict[str, Any]:
        checkout_rows = [row for row in self.rows if row.commerce_lane == "checkout"]
        quote_rows = [row for row in self.rows if row.commerce_lane == "quote_first"]
        return {
            "source_products": len(self.rows),
            "checkout_products": len(checkout_rows),
            "quote_first_products": len(quote_rows),
            "expected_sale_units": sum(row.expected_units for row in self.rows),
            "candidate_sale_units": sum(len(row.candidates) for row in self.rows),
            "source_variant_rows": sum(len(row.source_rows) for row in self.rows),
            "source_resolver_units": sum(row.source_resolver_units for row in self.rows),
            "source_base_units": sum(row.source_base_units for row in self.rows),
            "live_snapshot_units": sum(row.live_snapshot_units for row in self.rows),
            "review_units": sum(row.review_units for row in self.rows),
            "blocked_products": sum(1 for row in self.rows if row.blockers),
            "purge_blocked_products": sum(1 for row in self.rows if row.purge_reimport_status != PASS_PURGE_REIMPORT_PRICE_GATE),
        }

    def to_candidate_artifact(self) -> dict[str, Any]:
        return {
            "schema_version": "lt-product-page-price-enrichment-v1",
            "header": self.metadata,
            "purpose": "Candidate import price map for the rebuilt ERPNext product-page architecture.",
            "warning": (
                "live_erpnext_snapshot prices preserve current ERPNext data for reimport; "
                "they are not business price approval."
            ),
            "summary": self.summary(),
            "products": [row.to_dict() for row in self.rows],
        }

    def to_markdown(self) -> str:
        summary = self.summary()
        lines = [
            "# Product Page Price Enrichment Report",
            "",
            "This read-only report builds a candidate price map for the rebuilt product-page import contract.",
            "It does not mutate ERPNext or `_resources/catalog-source/catalog.json`.",
            "",
            "## Summary",
            "",
            f"- Source products checked: {summary['source_products']}",
            f"- Online checkout products: {summary['checkout_products']}",
            f"- Quote request first products: {summary['quote_first_products']}",
            f"- Source variant rows preserved: {summary['source_variant_rows']}",
            f"- Expected import sale units: {summary['expected_sale_units']}",
            f"- Candidate-priced sale units: {summary['candidate_sale_units']}",
            f"- Source resolver-priced units: {summary['source_resolver_units']}",
            f"- Source base-price units: {summary['source_base_units']}",
            f"- Live ERPNext snapshot-priced units: {summary['live_snapshot_units']}",
            f"- Candidate units still needing business price review: {summary['review_units']}",
            f"- Blocked products: {summary['blocked_products']}",
            f"- Products still blocked for purge/reimport by review gates: {summary['purge_blocked_products']}",
            "",
            "## Gate Result",
            "",
        ]

        if self.blockers:
            lines.append("**BLOCKED.** At least one expected import sale unit has no unambiguous price candidate.")
            lines.append("")
            lines.extend(f"- {blocker}" for blocker in self.blockers)
        else:
            lines.append("**PASS for price-candidate coverage.**")
            lines.append("")
            lines.append(
                "Every expected import sale unit has a price candidate from source resolver rows, "
                "source base price, or the current live ERPNext snapshot."
            )
            lines.append(
                "This is still not business price approval; live-snapshot candidates need review before prices are promised to customers."
            )

        lines.extend(
            [
                "",
                "## Product Coverage",
                "",
                "| Slug | Template | Lane | Required axes | Expected units | Source resolver | Source base | Live snapshot | Review units | Blockers |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in self.rows:
            axes = ", ".join(row.required_axes) or "(single SKU)"
            blockers = "<br>".join(row.blockers)
            lines.append(
                f"| {row.slug} | {row.product_page_type_label} | {row.commerce_lane_label} | {axes} | "
                f"{row.expected_units} | {row.source_resolver_units} | {row.source_base_units} | "
                f"{row.live_snapshot_units} | {row.review_units} | {blockers} |"
            )
        return "\n".join(lines)


def build_price_enrichment_report(
    products: list[dict[str, Any]],
    *,
    slug_to_group: dict[str, str],
    live_rows: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> PriceEnrichmentReport:
    live_catalog = _LivePriceCatalog(live_rows)
    rows: list[PriceEnrichmentRow] = []

    for product in products:
        contract = build_product_page_contract(
            product,
            category_hint=slug_to_group.get(str(product.get("slug") or ""), ""),
        )
        slug = str(product.get("slug") or "")
        required_axes = tuple(axis.name for axis in contract.required_axes)
        customization_axes = tuple(axis.name for axis in contract.customization_axes)
        add_ons = tuple(add_on.key for add_on in contract.add_ons)
        axis_review_warnings = tuple(
            warning
            for warning in contract.warnings
            if warning.startswith(REVIEW_WARNING_PREFIX)
        )
        expected = _expected_sale_units(product, required_axes)
        source_candidates, source_blockers = _source_candidates(product, required_axes, expected)
        live_candidates, live_blockers = live_catalog.candidates_for(slug, required_axes, expected)

        candidates: list[PriceCandidate] = []
        blockers: list[str] = []
        blockers.extend(source_blockers)
        blockers.extend(live_blockers)

        candidates_by_key: dict[tuple[tuple[str, str], ...], PriceCandidate] = {}
        for key, label in expected.items():
            source_candidate = source_candidates.get(key)
            live_candidate = live_candidates.get(key)
            if source_candidate:
                candidates.append(source_candidate)
                candidates_by_key[key] = source_candidate
                if live_candidate and live_candidate.price != source_candidate.price:
                    blockers.append(
                        f"{slug} {label} has source price {_money(source_candidate.price)} "
                        f"but live ERPNext price {_money(live_candidate.price)}."
                    )
                continue

            if live_candidate:
                candidate = PriceCandidate(
                    slug=slug,
                    combo_key=key,
                    combo_label=label,
                    price=live_candidate.price,
                    source=LIVE_ERPNEXT_SNAPSHOT,
                    live_item_codes=live_candidate.live_item_codes,
                    review_notes=(
                        "Raw source lacks resolver-backed price; this candidate preserves current live ERPNext price only.",
                    ),
                )
                candidates.append(candidate)
                candidates_by_key[key] = candidate
                continue

            blockers.append(f"{slug} {label} has no source or live ERPNext price candidate.")

        source_rows = _source_row_evidence(
            product,
            required_axes,
            expected,
            live_candidates=live_candidates,
            source_candidates=source_candidates,
        )
        sale_units = _sale_unit_evidence(
            expected,
            source_rows,
            candidates_by_key=candidates_by_key,
            live_candidates=live_candidates,
        )

        rows.append(
            PriceEnrichmentRow(
                slug=contract.slug,
                legacy_source_id=str(product.get("legacy_source_id") or ""),
                name=str(product.get("name") or contract.source_name or contract.slug),
                source_url=str(product.get("url") or ""),
                product_page_type=contract.product_page_type,
                product_page_type_label=contract.product_page_type_label,
                commerce_lane=contract.commerce_lane,
                commerce_lane_label=contract.commerce_lane_label,
                required_axes=required_axes,
                customization_axes=customization_axes,
                add_ons=add_ons,
                axis_review_warnings=axis_review_warnings,
                expected_units=len(expected),
                candidates=tuple(candidates),
                source_rows=tuple(source_rows),
                sale_units=tuple(sale_units),
                blockers=tuple(blockers),
            )
        )

    return PriceEnrichmentReport(rows=tuple(rows), metadata=dict(metadata or {}))


@dataclass(frozen=True)
class _LiveCandidate:
    price: Decimal
    live_item_codes: tuple[str, ...]
    live_active_item_codes: tuple[str, ...]
    distinct_prices: tuple[Decimal, ...]


class _LivePriceCatalog:
    def __init__(self, rows: list[dict[str, Any]]):
        self._items: dict[str, dict[str, Any]] = {}
        for row in rows:
            item_code = _clean(row.get("item_code"))
            if not item_code:
                continue
            item = self._items.setdefault(
                item_code,
                {
                    "template": _clean(row.get("template_item")),
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

    def candidates_for(
        self,
        slug: str,
        required_axes: tuple[str, ...],
        expected: dict[tuple[tuple[str, str], ...], str],
    ) -> tuple[dict[tuple[tuple[str, str], ...], _LiveCandidate], tuple[str, ...]]:
        prices_by_key: dict[tuple[tuple[str, str], ...], dict[Decimal, list[str]]] = {}
        active_by_key: dict[tuple[tuple[str, str], ...], set[str]] = {}
        blockers: list[str] = []
        for item_code, item in self._items.items():
            if item.get("disabled") not in ("0", 0):
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
                if item_code != slug:
                    continue
                key = ()

            active_by_key.setdefault(key, set()).add(item_code)
            price = item.get("price")
            if price is not None:
                prices_by_key.setdefault(key, {}).setdefault(price, []).append(item_code)

        candidates: dict[tuple[tuple[str, str], ...], _LiveCandidate] = {}
        for key, price_map in prices_by_key.items():
            if len(price_map) > 1:
                label = expected.get(key, _combo_label(dict(key)))
                price_list = ", ".join(_money(price) for price in sorted(price_map))
                blockers.append(f"{slug} {label} has conflicting live ERPNext prices: {price_list}.")
                continue
            price, item_codes = next(iter(price_map.items()))
            candidates[key] = _LiveCandidate(
                price=price,
                live_item_codes=tuple(sorted(item_codes)),
                live_active_item_codes=tuple(sorted(active_by_key.get(key, set()))),
                distinct_prices=tuple(sorted(price_map)),
            )
        return candidates, tuple(blockers)


def _source_candidates(
    product: dict[str, Any],
    required_axes: tuple[str, ...],
    expected: dict[tuple[tuple[str, str], ...], str],
) -> tuple[dict[tuple[tuple[str, str], ...], PriceCandidate], tuple[str, ...]]:
    slug = str(product.get("slug") or "")
    if not expected:
        return {}, (f"{slug} has no expected sale units.",)

    if set(expected.keys()) == {()}:
        price = _decimal_or_none(product.get("base_price"))
        if price is None:
            return {}, (f"{slug} single SKU has no source base price.",)
        return {
            (): PriceCandidate(
                slug=slug,
                combo_key=(),
                combo_label=expected[()],
                price=price,
                source=SOURCE_BASE_PRICE,
            )
        }, ()

    price_maps: dict[tuple[tuple[str, str], ...], dict[Decimal, int]] = {}
    for row in product.get("valid_variants") or []:
        if not isinstance(row, dict):
            continue
        price = _decimal_or_none(row.get("erpnext_variant_price"))
        if price is None:
            continue
        combo = row.get("combo") or {}
        key = _combo_key(
            {
                axis: normalize_variant_value(axis, str(combo.get(axis)))
                for axis in required_axes
                if combo.get(axis) not in (None, "")
            }
        )
        if key not in expected:
            continue
        price_maps.setdefault(key, {})[price] = price_maps.setdefault(key, {}).get(price, 0) + 1

    candidates: dict[tuple[tuple[str, str], ...], PriceCandidate] = {}
    blockers: list[str] = []
    for key, price_map in price_maps.items():
        if len(price_map) > 1:
            label = expected.get(key, _combo_label(dict(key)))
            price_list = ", ".join(_money(price) for price in sorted(price_map))
            blockers.append(f"{slug} {label} has conflicting source resolver prices: {price_list}.")
            continue
        price = next(iter(price_map))
        candidates[key] = PriceCandidate(
            slug=slug,
            combo_key=key,
            combo_label=expected[key],
            price=price,
            source=SOURCE_RESOLVER,
        )
    return candidates, tuple(blockers)


def _source_row_evidence(
    product: dict[str, Any],
    required_axes: tuple[str, ...],
    expected: dict[tuple[tuple[str, str], ...], str],
    *,
    live_candidates: dict[tuple[tuple[str, str], ...], _LiveCandidate],
    source_candidates: dict[tuple[tuple[str, str], ...], PriceCandidate],
) -> list[SourceRowEvidence]:
    rows = product.get("valid_variants") or []
    if not rows:
        rows = [{"ptav_ids": [], "combo": {}, "price": product.get("base_price")}]

    evidence: list[SourceRowEvidence] = []
    for index, row in enumerate(rows):
        row = row if isinstance(row, dict) else {}
        combo = dict(row.get("combo") or {})
        projected: dict[str, str] = {}
        blockers: list[str] = []
        for axis in required_axes:
            value = combo.get(axis)
            if value in (None, ""):
                blockers.append(f"missing required axis {axis}")
                continue
            projected[axis] = normalize_variant_value(axis, str(value))
        key = _combo_key(projected) if not blockers else ()
        sale_key = _sale_unit_key(key)
        live_candidate = live_candidates.get(key)
        source_candidate = source_candidates.get(key)
        if blockers:
            live_match_status = "blocked_missing_required_axis"
        elif live_candidate:
            live_match_status = "matched_priced"
        elif source_candidate:
            live_match_status = "source_price_only"
        elif key in expected:
            live_match_status = "missing_live_price"
        else:
            live_match_status = "not_expected"
            blockers.append("projected source row is not an expected import sale unit")

        evidence.append(
            SourceRowEvidence(
                source_row_index=index,
                ptav_ids=tuple(int(value) for value in row.get("ptav_ids") or [] if str(value).isdigit()),
                source_combo=combo,
                source_price=_decimal_or_none(row.get("price")),
                projected_required_combo=projected,
                dropped_axes={axis: value for axis, value in combo.items() if axis not in required_axes},
                sale_unit_key=sale_key,
                live_match_status=live_match_status,
                live_item_codes=tuple((live_candidate.live_item_codes if live_candidate else ())[:5]),
                live_item_code_count=len(live_candidate.live_item_codes) if live_candidate else 0,
                live_price=live_candidate.price if live_candidate else None,
                blockers=tuple(blockers),
            )
        )
    return evidence


def _sale_unit_evidence(
    expected: dict[tuple[tuple[str, str], ...], str],
    source_rows: list[SourceRowEvidence],
    *,
    candidates_by_key: dict[tuple[tuple[str, str], ...], PriceCandidate],
    live_candidates: dict[tuple[tuple[str, str], ...], _LiveCandidate],
) -> list[SaleUnitEvidence]:
    rows_by_sale_key: dict[str, list[SourceRowEvidence]] = {}
    for row in source_rows:
        rows_by_sale_key.setdefault(row.sale_unit_key, []).append(row)

    sale_units: list[SaleUnitEvidence] = []
    for key in expected:
        sale_key = _sale_unit_key(key)
        live_candidate = live_candidates.get(key)
        candidate = candidates_by_key.get(key)
        sale_units.append(
            SaleUnitEvidence(
                sale_unit_key=sale_key,
                projected_required_combo=dict(key),
                source_row_count=len(rows_by_sale_key.get(sale_key, [])),
                live_active_match_count=len(live_candidate.live_active_item_codes) if live_candidate else 0,
                live_priced_match_count=len(live_candidate.live_item_codes) if live_candidate else 0,
                distinct_live_prices=live_candidate.distinct_prices if live_candidate else (),
                chosen_price=candidate.price if candidate else None,
                price_source_kind=candidate.source if candidate else "",
            )
        )
    return sale_units


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


def _combo_key(combo: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(axis), _canonical_value(value)) for axis, value in combo.items() if value not in (None, "")))


def _combo_label(combo: dict[str, Any]) -> str:
    return ", ".join(f"{axis}: {value}" for axis, value in sorted(combo.items()))


def _sale_unit_key(key: tuple[tuple[str, str], ...]) -> str:
    if not key:
        return "single SKU"
    return "|".join(f"{axis}={value}" for axis, value in key)


def _decimal_or_none(value: Any) -> Decimal | None:
    text = _clean(value)
    if not text:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def _money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01")))


def _money_or_none(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return _money(value)


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
