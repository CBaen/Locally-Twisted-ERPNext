"""ERPNext-side ProductPatternContract join and capability report.

The source mapper explains what the Odoo option grid means. This module joins
that source contract to current ERPNext Website Item, Item, Item Price, and
variant-attribute rows so import and resolver work can reason from generic
architecture capabilities instead of product-name exceptions.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Literal

from locally_twisted.catalog_contract.addon_rules import known_add_on_contracts_for_axis
from locally_twisted.catalog_variant_rules import normalize_variant_value


SCHEMA_VERSION = "lt-erpnext-product-pattern-contract-v1"
CONFIG_VERSION = "lt-product-config-v1"
PRICE_LIST = "Standard Selling"
LINE_FIELDNAMES = {
    "template_item": "custom_lt_product_template_item",
    "page_type": "custom_lt_product_page_type",
    "version": "custom_lt_configuration_version",
    "summary": "custom_lt_configuration_summary",
    "json": "custom_lt_configuration_json",
}

Capability = Literal[
    "direct_checkout_ready",
    "checkout_architecture_gap",
    "quote_first_supported",
    "needs_review_or_missing",
]

CHECKOUT_BLOCKING_PATTERNS = {
    "large_single_choice_color",
    "multi_color_recipes",
    "conditional_pricing",
    "freeform_customer_text",
    "add_ons",
}


@dataclass(frozen=True)
class RepresentativePricedItem:
    item_code: str
    price: str | None
    price_source: str
    selected_options: dict[str, str] = field(default_factory=dict)
    provenance: str = "live_erpnext_item_price"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ServerBoundaryContract:
    selected_config_schema: dict[str, Any]
    representative_priced_item: RepresentativePricedItem | None
    add_on_line_contract: dict[str, Any]
    customization_validation: dict[str, Any]
    totals_provenance: dict[str, Any]
    cart_line_key_contract: dict[str, Any]
    sales_document_fields: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["representative_priced_item"] = (
            self.representative_priced_item.to_dict() if self.representative_priced_item else None
        )
        return data


@dataclass(frozen=True)
class ERPNextProductPatternRow:
    slug: str
    source_name: str
    patterns: tuple[str, ...]
    capability: Capability
    capability_reasons: tuple[str, ...]
    website_item: dict[str, Any]
    item_template: dict[str, Any]
    live_counts: dict[str, int]
    source_axes: dict[str, list[str]]
    live_required_axis_coverage: dict[str, Any]
    pricing_provenance: dict[str, Any]
    media_roles: dict[str, Any]
    dependency_matrix: dict[str, Any]
    checkout_eligibility: dict[str, Any]
    source_integrity: dict[str, Any]
    source_import_requirements: tuple[str, ...]
    source_import_implications: tuple[str, ...]
    server_boundary: ServerBoundaryContract

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["server_boundary"] = self.server_boundary.to_dict()
        return data


@dataclass(frozen=True)
class ERPNextProductPatternReport:
    rows: tuple[ERPNextProductPatternRow, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        capability_counts = Counter(row.capability for row in self.rows)
        lane_counts = Counter(_website_lane(row.website_item) for row in self.rows)
        pattern_counts: Counter[str] = Counter()
        blocker_counts: Counter[str] = Counter()
        for row in self.rows:
            pattern_counts.update(row.patterns)
            blocker_counts.update(row.checkout_eligibility.get("blocking_reasons") or [])
        inventory_failures = self.inventory_failures()
        checkout_gate_failures = self.checkout_gate_failures()
        return {
            "schema_version": SCHEMA_VERSION,
            "source_products": len(self.rows),
            "inventory_ok": not inventory_failures,
            "checkout_gate_ok": not checkout_gate_failures,
            "capability_counts": dict(sorted(capability_counts.items())),
            "website_lane_counts": dict(sorted(lane_counts.items())),
            "pattern_counts": dict(sorted(pattern_counts.items())),
            "checkout_blocker_counts": dict(sorted(blocker_counts.items())),
            "explicit_checkout_products": lane_counts.get("checkout", 0),
            "direct_checkout_ready_products": capability_counts.get("direct_checkout_ready", 0),
            "quote_first_supported_products": capability_counts.get("quote_first_supported", 0),
            "missing_or_needs_review_products": capability_counts.get("needs_review_or_missing", 0),
        }

    def inventory_failures(self) -> list[str]:
        failures = []
        missing_website = sorted(row.slug for row in self.rows if not row.website_item)
        if missing_website:
            failures.append(f"source products missing published Website Item rows: {missing_website}")
        missing_source = sorted(
            row.slug for row in self.rows if row.website_item and not row.source_integrity
        )
        if missing_source:
            failures.append(f"published Website Items missing Odoo source integrity: {missing_source}")
        return failures

    def checkout_gate_failures(self) -> list[str]:
        failures = []
        missing_price = sorted(
            row.slug
            for row in self.rows
            if row.website_item and row.pricing_provenance.get("representative") is None
        )
        if missing_price:
            failures.append(f"published Website Items missing item-specific Standard Selling price: {missing_price}")
        unresolved = sorted(
            row.slug
            for row in self.rows
            if row.website_item and row.checkout_eligibility.get("blocking_reasons")
        )
        if unresolved:
            failures.append(f"published Website Items with unresolved checkout gate blockers: {unresolved}")
        lost_mapper = sorted(
            row.slug
            for row in self.rows
            if row.website_item
            and (
                not row.patterns
                or not row.source_integrity
                or not row.source_import_requirements
            )
        )
        if lost_mapper:
            failures.append(f"published Website Items missing mapper pattern preservation: {lost_mapper}")
        return failures

    def to_artifact(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "metadata": self.metadata,
            "read_only": True,
            "destructive_allowed": False,
            "purpose": "ERPNext/Frappe ProductPatternContract architecture capability report.",
            "summary": self.summary(),
            "ok": not self.inventory_failures() and not self.checkout_gate_failures(),
            "inventory_ok": not self.inventory_failures(),
            "checkout_gate_ok": not self.checkout_gate_failures(),
            "inventory_failures": self.inventory_failures(),
            "checkout_gate_failures": self.checkout_gate_failures(),
            "server_side_contract_boundary": _server_boundary_overview(),
            "products": [row.to_dict() for row in self.rows],
        }

    def to_markdown(self) -> str:
        summary = self.summary()
        lines = [
            "# ERPNext Product Pattern Contract",
            "",
            "This report joins the Odoo source option-pattern contract to current ERPNext records.",
            "It is read-only and classifies architecture capability, not product-specific fixes.",
            "",
            "## Summary",
            "",
            f"- Source products checked: {summary['source_products']}",
            f"- Explicit checkout Website Items: {summary['explicit_checkout_products']}",
            f"- Direct-checkout ready by generic architecture: {summary['direct_checkout_ready_products']}",
            f"- Quote-first supported by generic architecture: {summary['quote_first_supported_products']}",
            f"- Needs review or missing records: {summary['missing_or_needs_review_products']}",
            f"- Capability counts: {_format_counts(summary['capability_counts'])}",
            f"- Website lane counts: {_format_counts(summary['website_lane_counts'])}",
            f"- Checkout blocker counts: {_format_counts(summary['checkout_blocker_counts'])}",
            "",
            "## Server-Side Boundary",
            "",
        ]
        overview = _server_boundary_overview()
        for key, value in overview.items():
            lines.append(f"- `{key}`: {value}")

        lines.extend(
            [
                "",
                "## Product Rows",
                "",
                "| Example product | Slug | Website lane | Capability | Required axes | Customization axes | Add-on axes | Representative item | Blocking reasons |",
                "|---|---|---|---|---|---|---|---|---|",
            ]
        )
        for row in self.rows:
            axes = row.source_axes
            rep = row.server_boundary.representative_priced_item
            rep_label = f"{rep.item_code} ({rep.price})" if rep else ""
            lines.append(
                "| "
                + " | ".join(
                    [
                        row.source_name,
                        f"`{row.slug}`",
                        _website_lane(row.website_item),
                        row.capability,
                        ", ".join(axes.get("required_sale_unit_axes") or []),
                        ", ".join(axes.get("customization_axes") or []),
                        ", ".join(axes.get("add_on_axes") or []),
                        rep_label,
                        "<br>".join(row.checkout_eligibility.get("blocking_reasons") or []),
                    ]
                )
                + " |"
            )
        return "\n".join(lines).rstrip() + "\n"


def build_erpnext_product_pattern_report(
    source_artifact: dict[str, Any],
    erpnext_rows: dict[str, list[dict[str, Any]]],
    *,
    metadata: dict[str, Any] | None = None,
) -> ERPNextProductPatternReport:
    products = source_artifact.get("products") or []
    source_slugs = {str(product.get("slug") or "") for product in products if product.get("slug")}
    published_slugs = {
        str(row.get("item_code") or "")
        for row in erpnext_rows.get("website_items") or []
        if row.get("item_code")
    }
    missing_source_products = [
        {"slug": slug, "source_name": slug, "patterns": (), "axis_contracts": ()}
        for slug in sorted(published_slugs - source_slugs)
    ]
    rows = tuple(_build_row(product, erpnext_rows) for product in [*products, *missing_source_products])
    return ERPNextProductPatternReport(rows=rows, metadata=dict(metadata or {}))


def _build_row(product: dict[str, Any], erpnext_rows: dict[str, list[dict[str, Any]]]) -> ERPNextProductPatternRow:
    slug = str(product.get("slug") or "").strip()
    website_item = _first_by_key(erpnext_rows.get("website_items") or [], "item_code", slug)
    template = _first_by_key(erpnext_rows.get("items") or [], "item_code", slug)
    variants = [
        row for row in erpnext_rows.get("items") or []
        if str(row.get("variant_of") or "") == slug and _is_enabled(row)
    ]
    price_by_item = _price_by_item(erpnext_rows.get("item_prices") or [])
    add_on_price_by_item = _price_by_item(erpnext_rows.get("add_on_prices") or [])
    attrs_by_item = _attrs_by_item(erpnext_rows.get("variant_attributes") or [])
    source_axes = _source_axes(product)
    expected = _expected_dependency_matrix(product, source_axes["required_sale_unit_axes"])
    live_coverage = _live_axis_coverage(expected, variants, attrs_by_item, price_by_item)
    representative = _representative_priced_item(
        slug=slug,
        required_axes=source_axes["required_sale_unit_axes"],
        template=template,
        variants=variants,
        attrs_by_item=attrs_by_item,
        price_by_item=price_by_item,
    )
    checkout = _checkout_eligibility(
        product=product,
        website_item=website_item,
        template=template,
        representative=representative,
        line_fields=erpnext_rows.get("line_fields") or [],
        live_coverage=live_coverage,
        add_on_price_by_item=add_on_price_by_item,
    )
    capability, reasons = _capability(website_item, checkout)
    return ERPNextProductPatternRow(
        slug=slug,
        source_name=str(product.get("source_name") or product.get("example_label") or slug),
        patterns=tuple(str(pattern) for pattern in product.get("patterns") or ()),
        capability=capability,
        capability_reasons=tuple(reasons),
        website_item=_public_row(website_item),
        item_template=_public_row(template),
        live_counts={
            "enabled_variants": len(variants),
            "priced_enabled_variants": sum(1 for row in variants if row.get("item_code") in price_by_item),
            "source_expected_sale_units": len(expected),
        },
        source_axes=source_axes,
        live_required_axis_coverage=live_coverage,
        pricing_provenance=_pricing_provenance(representative, live_coverage),
        media_roles=dict(product.get("media_roles") or {}),
        source_integrity=dict(product.get("source_integrity") or {}),
        source_import_requirements=tuple(str(value) for value in product.get("erpnext_contract_requirements") or ()),
        source_import_implications=tuple(str(value) for value in product.get("import_implications") or ()),
        dependency_matrix={
            "axes": source_axes["required_sale_unit_axes"],
            "expected_combination_count": len(expected),
            "expected_combinations": [dict(key) for key in expected[:50]],
            "truncated": len(expected) > 50,
        },
        checkout_eligibility=checkout,
        server_boundary=_server_boundary(
            product=product,
            website_item=website_item,
            representative=representative,
            checkout=checkout,
            source_axes=source_axes,
        ),
    )


def _source_axes(product: dict[str, Any]) -> dict[str, list[str]]:
    groups = {
        "required_sale_unit_axes": [],
        "customization_axes": [],
        "add_on_axes": [],
        "review_only_axes": [],
        "conditional_pricing_axes": [],
        "freeform_customer_text_axes": [],
    }
    for axis in product.get("axis_contracts") or []:
        name = str(axis.get("name") or "")
        patterns = set(axis.get("patterns") or [])
        if "required_sale_unit_axis" in patterns:
            groups["required_sale_unit_axes"].append(name)
        if patterns & {"large_single_choice_color", "multi_color_recipe_customization"}:
            groups["customization_axes"].append(name)
        if "add_on_axis" in patterns:
            groups["add_on_axes"].append(name)
        if "review_only_axis" in patterns:
            groups["review_only_axes"].append(name)
        if "conditional_pricing_candidate" in patterns:
            groups["conditional_pricing_axes"].append(name)
        if "freeform_customer_text_candidate" in patterns:
            groups["freeform_customer_text_axes"].append(name)
    return groups


def _expected_dependency_matrix(product: dict[str, Any], required_axes: list[str]) -> list[tuple[tuple[str, str], ...]]:
    if not required_axes:
        return [()]
    seen = {}
    for row in product.get("source_rows") or []:
        combo = row.get("combo") or {}
        projected = {}
        for axis in required_axes:
            value = combo.get(axis)
            if value in (None, ""):
                projected = {}
                break
            projected[axis] = str(normalize_variant_value(axis, str(value)))
        if projected:
            key = tuple(sorted(projected.items()))
            seen[key] = key
    if seen:
        return [seen[key] for key in sorted(seen)]
    # Source artifact from pattern_mapper does not carry raw source rows; use
    # axis value cross-product only for tiny finite axes where it is useful.
    axis_values = []
    for axis in product.get("axis_contracts") or []:
        if axis.get("name") in required_axes:
            values = tuple(str(value) for value in axis.get("sample_values") or [])
            if values:
                axis_values.append((str(axis.get("name")), values))
    if not axis_values:
        return [()]
    combos = [()]
    for axis, values in axis_values:
        combos = [(*combo, (axis, value)) for combo in combos for value in values]
    return [tuple(sorted(combo)) for combo in combos]


def _live_axis_coverage(
    expected: list[tuple[tuple[str, str], ...]],
    variants: list[dict[str, Any]],
    attrs_by_item: dict[str, dict[str, str]],
    price_by_item: dict[str, Decimal],
) -> dict[str, Any]:
    if expected == [()]:
        return {
            "expected_units": 1,
            "priced_units": 0,
            "coverage_status": "representative_item_required",
            "missing_units": [],
            "priced_examples": [],
        }
    expected_set = set(expected)
    priced = {}
    for variant in variants:
        item_code = str(variant.get("item_code") or "")
        if item_code not in price_by_item:
            continue
        attrs = attrs_by_item.get(item_code) or {}
        key = tuple(
            sorted(
                (axis, str(normalize_variant_value(axis, attrs.get(axis, ""))))
                for axis, _value in expected[0]
                if attrs.get(axis)
            )
        )
        if key in expected_set:
            priced[key] = item_code
    missing = sorted(expected_set - set(priced))
    return {
        "expected_units": len(expected_set),
        "priced_units": len(priced),
        "coverage_status": "covered" if not missing else "partial",
        "missing_units": [dict(key) for key in missing[:20]],
        "missing_units_truncated": len(missing) > 20,
        "priced_examples": [
            {"combo": dict(key), "item_code": item_code}
            for key, item_code in list(sorted(priced.items()))[:20]
        ],
    }


def _representative_priced_item(
    *,
    slug: str,
    required_axes: list[str],
    template: dict[str, Any],
    variants: list[dict[str, Any]],
    attrs_by_item: dict[str, dict[str, str]],
    price_by_item: dict[str, Decimal],
) -> RepresentativePricedItem | None:
    if template and slug in price_by_item and not required_axes:
        return RepresentativePricedItem(slug, _money(price_by_item[slug]), "live_template_item_price")
    for variant in sorted(variants, key=lambda row: str(row.get("item_code") or "")):
        item_code = str(variant.get("item_code") or "")
        price = price_by_item.get(item_code)
        if price is None:
            continue
        attrs = attrs_by_item.get(item_code) or {}
        selected = {
            axis: str(normalize_variant_value(axis, attrs[axis]))
            for axis in required_axes
            if attrs.get(axis)
        }
        if required_axes and set(selected) != set(required_axes):
            continue
        return RepresentativePricedItem(
            item_code=item_code,
            price=_money(price),
            price_source="live_variant_item_price",
            selected_options=selected,
        )
    return None


def _checkout_eligibility(
    *,
    product: dict[str, Any],
    website_item: dict[str, Any],
    template: dict[str, Any],
    representative: RepresentativePricedItem | None,
    line_fields: list[dict[str, Any]],
    live_coverage: dict[str, Any],
    add_on_price_by_item: dict[str, Decimal],
) -> dict[str, Any]:
    patterns = set(product.get("patterns") or [])
    blocking = []
    missing_mapper_contract = (
        not patterns
        or not product.get("source_integrity")
        or not product.get("erpnext_contract_requirements")
    )
    if missing_mapper_contract and website_item:
        blocking.append("missing_odoo_pattern_mapper_contract")
    if not website_item:
        blocking.append("missing_website_item")
    if not template:
        blocking.append("missing_template_item")
    if _website_lane(website_item) == "needs_review":
        blocking.append("website_item_needs_review")
    source_axes = _source_axes(product)
    if _website_lane(website_item) == "checkout" and patterns & CHECKOUT_BLOCKING_PATTERNS:
        unpriced_add_on_axes = _unpriced_add_on_axes(source_axes.get("add_on_axes") or [], add_on_price_by_item)
        if unpriced_add_on_axes:
            blocking.append("priced_add_on_line_contract_needed")
        if (
            "conditional_pricing" in patterns
            and live_coverage.get("coverage_status") not in {"covered", "representative_item_required"}
        ):
            blocking.append("conditional_pricing_matrix_needed")
        if patterns & {"large_single_choice_color", "multi_color_recipes", "freeform_customer_text"}:
            if not _representative_only_checkout(source_axes, representative):
                blocking.append("checkout_customization_contract_needed")
    if source_axes["review_only_axes"] and _website_lane(website_item) == "checkout":
        blocking.append("review_only_add_on_checkout_contract_needed")
    if representative is None and _website_lane(website_item) == "checkout":
        blocking.append("missing_representative_priced_item")
    if live_coverage.get("coverage_status") == "partial" and _website_lane(website_item) == "checkout":
        blocking.append("missing_required_axis_price_coverage")
    missing_line_fields = sorted(set(LINE_FIELDNAMES.values()) - {str(row.get("fieldname")) for row in line_fields})
    if missing_line_fields:
        blocking.append("missing_sales_line_configuration_fields")
    return {
        "website_lane": _website_lane(website_item),
        "explicit_checkout": _website_lane(website_item) == "checkout",
        "representative_priced_item_ready": representative is not None,
        "line_configuration_fields_ready": not missing_line_fields,
        "missing_line_fields": missing_line_fields,
        "blocking_reasons": sorted(set(blocking)),
        "eligible_for_direct_checkout_by_generic_contract": not blocking and _website_lane(website_item) == "checkout",
    }


def _unpriced_add_on_axes(add_on_axes: list[str], add_on_price_by_item: dict[str, Decimal]) -> list[str]:
    unpriced = []
    for axis in add_on_axes:
        contracts = known_add_on_contracts_for_axis(axis)
        if not contracts:
            unpriced.append(axis)
            continue
        item_codes = [str(contract.get("item_code") or "") for contract in contracts if contract.get("item_code")]
        if not item_codes or any(item_code not in add_on_price_by_item for item_code in item_codes):
            unpriced.append(axis)
    return unpriced


def _capability(website_item: dict[str, Any], checkout: dict[str, Any]) -> tuple[Capability, list[str]]:
    lane = _website_lane(website_item)
    blockers = checkout.get("blocking_reasons") or []
    if lane == "checkout" and not blockers:
        return "direct_checkout_ready", ["explicit checkout lane has representative priced item and no generic blockers"]
    if lane == "checkout":
        return "checkout_architecture_gap", blockers
    if lane == "quote_first" and "missing_website_item" not in blockers:
        return "quote_first_supported", ["quote-first lane can preserve source meaning without cart checkout"]
    return "needs_review_or_missing", blockers or ["missing or needs-review ERPNext lane"]


def _representative_only_checkout(
    source_axes: dict[str, list[str]],
    representative: RepresentativePricedItem | None,
) -> bool:
    return bool(
        representative
        and not source_axes.get("required_sale_unit_axes")
        and not source_axes.get("add_on_axes")
        and not source_axes.get("review_only_axes")
    )


def _server_boundary(
    *,
    product: dict[str, Any],
    website_item: dict[str, Any],
    representative: RepresentativePricedItem | None,
    checkout: dict[str, Any],
    source_axes: dict[str, list[str]],
) -> ServerBoundaryContract:
    selected_options = representative.selected_options if representative else {}
    add_on_axes = source_axes.get("add_on_axes") or []
    customization_axes = source_axes.get("customization_axes") or []
    representative_only = _representative_only_checkout(source_axes, representative)
    return ServerBoundaryContract(
        selected_config_schema={
            "schema_version": CONFIG_VERSION,
            "website_item_code": product.get("slug"),
            "selected_options": selected_options,
            "add_ons": [{"source_axis": axis, "status": "requires_add_on_registry"} for axis in add_on_axes],
            "customizations": [{"source_axis": axis, "status": "requires_validation_contract"} for axis in customization_axes],
        },
        representative_priced_item=representative,
        add_on_line_contract={
            "status": "requires_priced_item_registry" if add_on_axes else "not_required",
            "source_axes": add_on_axes,
            "line_source": "lt_product_page_add_on",
            "required_fields": ("item_code", "qty", "rate", "amount", "description", "receipt_label"),
        },
        customization_validation={
            "status": (
                "checkout_validation_contract_needed"
                if customization_axes and _website_lane(website_item) == "checkout"
                and not representative_only
                else "not_exposed_in_representative_checkout"
                if customization_axes and representative_only and _website_lane(website_item) == "checkout"
                else "quote_first_or_not_required"
            ),
            "source_axes": customization_axes,
        },
        totals_provenance={
            "item_price_source": representative.provenance if representative else "",
            "base_item_price": representative.price if representative else None,
            "add_on_price_source": "ERPNext Item Price for registered add-on Items",
            "total_rule": "base representative item price + validated priced add-on lines",
        },
        cart_line_key_contract={
            "formula": "item_code::json.dumps(configuration, sort_keys=True, separators=(',', ':'))",
            "requires_selected_options_match_resolved_item": True,
            "checkout_blocked": bool(checkout.get("blocking_reasons")),
        },
        sales_document_fields={
            "sales_order_item": LINE_FIELDNAMES,
            "sales_invoice_item": LINE_FIELDNAMES,
            "summary_source": "custom_lt_configuration_summary",
            "json_source": "custom_lt_configuration_json",
            "source_integrity_required": bool(product.get("source_integrity")),
            "import_requirements": tuple(str(value) for value in product.get("erpnext_contract_requirements") or ()),
        },
    )


def _server_boundary_overview() -> dict[str, str]:
    return {
        "selected_config": "versioned payload containing selected_options, add_ons, and customizations",
        "item_resolution": "selected config resolves to one ERPNext item_code or representative priced item",
        "add_on_lines": "registered add-ons become separate priced Sales Order/Sales Invoice lines",
        "customization_validation": "unsupported checkout customizations fail loudly; quote-first can preserve them",
        "totals_provenance": "totals derive from ERPNext Item Price rows plus registered add-on Item Price rows",
        "cart_line_key": "item_code plus canonical configuration JSON prevents option collisions",
        "document_summary": "SO/SI line fields preserve template, page type, schema version, summary, and JSON",
    }


def _pricing_provenance(
    representative: RepresentativePricedItem | None,
    live_coverage: dict[str, Any],
) -> dict[str, Any]:
    return {
        "representative": representative.to_dict() if representative else None,
        "required_axis_coverage": live_coverage,
        "trusted_for_checkout": representative is not None and live_coverage.get("coverage_status") in {
            "covered",
            "representative_item_required",
        },
    }


def _price_by_item(rows: list[dict[str, Any]]) -> dict[str, Decimal]:
    result = {}
    for row in rows:
        item_code = str(row.get("item_code") or "")
        price = _decimal_or_none(row.get("price_list_rate"))
        if item_code and price is not None:
            result[item_code] = price
    return result


def _attrs_by_item(rows: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = defaultdict(dict)
    for row in rows:
        parent = str(row.get("parent") or "")
        attribute = str(row.get("attribute") or "")
        value = str(row.get("attribute_value") or "")
        if parent and attribute and value:
            result[parent][attribute] = value
    return dict(result)


def _first_by_key(rows: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    for row in rows:
        if str(row.get(key) or "") == value:
            return row
    return {}


def _public_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in row.items()
        if key not in {"owner", "modified_by"}
    } if row else {}


def _website_lane(row: dict[str, Any]) -> str:
    if not row:
        return "missing"
    return str(row.get("lt_commerce_lane") or "needs_review")


def _is_enabled(row: dict[str, Any]) -> bool:
    return str(row.get("disabled") or "0") in {"0", "False", "false", ""}


def _decimal_or_none(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01")))


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def canonical_cart_line_key(item_code: str, configuration: dict[str, Any] | None) -> str:
    """Return the future resolver boundary's stable cart-line identity."""
    config = json.dumps(configuration or {}, sort_keys=True, separators=(",", ":"), default=str)
    return f"{item_code}::{config}"
