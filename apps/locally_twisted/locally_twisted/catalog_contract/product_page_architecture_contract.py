"""Generic product-page receiving architecture contract.

This module is the backend-owned boundary between product/source semantics and
customer-facing product controls. It is intentionally pure: ERPNext/Frappe code
may feed it live rows, but the rules here do not query or mutate the database.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from locally_twisted.catalog_contract.color_rules import is_balloon_color_axis
from locally_twisted.catalog_contract.product_pattern_contract import (
    CART_CONFIGURATION_VERSION,
    LINE_CONFIGURATION_FIELDS,
    SCHEMA_VERSION as PRODUCT_PATTERN_SCHEMA_VERSION,
)


SCHEMA_VERSION = "lt-product-page-architecture-contract-v1"

CLIENT_PAYLOAD_KEYS = (
    "schema_version",
    "item_code",
    "website_item_code",
    "selected_options",
    "color_recipes",
    "add_ons",
    "customizations",
)
SERVER_DERIVED_KEYS = (
    "resolved_item_code",
    "price_provenance",
    "readable_summary",
    "canonical_cart_line_key",
)
LINE_FIELD_DOCTYPES = ("Quotation Item", "Sales Order Item", "Sales Invoice Item")


@dataclass(frozen=True)
class ProductPageControlContract:
    control_id: str
    axis_name: str
    role: str
    selector_type: str
    payload_target: str
    required_for_checkout: bool
    server_validated: bool
    checkout_blocking: bool
    allows_multiple_values: bool = False
    values: tuple[str, ...] = field(default_factory=tuple)
    value_count: int = 0
    source: str = ""
    server_validation: str = ""
    failure_mode: str = ""
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProductPagePayloadContract:
    schema_version: str
    client_payload_keys: tuple[str, ...]
    server_derived_keys: tuple[str, ...]
    required_for_checkout: tuple[str, ...]
    quote_first_payload_keys: tuple[str, ...]
    target_by_role: dict[str, str]
    browser_may_price: bool = False
    browser_may_resolve_checkout_eligibility: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProductPageDocumentParityContract:
    line_fields: dict[str, tuple[str, ...]]
    summary_required: bool
    json_required: bool
    receipt_label_source: str
    operator_review_source: str
    add_on_line_detail_required: bool
    color_recipe_detail_required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProductPageArchitectureContract:
    schema_version: str
    source_contract_schema: str
    item_code: str
    source_name: str
    route: str
    product_page_type: str
    commerce_lane: str
    checkout_allowed: bool
    quote_first_allowed: bool
    controls: tuple[ProductPageControlContract, ...]
    payload_contract: ProductPagePayloadContract
    document_parity: ProductPageDocumentParityContract
    fail_loud_states: tuple[str, ...] = field(default_factory=tuple)
    required_work: tuple[str, ...] = field(default_factory=tuple)
    architecture_boundaries: tuple[str, ...] = field(default_factory=tuple)
    architecture_failures: tuple[str, ...] = field(default_factory=tuple)
    product_specific_rules_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["controls"] = [control.to_dict() for control in self.controls]
        data["payload_contract"] = self.payload_contract.to_dict()
        data["document_parity"] = self.document_parity.to_dict()
        return data


def build_product_page_architecture_contract(
    product_contract: Mapping[str, Any] | Any,
) -> ProductPageArchitectureContract:
    """Build the generic product-page receiving contract for one product row."""

    row = _to_mapping(product_contract)
    checkout = _to_mapping(row.get("checkout_eligibility"))
    fail_loud_states = tuple(_clean(value) for value in checkout.get("fail_loud_states") or () if _clean(value))
    checkout_status = _clean(checkout.get("status"))
    commerce_lane = _clean(row.get("current_commerce_lane") or checkout.get("current_commerce_lane"))
    checkout_allowed = commerce_lane == "checkout" and checkout_status == "checkout_ready" and not fail_loud_states
    quote_first_allowed = commerce_lane == "quote_first" or not checkout_allowed
    axes = tuple(_to_mapping(axis) for axis in row.get("axis_contracts") or ())
    controls = tuple(_control_contract(axis, checkout_allowed=checkout_allowed) for axis in axes)
    payload_contract = _payload_contract(controls)
    document_parity = _document_parity_contract(row)
    architecture_failures = tuple(
        validate_product_page_architecture_contract(
            {
                "schema_version": SCHEMA_VERSION,
                "source_contract_schema": _clean(row.get("schema_version") or PRODUCT_PATTERN_SCHEMA_VERSION),
                "item_code": _clean(row.get("item_code") or row.get("slug")),
                "source_name": _clean(row.get("source_name")),
                "route": _clean(row.get("route")),
                "product_page_type": _clean(row.get("current_page_type")),
                "commerce_lane": commerce_lane,
                "checkout_allowed": checkout_allowed,
                "quote_first_allowed": quote_first_allowed,
                "controls": [control.to_dict() for control in controls],
                "payload_contract": payload_contract.to_dict(),
                "document_parity": document_parity.to_dict(),
                "fail_loud_states": fail_loud_states,
                "required_work": tuple(_clean(value) for value in checkout.get("required_work") or () if _clean(value)),
                "product_specific_rules_allowed": False,
            }
        )
    )

    return ProductPageArchitectureContract(
        schema_version=SCHEMA_VERSION,
        source_contract_schema=_clean(row.get("schema_version") or PRODUCT_PATTERN_SCHEMA_VERSION),
        item_code=_clean(row.get("item_code") or row.get("slug")),
        source_name=_clean(row.get("source_name")),
        route=_clean(row.get("route")),
        product_page_type=_clean(row.get("current_page_type")),
        commerce_lane=commerce_lane,
        checkout_allowed=checkout_allowed,
        quote_first_allowed=quote_first_allowed,
        controls=controls,
        payload_contract=payload_contract,
        document_parity=document_parity,
        fail_loud_states=fail_loud_states,
        required_work=tuple(_clean(value) for value in checkout.get("required_work") or () if _clean(value)),
        architecture_boundaries=_architecture_boundaries(),
        architecture_failures=architecture_failures,
        product_specific_rules_allowed=False,
    )


def build_product_page_architecture_report(
    product_contracts: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
    *,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build and validate the architecture contract for many product rows."""

    contracts = [build_product_page_architecture_contract(row) for row in product_contracts]
    product_rows = [contract.to_dict() for contract in contracts]
    failures = [
        f"{contract.item_code}: {failure}"
        for contract in contracts
        for failure in contract.architecture_failures
    ]
    control_target_counts = Counter(
        control.payload_target for contract in contracts for control in contract.controls
    )
    control_role_counts = Counter(control.role for contract in contracts for control in contract.controls)
    lane_counts = Counter(contract.commerce_lane or "unset" for contract in contracts)
    checkout_allowed_count = sum(1 for contract in contracts if contract.checkout_allowed)
    quote_first_allowed_count = sum(1 for contract in contracts if contract.quote_first_allowed)
    return {
        "ok": not failures,
        "schema_version": SCHEMA_VERSION,
        "source_contract_schema": PRODUCT_PATTERN_SCHEMA_VERSION,
        "read_only": True,
        "destructive_allowed": False,
        "metadata": dict(metadata or {}),
        "purpose": (
            "Backend-driven product-page receiving architecture: axis semantics to "
            "controls, versioned payload, cart/checkout resolver boundary, and "
            "ERPNext document parity."
        ),
        "summary": {
            "product_count": len(contracts),
            "checkout_allowed_products": checkout_allowed_count,
            "quote_first_allowed_products": quote_first_allowed_count,
            "commerce_lane_counts": dict(sorted(lane_counts.items())),
            "control_role_counts": dict(sorted(control_role_counts.items())),
            "payload_target_counts": dict(sorted(control_target_counts.items())),
            "architecture_failure_count": len(failures),
            "product_specific_rules_allowed": False,
        },
        "architecture_boundaries": _architecture_boundaries(),
        "failures": failures,
        "products": product_rows,
    }


def validate_product_page_architecture_contract(contract: Mapping[str, Any]) -> list[str]:
    """Return structural failures for one architecture contract."""

    failures: list[str] = []
    payload = _to_mapping(contract.get("payload_contract"))
    document = _to_mapping(contract.get("document_parity"))
    controls = [_to_mapping(control) for control in contract.get("controls") or ()]
    client_keys = tuple(payload.get("client_payload_keys") or ())
    server_keys = tuple(payload.get("server_derived_keys") or ())

    for key in CLIENT_PAYLOAD_KEYS:
        if key not in client_keys:
            failures.append(f"payload contract missing client key {key}")
    for key in SERVER_DERIVED_KEYS:
        if key not in server_keys:
            failures.append(f"payload contract missing server-derived key {key}")

    line_fields = _to_mapping(document.get("line_fields"))
    required_line_fields = set(LINE_CONFIGURATION_FIELDS["Sales Order Item"])
    for doctype in LINE_FIELD_DOCTYPES:
        fields = set(line_fields.get(doctype) or ())
        missing = sorted(required_line_fields - fields)
        if missing:
            failures.append(f"{doctype} missing architecture line fields {missing}")

    if not document.get("summary_required"):
        failures.append("document parity must require a human-readable summary")
    if not document.get("json_required"):
        failures.append("document parity must require machine-readable JSON")

    for control in controls:
        axis_name = _clean(control.get("axis_name"))
        role = _clean(control.get("role"))
        payload_target = _clean(control.get("payload_target"))
        if not axis_name:
            failures.append("control missing axis_name")
        if not role:
            failures.append(f"{axis_name or 'unnamed control'} missing role")
        if not payload_target:
            failures.append(f"{axis_name or 'unnamed control'} missing payload_target")
        if role == "sale_unit" and payload_target != "selected_options":
            failures.append(f"{axis_name} sale-unit control must target selected_options")
        if role == "customization" and is_balloon_color_axis(axis_name) and payload_target != "color_recipes":
            failures.append(f"{axis_name} color customization must target color_recipes, not {payload_target}")
        if role == "customization" and is_balloon_color_axis(axis_name) and "color_recipes" not in client_keys:
            failures.append(f"{axis_name} color customization has no color_recipes payload key")
        if role == "add_on" and payload_target not in {"add_ons", "quote_context"}:
            failures.append(f"{axis_name} add-on control has invalid payload target {payload_target}")
        if control.get("required_for_checkout") and not control.get("server_validated"):
            failures.append(f"{axis_name} required checkout control is not server validated")

    if contract.get("checkout_allowed"):
        if contract.get("fail_loud_states"):
            failures.append("checkout_allowed cannot be true while fail_loud_states exist")
        if _clean(contract.get("commerce_lane")) != "checkout":
            failures.append("checkout_allowed requires commerce_lane=checkout")
        blocking_controls = [
            _clean(control.get("axis_name"))
            for control in controls
            if control.get("checkout_blocking")
        ]
        if blocking_controls:
            failures.append(f"checkout_allowed has blocking controls {blocking_controls}")

    if contract.get("product_specific_rules_allowed") is not False:
        failures.append("architecture contract must not allow product-specific rules")
    return failures


def _control_contract(axis: Mapping[str, Any], *, checkout_allowed: bool) -> ProductPageControlContract:
    axis_name = _clean(axis.get("name"))
    role = _clean(axis.get("role")) or "sale_unit"
    selector_type = _clean(axis.get("selector_type")) or "single_select"
    values = tuple(_clean(value) for value in axis.get("values") or () if _clean(value))
    notes = tuple(_clean(value) for value in axis.get("notes") or () if _clean(value))
    if role == "sale_unit":
        payload_target = "selected_options"
        required_for_checkout = True
        checkout_blocking = False
        server_validation = "Resolve sale-unit selected_options to an ERPNext item_code or representative priced item."
        failure_mode = "unknown or impossible sale-unit selection blocks cart/checkout"
    elif role == "customization" and is_balloon_color_axis(axis_name):
        payload_target = "color_recipes"
        selector_type = "multi_color_recipe_builder"
        required_for_checkout = checkout_allowed
        checkout_blocking = False
        server_validation = "Reject color axes in selected_options; require non-empty color_recipes for checkout."
        failure_mode = "missing or malformed color recipe routes to quote/fails checkout loudly"
    elif role == "customization":
        payload_target = "customizations"
        required_for_checkout = False
        checkout_blocking = False
        server_validation = "Hide unsupported customization controls until a checkout validator exists; reject submitted payloads server-side."
        failure_mode = "unsupported customization payload is rejected, but the base product remains purchasable"
    elif role == "add_on":
        add_on_contract = _to_mapping(axis.get("add_on_contract"))
        ready = _add_on_contract_ready(add_on_contract)
        payload_target = "add_ons" if ready else "quote_context"
        required_for_checkout = ready and checkout_allowed
        checkout_blocking = False
        selector_type = _clean(add_on_contract.get("input_type") or selector_type or "add_on_selector")
        server_validation = (
            "Validate add-on eligibility, quantity/value, ERPNext Item Price, and separate order/invoice line."
            if ready
            else "Hide add-on control until an approved priced add-on Item contract exists."
        )
        failure_mode = "unapproved or unpriced add-on payload is rejected, but the base product remains purchasable"
    elif role == "review_only":
        payload_target = "quote_context"
        selector_type = "review_notice"
        required_for_checkout = False
        checkout_blocking = False
        server_validation = "Hide review-only source controls from paid checkout until mapped and approved."
        failure_mode = "review-only source axis cannot become a free checkout option"
    else:
        payload_target = "quote_context"
        required_for_checkout = False
        checkout_blocking = checkout_allowed
        server_validation = "Unknown axis role routes to quote/review until mapped."
        failure_mode = "unknown axis role blocks paid checkout"

    return ProductPageControlContract(
        control_id=_control_id(axis_name),
        axis_name=axis_name,
        role=role,
        selector_type=selector_type,
        payload_target=payload_target,
        required_for_checkout=required_for_checkout,
        server_validated=True,
        checkout_blocking=checkout_blocking,
        allows_multiple_values=bool(axis.get("allows_multiple_values")) or payload_target == "color_recipes",
        values=values,
        value_count=len(values),
        source=_clean(axis.get("source")),
        server_validation=server_validation,
        failure_mode=failure_mode,
        notes=notes,
    )


def _payload_contract(controls: tuple[ProductPageControlContract, ...]) -> ProductPagePayloadContract:
    required_for_checkout = [
        "schema_version",
        "item_code",
        "website_item_code",
        "selected_options",
        "add_ons",
        "customizations",
    ]
    if any(control.payload_target == "color_recipes" for control in controls):
        required_for_checkout.append("color_recipes")
    return ProductPagePayloadContract(
        schema_version=CART_CONFIGURATION_VERSION,
        client_payload_keys=CLIENT_PAYLOAD_KEYS,
        server_derived_keys=SERVER_DERIVED_KEYS,
        required_for_checkout=tuple(dict.fromkeys(required_for_checkout)),
        quote_first_payload_keys=(
            "schema_version",
            "website_item_code",
            "product_page_type",
            "commerce_lane",
            "selected_options",
            "color_recipes",
            "add_ons",
            "customizations",
        ),
        target_by_role={
            "sale_unit": "selected_options",
            "customization_color": "color_recipes",
            "customization_other": "customizations",
            "add_on": "add_ons",
            "review_only": "quote_context",
        },
    )


def _document_parity_contract(row: Mapping[str, Any]) -> ProductPageDocumentParityContract:
    preservation = _to_mapping(row.get("order_preservation_contract"))
    line_fields = preservation.get("line_fields") or LINE_CONFIGURATION_FIELDS
    clean_line_fields = {
        doctype: tuple(fields or ())
        for doctype, fields in _to_mapping(line_fields).items()
        if doctype in LINE_FIELD_DOCTYPES
    }
    for doctype in LINE_FIELD_DOCTYPES:
        clean_line_fields.setdefault(doctype, tuple(LINE_CONFIGURATION_FIELDS[doctype]))
    return ProductPageDocumentParityContract(
        line_fields=clean_line_fields,
        summary_required=bool(preservation.get("summary_required", True)),
        json_required=bool(preservation.get("json_required", True)),
        receipt_label_source=_clean(
            preservation.get("receipt_label_source")
            or "custom_lt_configuration_summary/custom_lt_configuration_json"
        ),
        operator_review_source="Quotation/Sales Order/Sales Invoice line JSON plus human summary",
        add_on_line_detail_required=bool(preservation.get("add_on_line_detail_required", True)),
        color_recipe_detail_required=bool(preservation.get("color_recipe_detail_required", True)),
    )


def _architecture_boundaries() -> tuple[str, ...]:
    return (
        "Source/ProductPatternContract owns axis role, add-on status, pricing provenance, media status, and fail-loud blockers.",
        "Product page renders controls from backend architecture, not product-name branches or frontend-only eligibility.",
        "Browser submits lt-product-config-v1 with selected_options, color_recipes, add_ons, and customizations.",
        "Server resolves item_code, add-on lines, price provenance, readable summary, and canonical cart-line key.",
        "Quotation Item, Sales Order Item, and Sales Invoice Item carry the same LT configuration fields.",
        "Quote-first preserves customer intent through Lead and draft Quotation without creating payment, invoice, or false success.",
    )


def _add_on_contract_ready(contract: Mapping[str, Any]) -> bool:
    return bool(
        contract.get("ready_for_checkout")
        and contract.get("item_code")
        and contract.get("price_status") == "ready"
        and contract.get("live_unit_price") not in (None, "")
        and contract.get("quantity_min") not in (None, "")
        and contract.get("quantity_max") not in (None, "")
        and contract.get("receipt_label")
    )


def _control_id(axis_name: str) -> str:
    clean = "".join(char.lower() if char.isalnum() else "-" for char in axis_name)
    return "lt-control-" + "-".join(part for part in clean.split("-") if part)


def _to_mapping(value: Mapping[str, Any] | Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return dict(to_dict())
    return {}


def _clean(value: Any) -> str:
    return str(value or "").strip()
