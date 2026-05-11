"""Reusable Odoo option-pattern mapper for product imports.

This module is pure reporting code. It reads saved source product rows and
describes the ERPNext primitives needed to preserve their option meaning before
any import runner creates or mutates records.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any, Literal

from locally_twisted.catalog_contract.addon_rules import CONFIRMED_ADD_ONS, REVIEW_ADD_ONS
from locally_twisted.catalog_contract.color_rules import is_balloon_color_axis


AxisPattern = Literal[
    "required_sale_unit_axis",
    "large_single_choice_color",
    "multi_color_recipe_customization",
    "add_on_axis",
    "conditional_pricing_candidate",
    "freeform_customer_text_candidate",
    "review_only_axis",
]

SCHEMA_VERSION = "lt-odoo-option-pattern-contract-v1"
LARGE_COLOR_VALUE_THRESHOLD = 12
FINITE_AXIS_VALUE_LIMIT = 12

CONDITIONAL_PRICE_AXIS_TOKENS = (
    "size",
    "height",
    "length",
    "drop",
    "ft",
    "foot",
    "feet",
    "tier",
)

FREEFORM_TEXT_TOKENS = (
    "custom",
    "logo",
    "message",
    "name",
    "school",
    "team",
    "theme",
    "text",
    "word",
    "upload",
)

DESIGN_RECIPE_AXIS_TOKENS = (
    "color palette",
    "latex colors",
    "number colors",
    "baby color",
    "design",
)


@dataclass(frozen=True)
class AxisPatternContract:
    name: str
    source_value_count: int
    patterns: tuple[AxisPattern, ...]
    source_values: tuple[str, ...]
    source_value_hash: str
    primitive_key: str
    erpnext_primitive: str
    selector_key: str
    import_implication: str
    selector_requirement: str
    pricing_strategy: str
    review_reason: str = ""
    sample_values: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MediaRoleRequirement:
    primary_image_url: str
    extra_image_count: int
    source_variant_rows: int
    requirements: tuple[str, ...]
    safe_default: str = "hold_extra_images_until_classified"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProductPatternContract:
    slug: str
    odoo_product_id: str
    source_name: str
    source_url: str
    currency: str
    source_variant_rows: int
    source_declared_variant_count: int | None
    base_price: str | None
    patterns: tuple[str, ...]
    axis_contracts: tuple[AxisPatternContract, ...]
    media_roles: MediaRoleRequirement
    sale_unit_contract: dict[str, Any]
    pricing: dict[str, Any]
    source_integrity: dict[str, Any]
    erpnext_contract_requirements: tuple[str, ...]
    import_implications: tuple[str, ...]
    example_label: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["axis_contracts"] = [axis.to_dict() for axis in self.axis_contracts]
        data["media_roles"] = self.media_roles.to_dict()
        return data


@dataclass(frozen=True)
class ProductPatternReport:
    products: tuple[ProductPatternContract, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        pattern_counts: Counter[str] = Counter()
        axis_pattern_counts: Counter[str] = Counter()
        media_requirement_counts: Counter[str] = Counter()
        for product in self.products:
            pattern_counts.update(product.patterns)
            for axis in product.axis_contracts:
                axis_pattern_counts.update(axis.patterns)
            media_requirement_counts.update(product.media_roles.requirements)
        return {
            "schema_version": SCHEMA_VERSION,
            "source_products": len(self.products),
            "pattern_counts": dict(sorted(pattern_counts.items())),
            "axis_pattern_counts": dict(sorted(axis_pattern_counts.items())),
            "media_requirement_counts": dict(sorted(media_requirement_counts.items())),
            "source_variant_rows": sum(product.source_variant_rows for product in self.products),
            "source_extra_images": sum(product.media_roles.extra_image_count for product in self.products),
        }

    def to_artifact(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "metadata": self.metadata,
            "read_only": True,
            "destructive_allowed": False,
            "purpose": "Reusable Odoo option-pattern classification feeding ERPNext ProductPatternContract imports.",
            "summary": self.summary(),
            "products": [product.to_dict() for product in self.products],
        }

    def to_markdown(self) -> str:
        summary = self.summary()
        lines = [
            "# Odoo Option Pattern Mapper",
            "",
            "This is a read-only source classifier. It does not import, purge, delete, or mutate ERPNext.",
            "Product names are examples only; classification is driven by source axes, prices, descriptions, and media shape.",
            "",
            "## Summary",
            "",
            f"- Source products: {summary['source_products']}",
            f"- Source variant rows: {summary['source_variant_rows']}",
            f"- Source extra images: {summary['source_extra_images']}",
            f"- Product patterns: {_format_counts(summary['pattern_counts'])}",
            f"- Axis patterns: {_format_counts(summary['axis_pattern_counts'])}",
            f"- Media requirements: {_format_counts(summary['media_requirement_counts'])}",
            "",
            "## Pattern Matrix",
            "",
            "| Odoo pattern | ERPNext primitive / contract | Missing generic architecture | Import implications |",
            "|---|---|---|---|",
        ]
        lines.extend(_pattern_matrix_rows())
        lines.extend(
            [
                "",
                "## Product Pattern Examples",
                "",
                "| Example product | Slug | Patterns | Required architecture | Import implications |",
                "|---|---|---|---|---|",
            ]
        )
        for product in self.products:
            lines.append(
                "| "
                + " | ".join(
                    [
                        product.example_label,
                        f"`{product.slug}`",
                        ", ".join(product.patterns) or "none",
                        "<br>".join(product.erpnext_contract_requirements),
                        "<br>".join(product.import_implications),
                    ]
                )
                + " |"
            )
        return "\n".join(lines).rstrip() + "\n"


def build_product_pattern_report(
    products: list[dict[str, Any]],
    *,
    metadata: dict[str, Any] | None = None,
) -> ProductPatternReport:
    return ProductPatternReport(
        products=tuple(build_product_pattern_contract(product) for product in products),
        metadata=dict(metadata or {}),
    )


def build_product_pattern_contract(product: dict[str, Any]) -> ProductPatternContract:
    attributes = product.get("attributes") or {}
    axes = tuple(_axis_contract(name, axis, product=product) for name, axis in attributes.items())
    pattern_names = _product_patterns(product, axes)
    return ProductPatternContract(
        slug=_clean(product.get("slug")),
        odoo_product_id=_clean(product.get("odoo_id")),
        source_name=_clean(product.get("name")),
        source_url=_clean(product.get("url")),
        currency=_clean(product.get("currency")),
        source_variant_rows=len(product.get("valid_variants") or []),
        source_declared_variant_count=_int_or_none(product.get("variant_count")),
        base_price=_money_or_none(product.get("base_price")),
        patterns=pattern_names,
        axis_contracts=axes,
        media_roles=_media_requirements(product),
        sale_unit_contract=_sale_unit_contract(product, axes, pattern_names),
        pricing=_pricing_summary(product, axes),
        source_integrity=_source_integrity(product),
        erpnext_contract_requirements=_erpnext_requirements(pattern_names),
        import_implications=_import_implications(pattern_names),
        example_label=_clean(product.get("name")) or _clean(product.get("slug")),
    )


def _axis_contract(axis_name: str, axis: dict[str, Any], *, product: dict[str, Any]) -> AxisPatternContract:
    values = _axis_values(axis)
    patterns: list[AxisPattern] = []
    lower = _key(axis_name)
    is_color = is_balloon_color_axis(axis_name)
    review_reason = ""

    if axis_name in CONFIRMED_ADD_ONS:
        patterns.append("add_on_axis")
    elif axis_name in REVIEW_ADD_ONS:
        patterns.append("review_only_axis")
        review_reason = REVIEW_ADD_ONS[axis_name]
    elif is_color and len(values) >= LARGE_COLOR_VALUE_THRESHOLD:
        patterns.append("large_single_choice_color")
    elif is_color:
        patterns.append("multi_color_recipe_customization")
    else:
        patterns.append("required_sale_unit_axis")

    if _looks_like_design_recipe_axis(lower):
        _append_unique(patterns, "multi_color_recipe_customization")
    if _looks_like_conditional_pricing_axis(lower, values, product):
        _append_unique(patterns, "conditional_pricing_candidate")
    if _looks_like_freeform_axis(lower, values):
        _append_unique(patterns, "freeform_customer_text_candidate")

    primitive_key, primitive, selector_key, implication, selector, pricing_strategy = _axis_mapping(
        axis_name,
        values,
        tuple(patterns),
    )
    return AxisPatternContract(
        name=str(axis_name),
        source_value_count=len(values),
        patterns=tuple(patterns),
        source_values=values,
        source_value_hash=_stable_hash(values),
        primitive_key=primitive_key,
        erpnext_primitive=primitive,
        selector_key=selector_key,
        import_implication=implication,
        selector_requirement=selector,
        pricing_strategy=pricing_strategy,
        review_reason=review_reason,
        sample_values=tuple(values[:8]),
    )


def _axis_mapping(
    axis_name: str,
    values: tuple[str, ...],
    patterns: tuple[AxisPattern, ...],
) -> tuple[str, str, str, str, str, str]:
    if "add_on_axis" in patterns:
        return (
            "separate_priced_item",
            "separate ERPNext Item + Item Price + add-on line contract",
            "validated_add_on_input",
            "Do not create required variants for confirmed add-ons; import them as optional priced lines.",
            "validated add-on input with quantity/value limits",
            "separate_item_price",
        )
    if "review_only_axis" in patterns:
        return (
            "review_only_quote_gate",
            "quote-first review-only option contract",
            "quote_or_hidden_review_packet",
            "Do not expose this option in checkout until a priced add-on or required-axis contract exists.",
            "quote-first selector or hidden review packet",
            "not_checkout_priced",
        )
    if "large_single_choice_color" in patterns:
        return (
            "multi_color_configuration_contract",
            "multi-color/recipe-capable configuration contract",
            "multi_color_recipe_builder",
            "Checkout imports must preserve color selection or recipe details in validated line configuration.",
            "multi-color/recipe builder with cart, checkout, SO/SI, and receipt preservation",
            "quote_or_validated_configuration_price",
        )
    if "multi_color_recipe_customization" in patterns:
        return (
            "multi_color_recipe_payload",
            "multi-color recipe customization contract",
            "recipe_builder",
            "Avoid variant explosion; preserve recipe details in quote/customization payload unless finite priced recipes exist.",
            "color recipe builder with summary and validation",
            "quote_or_validated_configuration_price",
        )
    if "conditional_pricing_candidate" in patterns:
        return (
            "required_variant_axis_price_matrix",
            "required variant axis plus explicit price matrix",
            "dependency_aware_finite_selector",
            "Import can create variants, but checkout requires one approved price per projected sale unit.",
            "dependency-aware finite selector",
            "explicit_price_matrix",
        )
    if len(values) <= FINITE_AXIS_VALUE_LIMIT:
        return (
            "item_variant_attribute",
            "ERPNext Item Variant Attribute + Item Price",
            "finite_radio_or_cards",
            "Create finite variants when each value maps to an enabled priced sale unit.",
            "radio/cards selector",
            "item_price_per_variant",
        )
    return (
        "item_variant_attribute_dependency_matrix",
        "ERPNext Item Variant Attribute with dependency matrix",
        "single_select_dependency_filter",
        "Large finite axes need resolver verification before checkout.",
        "single-select selector with dependency filtering",
        "verified_item_price_per_resolved_variant",
    )


def _product_patterns(product: dict[str, Any], axes: tuple[AxisPatternContract, ...]) -> tuple[str, ...]:
    patterns: list[str] = []
    axis_patterns = {pattern for axis in axes for pattern in axis.patterns}
    if not axes and _is_priced(product):
        patterns.append("simple_single_sku")
    if "required_sale_unit_axis" in axis_patterns:
        patterns.append("finite_variants")
    if "large_single_choice_color" in axis_patterns:
        patterns.append("large_single_choice_color")
    if "multi_color_recipe_customization" in axis_patterns:
        patterns.append("multi_color_recipes")
    if _required_axis_count(axes) > 1:
        patterns.append("multi_axis_priced_variants")
    if "add_on_axis" in axis_patterns or "review_only_axis" in axis_patterns:
        patterns.append("add_ons")
    if "conditional_pricing_candidate" in axis_patterns or _distinct_source_price_count(product) > 1:
        patterns.append("conditional_pricing")
    if "freeform_customer_text_candidate" in axis_patterns or _description_has_freeform_signal(product):
        patterns.append("freeform_customer_text")
    if product.get("image_url") or product.get("additional_image_urls"):
        patterns.append("media_gallery_variant_media")
    if not patterns:
        patterns.append("simple_single_sku")
    return tuple(dict.fromkeys(patterns))


def _required_axis_count(axes: tuple[AxisPatternContract, ...]) -> int:
    return sum(1 for axis in axes if "required_sale_unit_axis" in axis.patterns)


def _media_requirements(product: dict[str, Any]) -> MediaRoleRequirement:
    requirements: list[str] = []
    primary = _clean(product.get("image_url"))
    extra_count = len(product.get("additional_image_urls") or [])
    variant_rows = len(product.get("valid_variants") or [])
    if primary:
        requirements.append("primary_image")
    if "product.product" in primary or variant_rows:
        requirements.append("variant_media_review")
    if extra_count:
        requirements.append("gallery_classification")
    if not requirements:
        requirements.append("media_missing_or_not_required")
    return MediaRoleRequirement(
        primary_image_url=primary,
        extra_image_count=extra_count,
        source_variant_rows=variant_rows,
        requirements=tuple(requirements),
    )


def _pricing_summary(product: dict[str, Any], axes: tuple[AxisPatternContract, ...]) -> dict[str, Any]:
    prices = _source_prices(product)
    candidate_axes = [
        axis.name for axis in axes if "conditional_pricing_candidate" in axis.patterns
    ]
    return {
        "base_price": _money_or_none(product.get("base_price")),
        "currency": _clean(product.get("currency")),
        "distinct_source_prices": prices,
        "distinct_source_price_count": len(prices),
        "conditional_pricing_candidate_axes": candidate_axes,
        "source_has_flat_price_for_option_grid": bool(candidate_axes and len(prices) <= 1),
        "import_requirement": (
            "explicit_price_matrix_or_quote_first"
            if candidate_axes and len(prices) <= 1
            else "price_per_sale_unit_verification"
        ),
    }


def _sale_unit_contract(
    product: dict[str, Any],
    axes: tuple[AxisPatternContract, ...],
    patterns: tuple[str, ...],
) -> dict[str, Any]:
    if not _is_priced(product):
        return {
            "path": "not_priced",
            "checkout_eligible": False,
            "requirements": ("price_required_before_sale_unit",),
        }
    if "simple_single_sku" in patterns:
        return {
            "path": "simple_single_sku",
            "checkout_eligible": True,
            "requirements": (
                "ERPNext Item",
                "Website Item",
                "Item Price",
                "stock or non-stock sale settings",
            ),
            "selector_key": "quantity_only",
            "pricing_strategy": "base_item_price",
        }
    if "large_single_choice_color" in patterns or "multi_color_recipes" in patterns:
        return {
            "path": "multi_color_configuration_contract",
            "checkout_eligible": False,
            "requirements": (
                "multi-color/recipe-capable cart selected_config",
                "checkout validation contract",
                "Sales Order/Sales Invoice line JSON preservation",
                "receipt summary preservation",
                "quote gate until configuration price path exists",
            ),
            "selector_key": "multi_color_recipe_builder",
            "pricing_strategy": "quote_or_validated_configuration_price",
        }
    required_axes = tuple(axis.name for axis in axes if "required_sale_unit_axis" in axis.patterns)
    if required_axes:
        return {
            "path": "finite_variant_sale_units",
            "checkout_eligible": True,
            "required_axes": required_axes,
            "requirements": (
                "ERPNext Item template",
                "enabled Item variants",
                "Item Variant Attribute rows",
                "Item Price for each resolved sale unit",
                "Website Item linked to the template",
            ),
            "selector_key": "finite_axis_resolver",
            "pricing_strategy": "item_price_per_resolved_sale_unit",
        }
    return {
        "path": "priced_configuration_or_quote_gate",
        "checkout_eligible": False,
        "requirements": (
            "explicit stored configuration contract",
            "approved price preservation rule",
            "quote gate until sale-unit path exists",
        ),
        "selector_key": "configuration_review",
        "pricing_strategy": "requires_explicit_configuration_price",
    }


def _erpnext_requirements(patterns: tuple[str, ...]) -> tuple[str, ...]:
    requirements = []
    if "simple_single_sku" in patterns:
        requirements.append("Single SKU Item, Website Item, and Item Price contract")
    if "finite_variants" in patterns:
        requirements.append("Item template, Item variants, Item Variant Attribute rows, and Item Price rows")
    if "large_single_choice_color" in patterns:
        requirements.append("Multi-color/recipe-capable line configuration contract")
    if "multi_color_recipes" in patterns:
        requirements.append("Multi-color recipe/customization payload and quote-first fallback")
    if "multi_axis_priced_variants" in patterns:
        requirements.append("Dependency matrix and resolver coverage for all required-axis combinations")
    if "add_ons" in patterns:
        requirements.append("Add-on registry with separate priced Items or review-only quote gate")
    if "conditional_pricing" in patterns:
        requirements.append("Approved price matrix or quote-first lane for conditional prices")
    if "freeform_customer_text" in patterns:
        requirements.append("Validated customer text/customization storage in line configuration or quote intake")
    if "media_gallery_variant_media" in patterns:
        requirements.append("Media role classification before publishing extra or variant images")
    return tuple(requirements or ("Single SKU Item and Website Item contract",))


def _import_implications(patterns: tuple[str, ...]) -> tuple[str, ...]:
    implications = []
    if "simple_single_sku" in patterns:
        implications.append("Import as one enabled sale unit with one Website Item and one Item Price.")
    if "finite_variants" in patterns:
        implications.append("Project source axes into required sale units before creating variants.")
    if "large_single_choice_color" in patterns:
        implications.append("Do not clear checkout until color selections preserve cart, checkout, SO/SI, and receipt data.")
    if "multi_color_recipes" in patterns:
        implications.append("Avoid color-combination variant explosion; preserve recipe details as customization/quote data.")
    if "multi_axis_priced_variants" in patterns:
        implications.append("Import only combinations that resolve to one enabled priced ERPNext Item.")
    if "add_ons" in patterns:
        implications.append("Confirmed add-ons become separate priced lines; unconfirmed add-ons stay quote-first/review-only.")
    if "conditional_pricing" in patterns:
        implications.append("Flat source prices must not be treated as approved tier pricing without provenance.")
    if "freeform_customer_text" in patterns:
        implications.append("Checkout must reject unsupported freeform customizations instead of silently dropping them.")
    if "media_gallery_variant_media" in patterns:
        implications.append("Primary images may map directly; extra/variant media remains held until classified.")
    return tuple(implications or ("Import as simple single SKU when price and media are present.",))


def _pattern_matrix_rows() -> list[str]:
    return [
        "| finite variants | Item template + variants + Item Variant Attribute + Item Price + required-axis contract | Generic sale-unit axis projection and resolver/price verifier | Create variants only for true sale-unit axes; block checkout when resolver or price is incomplete. |",
        "| large single-choice color | Color variant axis or validated customization line payload | Lane-level color decision: color-as-variant vs color-as-configuration | Preserve selected color in checkout; quote-first if selected color cannot be stored/priced. |",
        "| multi-color recipes | Multi-color customization/recipe contract | Recipe schema for color counts, layout zones, style constraints, and summaries | Do not create combinatorial variants; route quote-first until finite priced recipes exist. |",
        "| multi-axis priced variants | Required axes + dependency matrix + Item Price matrix | Dependency-aware selector and all-combination price gate | Import projected combinations only; every checkout combo needs one enabled item and one selling price. |",
        "| add-ons | Separate ERPNext Item + Item Price + Sales Order add-on line | Add-on registry with eligibility, pricing rule, quantity/value validation | Confirmed add-ons become priced extra lines; review-only add-ons stay quote-first. |",
        "| conditional pricing | Price matrix over required axes or quote-first estimator | Explicit price provenance for size/height/length/drop tiers | Do not infer tiered prices from labels; require source/owner-approved prices or quote-first. |",
        "| freeform/customer text | Validated configuration JSON/summary or quote intake fields | Whitelisted text/upload/reference-note schema with limits and document propagation | Paid checkout can accept only approved stored fields; unsupported custom text fails loudly to quote-first. |",
        "| media gallery/variant media | Primary image, gallery role, variant image role, media classification packet | Media assignment workflow and rendered media verifier | Attach clear primary images; hold extras/variant images until classified. |",
    ]


def _axis_values(axis: Any) -> tuple[str, ...]:
    if not isinstance(axis, dict):
        return ()
    values = []
    for value in axis.get("values") or []:
        if isinstance(value, dict) and value.get("name") not in (None, ""):
            values.append(str(value.get("name")).strip())
    return tuple(values)


def _looks_like_conditional_pricing_axis(axis_key: str, values: tuple[str, ...], product: dict[str, Any]) -> bool:
    text = f"{axis_key} {' '.join(values)}".lower()
    if any(token in text for token in CONDITIONAL_PRICE_AXIS_TOKENS):
        return True
    return _distinct_source_price_count(product) > 1


def _looks_like_design_recipe_axis(axis_key: str) -> bool:
    if axis_key == "design":
        return True
    return any(token in axis_key for token in DESIGN_RECIPE_AXIS_TOKENS if token != "design")


def _looks_like_freeform_axis(axis_key: str, values: tuple[str, ...]) -> bool:
    if any(token in axis_key for token in FREEFORM_TEXT_TOKENS):
        return True
    value_text = _key(" ".join(values))
    return any(token in value_text for token in FREEFORM_TEXT_TOKENS)


def _description_has_freeform_signal(product: dict[str, Any]) -> bool:
    text = _key(product.get("description"))
    return any(token in text for token in FREEFORM_TEXT_TOKENS)


def _source_prices(product: dict[str, Any]) -> list[str]:
    prices = set()
    for row in product.get("valid_variants") or []:
        if not isinstance(row, dict):
            continue
        price = row.get("erpnext_variant_price", row.get("price"))
        if price is not None:
            prices.add(_money(price))
    if not prices and product.get("base_price") is not None:
        prices.add(_money(product.get("base_price")))
    return sorted(prices, key=lambda value: Decimal(value))


def _source_integrity(product: dict[str, Any]) -> dict[str, Any]:
    attributes = product.get("attributes") if isinstance(product.get("attributes"), dict) else {}
    variants = product.get("valid_variants") if isinstance(product.get("valid_variants"), list) else []
    axis_values = {
        str(name): _axis_values(axis)
        for name, axis in sorted(attributes.items(), key=lambda item: str(item[0]).lower())
    }
    return {
        "odoo_product_id": _clean(product.get("odoo_id")),
        "currency": _clean(product.get("currency")),
        "source_declared_variant_count": _int_or_none(product.get("variant_count")),
        "source_valid_variant_count": len(variants),
        "axis_value_counts": {name: len(values) for name, values in axis_values.items()},
        "axis_value_hashes": {name: _stable_hash(values) for name, values in axis_values.items()},
        "valid_variant_hash": _stable_hash(variants),
        "valid_variant_pointer": "source.valid_variants",
    }


def _distinct_source_price_count(product: dict[str, Any]) -> int:
    return len(_source_prices(product))


def _is_priced(product: dict[str, Any]) -> bool:
    return bool(_source_prices(product))


def _stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _int_or_none(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _append_unique(values: list[AxisPattern], value: AxisPattern) -> None:
    if value not in values:
        values.append(value)


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _key(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().replace("-", " ").replace("_", " ").split())


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _money_or_none(value: Any) -> str | None:
    if value is None:
        return None
    return _money(value)


def _money(value: Any) -> str:
    try:
        return str(Decimal(str(value)).quantize(Decimal("0.01")))
    except (InvalidOperation, ValueError):
        return str(value)
