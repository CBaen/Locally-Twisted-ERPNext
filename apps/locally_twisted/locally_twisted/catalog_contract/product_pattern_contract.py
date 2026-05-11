"""Generic backend contract for purchasable product configurations.

This module is intentionally data-oriented. It describes what ERPNext/Frappe
must know before a product page can become paid checkout, without mutating
Website Items, Items, prices, or customer records.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any, Callable, Literal

from locally_twisted.catalog_contract.addon_rules import (
    classify_axis,
    known_add_on_contracts_for_axis,
)
from locally_twisted.catalog_contract.color_rules import is_balloon_color_axis
from locally_twisted.catalog_contract.pattern_mapper import (
    build_product_pattern_contract as build_source_pattern_contract,
)


SCHEMA_VERSION = "lt-product-pattern-contract-v1"
CART_CONFIGURATION_VERSION = "lt-product-config-v1"
STANDARD_PRICE_LIST = "Standard Selling"

AxisRole = Literal["sale_unit", "customization", "add_on", "review_only"]
AxisSource = Literal["odoo_source", "erpnext_variant", "combined"]
AxisStatus = Literal["ready", "needs_mapping", "needs_review"]
PricingStatus = Literal["ready", "missing", "incomplete", "conflict_needs_fix"]
MediaStatus = Literal["ready", "primary_missing", "uncertain_roles"]
DependencyStatus = Literal["ready", "not_required", "missing_source_matrix", "mismatch"]
CheckoutStatus = Literal[
    "checkout_ready",
    "lane_mapping_only",
    "needs_pricing",
    "needs_add_on_pricing",
    "needs_customization_payload",
    "needs_media_review",
    "dependency_mismatch",
]
FailLoudState = Literal[
    "missing_price",
    "review_only_add_on",
    "unpriced_add_on",
    "unsupported_customization_payload",
    "media_uncertainty",
    "dependency_mismatch",
]
ResolverMode = Literal["checkout", "quote", "report"]


LINE_CONFIGURATION_FIELDS = {
    "Sales Order Item": (
        "custom_lt_product_template_item",
        "custom_lt_product_page_type",
        "custom_lt_configuration_version",
        "custom_lt_configuration_summary",
        "custom_lt_configuration_json",
    ),
    "Sales Invoice Item": (
        "custom_lt_product_template_item",
        "custom_lt_product_page_type",
        "custom_lt_configuration_version",
        "custom_lt_configuration_summary",
        "custom_lt_configuration_json",
    ),
    "Quotation Item": (
        "custom_lt_product_template_item",
        "custom_lt_product_page_type",
        "custom_lt_configuration_version",
        "custom_lt_configuration_summary",
        "custom_lt_configuration_json",
    ),
}


class ProductPatternContractError(ValueError):
    """Raised when a selected configuration violates the backend contract."""


@dataclass(frozen=True)
class AxisContract:
    name: str
    role: AxisRole
    values: tuple[str, ...] = field(default_factory=tuple)
    selector_type: str = "single_select"
    source: AxisSource = "odoo_source"
    status: AxisStatus = "ready"
    pricing_required: bool = True
    allows_multiple_values: bool = False
    add_on_key: str = ""
    add_on_contract: dict[str, Any] = field(default_factory=dict)
    review_reason: str = ""
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PricingProvenance:
    status: PricingStatus
    price_list: str = STANDARD_PRICE_LIST
    source_base_price: str | None = None
    erpnext_price_min: str | None = None
    erpnext_price_max: str | None = None
    expected_sale_units: int = 0
    priced_sale_units: int = 0
    missing_sale_units: int = 0
    representative_item_code: str = ""
    representative_price: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MediaRoleContract:
    status: MediaStatus
    primary_image: str = ""
    variant_image_count: int = 0
    gallery_count: int = 0
    uncertain_count: int = 0
    roles: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DependencyMatrixContract:
    status: DependencyStatus
    axes: tuple[str, ...] = field(default_factory=tuple)
    source_combination_count: int = 0
    erpnext_variant_count: int = 0
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CheckoutEligibility:
    status: CheckoutStatus
    current_page_type: str = ""
    current_commerce_lane: str = ""
    fail_loud_states: tuple[FailLoudState, ...] = field(default_factory=tuple)
    resolver_boundary: str = (
        "contract + selected_config -> item_code or priced representative item, "
        "validated add-on lines, customization payload, cart line key, SO/SI summary"
    )
    required_work: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProductPatternContract:
    slug: str
    source_name: str
    route: str
    item_code: str
    current_page_type: str
    current_commerce_lane: str
    axis_contracts: tuple[AxisContract, ...]
    pricing: PricingProvenance
    media: MediaRoleContract
    dependency_matrix: DependencyMatrixContract
    checkout_eligibility: CheckoutEligibility
    cart_contract: dict[str, Any]
    order_preservation_contract: dict[str, Any]
    source_patterns: tuple[str, ...] = field(default_factory=tuple)
    source_integrity: dict[str, Any] = field(default_factory=dict)
    source_import_requirements: tuple[str, ...] = field(default_factory=tuple)
    source_pattern_contract: dict[str, Any] = field(default_factory=dict)
    import_implications: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["axis_contracts"] = [axis.to_dict() for axis in self.axis_contracts]
        data["pricing"] = self.pricing.to_dict()
        data["media"] = self.media.to_dict()
        data["dependency_matrix"] = self.dependency_matrix.to_dict()
        data["checkout_eligibility"] = self.checkout_eligibility.to_dict()
        return data


@dataclass(frozen=True)
class ProductPatternResolution:
    item_code: str
    representative_item_code: str
    selected_options: dict[str, str]
    customization_payload: dict[str, Any]
    add_on_lines: tuple[dict[str, Any], ...]
    cart_line_key: str
    total_provenance: dict[str, Any]
    so_si_summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_product_pattern_contract(
    *,
    source_product: dict[str, Any] | None,
    erpnext_product: dict[str, Any],
) -> ProductPatternContract:
    """Build one architecture contract from source evidence plus ERPNext state."""

    source_product = source_product or {}
    slug = _clean(erpnext_product.get("item_code") or source_product.get("slug"))
    source_pattern = _source_pattern_contract(source_product)
    axis_contracts = _axis_contracts(source_product, erpnext_product)
    pricing = _pricing_provenance(source_product, erpnext_product)
    media = _media_contract(source_product, erpnext_product)
    dependency_matrix = _dependency_matrix(source_product, erpnext_product, axis_contracts)
    checkout = _checkout_eligibility(
        erpnext_product=erpnext_product,
        axes=axis_contracts,
        pricing=pricing,
        media=media,
        dependency_matrix=dependency_matrix,
    )
    return ProductPatternContract(
        slug=slug,
        source_name=_clean(source_product.get("name") or erpnext_product.get("web_item_name") or slug),
        route=_clean(erpnext_product.get("route")),
        item_code=slug,
        current_page_type=_clean(erpnext_product.get("lt_product_page_type")),
        current_commerce_lane=_clean(erpnext_product.get("lt_commerce_lane")),
        axis_contracts=axis_contracts,
        pricing=pricing,
        media=media,
        dependency_matrix=dependency_matrix,
        checkout_eligibility=checkout,
        cart_contract=_cart_contract(axis_contracts),
        order_preservation_contract=_order_preservation_contract(),
        source_patterns=tuple(str(pattern) for pattern in source_pattern.get("patterns") or ()),
        source_integrity=dict(source_pattern.get("source_integrity") or {}),
        source_import_requirements=tuple(
            str(requirement) for requirement in source_pattern.get("erpnext_contract_requirements") or ()
        ),
        source_pattern_contract=source_pattern,
        import_implications=_import_implications(axis_contracts, pricing, dependency_matrix, source_pattern),
        warnings=_warnings(source_product, erpnext_product, pricing, media, source_pattern),
    )


def resolve_product_pattern_selection(
    contract: ProductPatternContract,
    selected_config: dict[str, Any],
    *,
    item_resolver: Callable[[dict[str, str]], str | None] | None = None,
    price_resolver: Callable[[str], Decimal | str | float | int | None] | None = None,
    mode: ResolverMode = "checkout",
) -> ProductPatternResolution:
    """Validate a selected configuration against a contract.

    The optional callbacks let Frappe code plug in ERPNext's variant and Item
    Price lookups without making this pure contract module depend on Frappe.
    """

    if not isinstance(selected_config, dict):
        raise ProductPatternContractError("selected_config must be a dict")
    _enforce_resolver_mode(contract, mode)

    selected_options = _selected_options(contract, selected_config)
    customization_payload = _customization_payload(contract, selected_config)
    add_on_lines = _add_on_lines(contract, selected_config)
    item_code = ""
    if item_resolver:
        item_code = _clean(item_resolver(selected_options))
    if not item_code:
        item_code = contract.pricing.representative_item_code
    if not item_code:
        raise ProductPatternContractError("missing item_code: no exact or representative priced sale unit")

    price = price_resolver(item_code) if price_resolver else contract.pricing.representative_price
    if price in (None, ""):
        raise ProductPatternContractError(f"missing price for resolved item {item_code}")

    payload = {
        "schema_version": CART_CONFIGURATION_VERSION,
        "item_code": item_code,
        "website_item_code": contract.item_code,
        "selected_options": selected_options,
        "add_ons": list(add_on_lines),
        "customizations": customization_payload,
        "source": SCHEMA_VERSION,
    }
    add_on_total = sum(_decimal(line.get("amount")) or Decimal("0") for line in add_on_lines)
    base_price = _decimal(price) or Decimal("0")
    summary = _summary(contract, selected_options, customization_payload, add_on_lines)
    return ProductPatternResolution(
        item_code=item_code,
        representative_item_code=contract.pricing.representative_item_code,
        selected_options=selected_options,
        customization_payload=customization_payload,
        add_on_lines=tuple(add_on_lines),
        cart_line_key=_cart_line_key(item_code, payload),
        total_provenance={
            "base_item_price": _money(price),
            "add_on_total": _money(add_on_total),
            "grand_total": _money(base_price + add_on_total),
            "price_list": contract.pricing.price_list,
            "pricing_status": contract.pricing.status,
            "add_on_line_count": len(add_on_lines),
        },
        so_si_summary=summary,
    )


def _axis_contracts(source_product: dict[str, Any], erpnext_product: dict[str, Any]) -> tuple[AxisContract, ...]:
    contracts: dict[str, AxisContract] = {}
    source_axes = source_product.get("attributes") or {}
    erpnext_axes = erpnext_product.get("variant_axes") or {}

    for axis_name, axis in source_axes.items():
        values = _source_axis_values(axis)
        contracts[str(axis_name)] = _axis_contract_from_source(str(axis_name), values, axis, erpnext_product)

    for axis_name, values in erpnext_axes.items():
        clean_name = str(axis_name)
        existing = contracts.get(clean_name)
        value_tuple = tuple(_clean(value) for value in values or [] if _clean(value))
        if existing:
            merged = tuple(dict.fromkeys([*existing.values, *value_tuple]))
            contracts[clean_name] = AxisContract(
                name=existing.name,
                role=existing.role,
                values=merged,
                selector_type=existing.selector_type,
                source="combined",
                status=existing.status,
                pricing_required=existing.pricing_required,
                allows_multiple_values=existing.allows_multiple_values,
                add_on_key=existing.add_on_key,
                add_on_contract=existing.add_on_contract,
                review_reason=existing.review_reason,
                notes=existing.notes,
            )
        else:
            contracts[clean_name] = AxisContract(
                name=clean_name,
                role="sale_unit",
                values=value_tuple,
                selector_type="single_select",
                source="erpnext_variant",
                status="ready",
                pricing_required=True,
                notes=("ERPNext variant axis not found in source artifact.",),
            )

    return tuple(contracts[name] for name in sorted(contracts))


def _axis_contract_from_source(
    axis_name: str,
    values: tuple[str, ...],
    axis: dict[str, Any],
    erpnext_product: dict[str, Any],
) -> AxisContract:
    classification = classify_axis(axis_name)
    selector_type = _selector_type(axis_name, values, axis)
    add_on_contracts = known_add_on_contracts_for_axis(axis_name)
    notes: list[str] = []

    if classification.status == "optional_addon":
        add_on_contract = _add_on_contract(axis_name, add_on_contracts, erpnext_product)
        add_on_key = _clean(add_on_contract.get("key"))
        if not _add_on_contract_ready(add_on_contract):
            notes.append("Confirmed add-on is missing live ERPNext item/price validation.")
        return AxisContract(
            name=axis_name,
            role="add_on",
            values=values,
            selector_type="add_on_control",
            status="ready" if _add_on_contract_ready(add_on_contract) else "needs_mapping",
            pricing_required=True,
            add_on_key=add_on_key,
            add_on_contract=add_on_contract,
            notes=tuple([classification.note, *notes]),
        )

    if classification.status == "needs_review":
        return AxisContract(
            name=axis_name,
            role="review_only",
            values=values,
            selector_type="review_only",
            status="needs_review",
            pricing_required=False,
            review_reason=classification.note,
            notes=("Must fail loudly to quote/review until add-on pricing is mapped.",),
        )

    role: AxisRole = "sale_unit"
    allows_multiple = False
    if is_balloon_color_axis(axis_name):
        notes.append("Single selected color can be a priced sale-unit axis when variants/prices exist.")
        notes.append("Multi-color recipes need customization payload support instead of variant explosion.")
        allows_multiple = str(axis.get("display_type") or "").strip().lower() == "multi"

    if _looks_like_customization_axis(axis_name):
        role = "customization"
        allows_multiple = True

    return AxisContract(
        name=axis_name,
        role=role,
        values=values,
        selector_type=selector_type,
        source="odoo_source",
        status="ready" if role == "sale_unit" else "needs_mapping",
        pricing_required=role == "sale_unit",
        allows_multiple_values=allows_multiple,
        notes=tuple(notes),
    )


def _pricing_provenance(source_product: dict[str, Any], erpnext_product: dict[str, Any]) -> PricingProvenance:
    variant_count = int(erpnext_product.get("variant_count") or 0)
    priced_variant_count = int(erpnext_product.get("priced_variant_count") or 0)
    template_price_count = int(erpnext_product.get("template_price_count") or 0)
    expected = variant_count if variant_count else 1
    priced = priced_variant_count if variant_count else template_price_count
    source_price = _money_or_none(source_product.get("base_price"))
    price_min = _money_or_none(erpnext_product.get("price_min"))
    price_max = _money_or_none(erpnext_product.get("price_max"))
    representative_price = _money_or_none(erpnext_product.get("representative_price"))
    notes: list[str] = []

    status: PricingStatus = "ready"
    if priced <= 0:
        status = "missing"
        notes.append("No Standard Selling Item Price found for any sale unit.")
    elif priced < expected:
        status = "incomplete"
        notes.append("Some enabled ERPNext sale units do not have Standard Selling prices.")
    elif _prices_conflict(source_price, representative_price, price_min, price_max):
        status = "conflict_needs_fix"
        notes.append("ERPNext prices differ from source base price; require approved provenance before public checkout.")

    return PricingProvenance(
        status=status,
        source_base_price=source_price,
        erpnext_price_min=price_min,
        erpnext_price_max=price_max,
        expected_sale_units=expected,
        priced_sale_units=priced,
        missing_sale_units=max(expected - priced, 0),
        representative_item_code=_clean(erpnext_product.get("representative_item_code")),
        representative_price=representative_price,
        notes=tuple(notes),
    )


def _add_on_contract(
    axis_name: str,
    add_on_contracts: list[dict],
    erpnext_product: dict[str, Any],
) -> dict[str, Any]:
    contract = dict(add_on_contracts[0] if add_on_contracts else {})
    if not contract:
        return {}
    item_code = _clean(contract.get("item_code"))
    live_prices = erpnext_product.get("add_on_prices_by_item")
    live_price = None
    if isinstance(live_prices, dict):
        live_price = _money_or_none(live_prices.get(item_code))
    unit_price = _money_or_none(contract.get("unit_price"))
    price_status = "ready"
    notes: list[str] = []
    if not item_code:
        price_status = "missing_item_code"
        notes.append("Add-on contract is missing an ERPNext item_code.")
    elif isinstance(live_prices, dict) and live_price is None:
        price_status = "missing_live_item_price"
        notes.append(f"No live {STANDARD_PRICE_LIST} Item Price found for add-on item {item_code}.")
    elif live_price is not None and unit_price is not None and _decimal(live_price) != _decimal(unit_price):
        price_status = "price_conflict"
        notes.append(f"Live add-on price {live_price} differs from contract unit price {unit_price}.")
    return {
        **contract,
        "source_attribute": axis_name,
        "item_code": item_code,
        "unit_price": unit_price,
        "live_unit_price": live_price,
        "price_list": STANDARD_PRICE_LIST,
        "price_status": price_status,
        "ready_for_checkout": price_status == "ready",
        "quantity_min": int(contract.get("quantity_min") or 1),
        "quantity_max": int(contract.get("quantity_max") or 1),
        "requires_value": bool(contract.get("requires_value")),
        "receipt_label": _clean(contract.get("receipt_label") or contract.get("label")),
        "notes": tuple(notes),
    }


def _add_on_contract_ready(contract: dict[str, Any]) -> bool:
    return bool(
        contract
        and contract.get("key")
        and contract.get("item_code")
        and contract.get("unit_price") not in (None, "")
        and contract.get("ready_for_checkout") is not False
    )


def _media_contract(source_product: dict[str, Any], erpnext_product: dict[str, Any]) -> MediaRoleContract:
    primary = _clean(erpnext_product.get("website_image") or erpnext_product.get("item_image") or source_product.get("image_url"))
    variant_count = int(erpnext_product.get("variant_image_count") or 0)
    gallery_count = len(source_product.get("additional_image_urls") or [])
    roles: list[str] = []
    notes: list[str] = []
    if primary:
        roles.append("primary")
    if variant_count:
        roles.append("variant")
    if gallery_count:
        roles.append("gallery")
        notes.append("Extra source media must stay classified by role before automated import.")

    status: MediaStatus = "ready"
    uncertain_count = gallery_count
    if not primary:
        status = "primary_missing"
        notes.append("No primary image found in ERPNext or source artifact.")
    elif uncertain_count:
        status = "uncertain_roles"

    return MediaRoleContract(
        status=status,
        primary_image=primary,
        variant_image_count=variant_count,
        gallery_count=gallery_count,
        uncertain_count=uncertain_count,
        roles=tuple(roles or ["none"]),
        notes=tuple(notes),
    )


def _dependency_matrix(
    source_product: dict[str, Any],
    erpnext_product: dict[str, Any],
    axes: tuple[AxisContract, ...],
) -> DependencyMatrixContract:
    sale_axes = tuple(axis.name for axis in axes if axis.role == "sale_unit")
    if not sale_axes:
        return DependencyMatrixContract(status="not_required")

    source_rows = source_product.get("valid_variants") or []
    erpnext_axis_names = set((erpnext_product.get("variant_axes") or {}).keys())
    missing_backend_axes = sorted(axis for axis in sale_axes if axis not in erpnext_axis_names)
    erpnext_count = int(erpnext_product.get("variant_count") or 0)
    if missing_backend_axes and erpnext_count:
        return DependencyMatrixContract(
            status="mismatch",
            axes=sale_axes,
            erpnext_variant_count=erpnext_count,
            notes=(f"ERPNext variants are missing required sale-unit axes: {missing_backend_axes}",),
        )
    if not source_rows:
        return DependencyMatrixContract(
            status="missing_source_matrix",
            axes=sale_axes,
            erpnext_variant_count=erpnext_count,
            notes=("No source valid_variants rows available to prove option dependencies.",),
        )

    combinations = {
        tuple(sorted((axis, _clean(combo.get(axis))) for axis in sale_axes if _clean(combo.get(axis))))
        for combo in (_variant_combo(row) for row in source_rows)
    }
    combinations.discard(())
    source_count = len(combinations)
    if not erpnext_count and source_count:
        return DependencyMatrixContract(
            status="mismatch",
            axes=sale_axes,
            source_combination_count=source_count,
            erpnext_variant_count=erpnext_count,
            notes=("Source has sale-unit combinations but ERPNext has no enabled variants.",),
        )
    notes = []
    if erpnext_count and source_count and erpnext_count < source_count:
        notes.append(
            "ERPNext has fewer enabled variants than source combinations; treat as source-parity review, "
            "not resolver incapability when representative priced variants exist."
        )
    return DependencyMatrixContract(
        status="ready",
        axes=sale_axes,
        source_combination_count=source_count,
        erpnext_variant_count=erpnext_count,
        notes=tuple(notes),
    )


def _checkout_eligibility(
    *,
    erpnext_product: dict[str, Any],
    axes: tuple[AxisContract, ...],
    pricing: PricingProvenance,
    media: MediaRoleContract,
    dependency_matrix: DependencyMatrixContract,
) -> CheckoutEligibility:
    fail_loud: list[FailLoudState] = []
    required_work: list[str] = []

    if pricing.status in {"missing", "incomplete", "conflict_needs_fix"}:
        fail_loud.append("missing_price")
        required_work.append("Provide one approved Standard Selling price for every enabled sale unit.")

    review_axes = [axis.name for axis in axes if axis.role == "review_only"]
    unmapped_addons = [axis.name for axis in axes if axis.role == "add_on" and axis.status != "ready"]
    if review_axes:
        fail_loud.append("review_only_add_on")
        required_work.append("Keep review-only add-on axes in quote/review payloads until mapping is approved.")
    if unmapped_addons:
        fail_loud.append("unpriced_add_on")
        required_work.append("Map confirmed add-ons to priced ERPNext add-on Items with quantity/value validation.")

    customization_axes = [axis.name for axis in axes if axis.role == "customization"]
    if customization_axes:
        fail_loud.append("unsupported_customization_payload")
        required_work.append("Add validated customization payload schema and SO/SI/receipt summaries.")

    if media.status == "primary_missing":
        fail_loud.append("media_uncertainty")
        required_work.append("Attach a primary image or explicitly mark the product as image-not-required.")

    if dependency_matrix.status in {"missing_source_matrix", "mismatch"}:
        fail_loud.append("dependency_mismatch")
        required_work.append("Import or generate a source-backed dependency matrix for sale-unit options.")

    if "missing_price" in fail_loud:
        status: CheckoutStatus = "needs_pricing"
    elif "review_only_add_on" in fail_loud or "unpriced_add_on" in fail_loud:
        status = "needs_add_on_pricing"
    elif "unsupported_customization_payload" in fail_loud:
        status = "needs_customization_payload"
    elif "dependency_mismatch" in fail_loud:
        status = "dependency_mismatch"
    elif "media_uncertainty" in fail_loud:
        status = "needs_media_review"
    elif _clean(erpnext_product.get("lt_commerce_lane")) == "checkout":
        status = "checkout_ready"
    else:
        status = "lane_mapping_only"
        required_work.append("Change Website Item buying path/page template once owner approves direct checkout.")

    return CheckoutEligibility(
        status=status,
        current_page_type=_clean(erpnext_product.get("lt_product_page_type")),
        current_commerce_lane=_clean(erpnext_product.get("lt_commerce_lane")),
        fail_loud_states=tuple(dict.fromkeys(fail_loud)),
        required_work=tuple(dict.fromkeys(required_work)),
    )


def _selected_options(contract: ProductPatternContract, selected_config: dict[str, Any]) -> dict[str, str]:
    selected = selected_config.get("selected_options") or {}
    if not isinstance(selected, dict):
        raise ProductPatternContractError("selected_options must be a dict")

    result: dict[str, str] = {}
    for axis in contract.axis_contracts:
        if axis.role != "sale_unit":
            continue
        value = selected.get(axis.name)
        if isinstance(value, list):
            raise ProductPatternContractError(
                f"{axis.name} received multiple values; use customization payload for recipes"
            )
        clean_value = _clean(value)
        if not clean_value:
            raise ProductPatternContractError(f"missing required sale-unit axis: {axis.name}")
        if axis.values and clean_value not in axis.values:
            raise ProductPatternContractError(f"invalid value for {axis.name}: {clean_value}")
        result[axis.name] = clean_value
    return result


def _customization_payload(contract: ProductPatternContract, selected_config: dict[str, Any]) -> dict[str, Any]:
    customizations = selected_config.get("customizations") or {}
    if isinstance(customizations, list):
        customizations = {"items": customizations}
    if not isinstance(customizations, dict):
        raise ProductPatternContractError("customizations must be a dict or list")
    if customizations and not any(axis.role == "customization" for axis in contract.axis_contracts):
        raise ProductPatternContractError("customization payload provided for a product without customization axes")
    if customizations and "unsupported_customization_payload" in contract.checkout_eligibility.fail_loud_states:
        raise ProductPatternContractError("customization payload is not connected to paid checkout yet")
    return customizations


def _enforce_resolver_mode(contract: ProductPatternContract, mode: ResolverMode) -> None:
    if mode not in {"checkout", "quote", "report"}:
        raise ProductPatternContractError(f"unknown resolver mode: {mode}")
    if mode != "checkout":
        return
    if contract.checkout_eligibility.status != "checkout_ready":
        raise ProductPatternContractError(
            f"contract is not checkout-ready: {contract.checkout_eligibility.status}"
        )
    if contract.checkout_eligibility.fail_loud_states:
        states = ", ".join(contract.checkout_eligibility.fail_loud_states)
        raise ProductPatternContractError(f"contract has fail-loud states: {states}")


def _add_on_lines(contract: ProductPatternContract, selected_config: dict[str, Any]) -> list[dict[str, Any]]:
    add_ons = selected_config.get("add_ons") or []
    if not isinstance(add_ons, list):
        raise ProductPatternContractError("add_ons must be a list")
    allowed = {
        axis.add_on_key: axis
        for axis in contract.axis_contracts
        if axis.role == "add_on" and axis.add_on_key
    }
    review_only = {axis.name for axis in contract.axis_contracts if axis.role == "review_only"}
    result = []
    for row in add_ons:
        if not isinstance(row, dict):
            raise ProductPatternContractError("add_on rows must be dicts")
        key = _clean(row.get("key"))
        if key not in allowed:
            if review_only:
                raise ProductPatternContractError(f"review-only add-on axis cannot checkout yet: {sorted(review_only)}")
            raise ProductPatternContractError(f"unknown add-on key for product contract: {key}")
        axis = allowed[key]
        contract_row = axis.add_on_contract
        if not _add_on_contract_ready(contract_row):
            raise ProductPatternContractError(f"add-on is not priced for checkout: {axis.name}")
        quantity = _add_on_quantity(row, contract_row)
        selected_value = _clean(row.get("value") or row.get("selected_value"))
        if contract_row.get("requires_value") and not selected_value:
            raise ProductPatternContractError(f"add-on {axis.name} requires a selected value")
        if selected_value and axis.values and selected_value not in axis.values:
            raise ProductPatternContractError(f"invalid add-on value for {axis.name}: {selected_value}")
        unit_price = _decimal(contract_row.get("live_unit_price") or contract_row.get("unit_price"))
        if unit_price is None:
            raise ProductPatternContractError(f"add-on {axis.name} missing unit price")
        amount = unit_price * Decimal(quantity)
        result.append(
            {
                "key": key,
                "source_axis": axis.name,
                "item_code": contract_row["item_code"],
                "label": _clean(contract_row.get("label")),
                "receipt_label": _clean(contract_row.get("receipt_label") or contract_row.get("label")),
                "selected_value": selected_value,
                "quantity": quantity,
                "unit_price": _money(unit_price),
                "amount": _money(amount),
                "price_list": contract_row.get("price_list") or STANDARD_PRICE_LIST,
                "summary": _add_on_summary(contract_row, selected_value, quantity, amount),
            }
        )
    return result


def _add_on_quantity(row: dict[str, Any], contract_row: dict[str, Any]) -> int:
    raw = row.get("quantity", row.get("qty", 1))
    try:
        quantity = int(raw)
    except (TypeError, ValueError):
        raise ProductPatternContractError(f"invalid add-on quantity: {raw}") from None
    minimum = int(contract_row.get("quantity_min") or 1)
    maximum = int(contract_row.get("quantity_max") or minimum)
    if quantity < minimum or quantity > maximum:
        raise ProductPatternContractError(
            f"add-on quantity {quantity} outside allowed range {minimum}-{maximum}"
        )
    return quantity


def _add_on_summary(
    contract_row: dict[str, Any],
    selected_value: str,
    quantity: int,
    amount: Decimal,
) -> str:
    label = _clean(contract_row.get("receipt_label") or contract_row.get("label") or contract_row.get("key"))
    pieces = [label]
    if selected_value:
        pieces.append(selected_value)
    pieces.append(f"qty {quantity}")
    pieces.append(f"${_money(amount)}")
    return " - ".join(pieces)


def _cart_contract(axes: tuple[AxisContract, ...]) -> dict[str, Any]:
    return {
        "schema_version": CART_CONFIGURATION_VERSION,
        "required_keys": ("item_code", "website_item_code", "selected_options", "add_ons", "customizations"),
        "sale_unit_axes": [axis.name for axis in axes if axis.role == "sale_unit"],
        "customization_axes": [axis.name for axis in axes if axis.role == "customization"],
        "add_on_axes": [axis.name for axis in axes if axis.role == "add_on"],
        "add_on_contracts": [
            axis.add_on_contract for axis in axes if axis.role == "add_on" and axis.add_on_contract
        ],
        "review_only_axes": [axis.name for axis in axes if axis.role == "review_only"],
    }


def _order_preservation_contract() -> dict[str, Any]:
    return {
        "line_fields": LINE_CONFIGURATION_FIELDS,
        "summary_required": True,
        "json_required": True,
        "receipt_label_source": "custom_lt_configuration_summary/custom_lt_configuration_json",
        "add_on_line_detail_required": True,
        "add_on_line_fields": ("item_code", "qty", "rate", "amount", "description"),
    }


def _import_implications(
    axes: tuple[AxisContract, ...],
    pricing: PricingProvenance,
    dependency_matrix: DependencyMatrixContract,
    source_pattern: dict[str, Any],
) -> tuple[str, ...]:
    implications: list[str] = []
    implications.extend(str(value) for value in source_pattern.get("import_implications") or ())
    if any(axis.role == "sale_unit" for axis in axes):
        implications.append("Create/import only enabled sale-unit Items that resolve from required axes.")
    if any(axis.role == "customization" for axis in axes):
        implications.append("Do not create combinatorial variants for freeform/customization payloads.")
    if any(axis.role == "add_on" for axis in axes):
        implications.append("Create add-ons as separate priced Items and Sales Order add-on lines.")
    if any(axis.role == "review_only" for axis in axes):
        implications.append("Keep review-only axes out of paid checkout until mapping is approved.")
    if pricing.status != "ready":
        implications.append("Hold checkout until Standard Selling price provenance is complete.")
    if dependency_matrix.status in {"missing_source_matrix", "mismatch"}:
        implications.append("Regenerate source-backed dependency matrix before enabling direct checkout.")
    return tuple(implications or ("Single SKU checkout can use Website Item, Item, and Item Price directly.",))


def _warnings(
    source_product: dict[str, Any],
    erpnext_product: dict[str, Any],
    pricing: PricingProvenance,
    media: MediaRoleContract,
    source_pattern: dict[str, Any],
) -> tuple[str, ...]:
    warnings: list[str] = []
    if source_product and _clean(source_product.get("slug")) != _clean(erpnext_product.get("item_code")):
        warnings.append("Source slug and ERPNext item_code differ.")
    if pricing.status != "ready":
        warnings.extend(pricing.notes)
    if media.status != "ready":
        warnings.extend(media.notes)
    if source_product and not source_pattern:
        warnings.append("Source product could not be classified by Odoo option-pattern mapper.")
    return tuple(dict.fromkeys(warnings))


def _source_pattern_contract(source_product: dict[str, Any]) -> dict[str, Any]:
    if not source_product:
        return {}
    return build_source_pattern_contract(source_product).to_dict()


def _source_axis_values(axis: Any) -> tuple[str, ...]:
    if not isinstance(axis, dict):
        return ()
    values = []
    for value in axis.get("values") or []:
        if isinstance(value, dict):
            clean = _clean(value.get("name"))
            if clean:
                values.append(clean)
    return tuple(dict.fromkeys(values))


def _selector_type(axis_name: str, values: tuple[str, ...], axis: dict[str, Any]) -> str:
    if is_balloon_color_axis(axis_name):
        return "color_drawer"
    if len(values) <= 4:
        return "radio"
    if str(axis.get("display_type") or "").strip().lower() == "multi":
        return "multi_select_drawer"
    return "single_select"


def _looks_like_customization_axis(axis_name: str) -> bool:
    key = _key(axis_name)
    return any(token in key for token in ("custom text", "logo upload", "message text", "customer note"))


def _variant_combo(row: Any) -> dict[str, str]:
    if not isinstance(row, dict):
        return {}
    combo = row.get("combo") or row.get("attribute_values") or {}
    if not isinstance(combo, dict):
        return {}
    return {str(key): _clean(value) for key, value in combo.items()}


def _prices_conflict(
    source_price: str | None,
    representative_price: str | None,
    price_min: str | None,
    price_max: str | None,
) -> bool:
    if not source_price or not representative_price:
        return False
    if price_min and price_max and price_min != price_max:
        return False
    return _decimal(source_price) != _decimal(representative_price)


def _summary(
    contract: ProductPatternContract,
    selected_options: dict[str, str],
    customizations: dict[str, Any],
    add_ons: list[dict[str, Any]],
) -> str:
    pieces = [f"Product - {contract.source_name or contract.slug}"]
    if selected_options:
        pieces.append(
            "Options - " + ", ".join(f"{key}: {value}" for key, value in sorted(selected_options.items()))
        )
    if customizations:
        pieces.append("Customizations preserved in structured payload")
    if add_ons:
        pieces.append(
            "Add-ons - " + ", ".join(_clean(row.get("summary")) for row in add_ons if row.get("summary"))
        )
    return "; ".join(pieces)


def _cart_line_key(item_code: str, payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]
    return f"{item_code}::{digest}"


def _money_or_none(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return _money(value)


def _money(value: Any) -> str:
    decimal = _decimal(value)
    if decimal is None:
        return str(value)
    return str(decimal.quantize(Decimal("0.01")))


def _decimal(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _key(value: Any) -> str:
    return " ".join(str(value or "").replace("-", " ").replace("_", " ").strip().lower().split())


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())
