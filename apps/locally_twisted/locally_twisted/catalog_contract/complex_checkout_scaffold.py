"""Complex product checkout scaffold for ERPNext ecommerce.

This module is pure/data-oriented. It translates the current
ProductPatternContract report into the checkout regression and enhancement map
for legacy_source-imported products.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any, Literal


SCHEMA_VERSION = "lt-complex-checkout-scaffold-v1"
SOURCE_SCHEMA_VERSION = "lt-erpnext-product-pattern-contract-v1"
EXPECTED_SOURCE_PRODUCTS = 53
EXPECTED_DIRECT_CHECKOUT_PRODUCTS = 53

ScaffoldStage = Literal[
    "direct_checkout_regression_guard",
    "checkout_architecture_gap",
    "simple_axis_lane_flip_candidate",
    "multi_color_recipe_ui_required",
    "add_on_or_conditional_pricing_blocked",
    "needs_review_or_missing",
]


@dataclass(frozen=True)
class ComplexCheckoutScaffoldRow:
    slug: str
    source_name: str
    route: str
    current_website_lane: str
    current_capability: str
    patterns: tuple[str, ...]
    scaffold_stage: ScaffoldStage
    proof_ladder_stage: str
    required_ui_components: tuple[str, ...]
    required_server_contracts: tuple[str, ...]
    required_payload_keys: tuple[str, ...]
    preconditions_before_checkout: tuple[str, ...]
    gate_verifiers: tuple[str, ...]
    lane_flip_policy: dict[str, Any]
    source_axes: dict[str, list[str]] = field(default_factory=dict)
    catalog_counts: dict[str, int] = field(default_factory=dict)
    special_rules: dict[str, Any] = field(default_factory=dict)
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ComplexCheckoutScaffoldReport:
    rows: tuple[ComplexCheckoutScaffoldRow, ...]
    metadata: dict[str, Any] = field(default_factory=dict)
    source_summary: dict[str, Any] = field(default_factory=dict)
    contract_failures: tuple[str, ...] = ()

    def summary(self) -> dict[str, Any]:
        stage_counts = Counter(row.scaffold_stage for row in self.rows)
        ladder_counts = Counter(row.proof_ladder_stage for row in self.rows)
        lane_counts = Counter(row.current_website_lane for row in self.rows)
        return {
            "schema_version": SCHEMA_VERSION,
            "source_products": len(self.rows),
            "ok": not self.contract_failures,
            "stage_counts": dict(sorted(stage_counts.items())),
            "proof_ladder_counts": dict(sorted(ladder_counts.items())),
            "website_lane_counts": dict(sorted(lane_counts.items())),
            "direct_checkout_regression_guards": stage_counts.get("direct_checkout_regression_guard", 0),
            "simple_axis_lane_flip_candidates": stage_counts.get("simple_axis_lane_flip_candidate", 0),
            "complex_ui_required_products": stage_counts.get("multi_color_recipe_ui_required", 0),
            "add_on_or_conditional_blocked_products": stage_counts.get(
                "add_on_or_conditional_pricing_blocked", 0
            ),
            "needs_review_or_missing_products": stage_counts.get("needs_review_or_missing", 0),
            "checkout_architecture_gap_products": stage_counts.get("checkout_architecture_gap", 0),
        }

    def to_artifact(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "generated_from_schema_version": SOURCE_SCHEMA_VERSION,
            "metadata": self.metadata,
            "source_summary": self.source_summary,
            "read_only": True,
            "destructive_allowed": False,
            "live_site_update_allowed": False,
            "purpose": (
            "Local ERPNext ecommerce scaffold for product-page checkout regression guards, "
            "deferred enhancement controls, server contracts, and proof order."
            ),
            "ok": not self.contract_failures,
            "summary": self.summary(),
            "contract_failures": list(self.contract_failures),
            "proof_ladder": _proof_ladder(),
            "products": [row.to_dict() for row in self.rows],
        }

    def to_markdown(self) -> str:
        summary = self.summary()
        lines = [
            "# Complex Checkout Scaffold",
            "",
            "Read-only local scaffold for ERPNext ecommerce product-page checkout work.",
            "This is not live approval and does not permit a Frappe Cloud or DNS update.",
            "",
            "## Summary",
            "",
            f"- Products checked: {summary['source_products']}",
            f"- Scaffold ok: {summary['ok']}",
            f"- Stage counts: {_format_counts(summary['stage_counts'])}",
            f"- Proof ladder counts: {_format_counts(summary['proof_ladder_counts'])}",
            f"- Direct checkout regression guards: {summary['direct_checkout_regression_guards']}",
            f"- Simple-axis lane-flip candidates: {summary['simple_axis_lane_flip_candidates']}",
            f"- Complex UI required products: {summary['complex_ui_required_products']}",
            f"- Add-on or conditional-pricing blocked products: {summary['add_on_or_conditional_blocked_products']}",
            "",
            "## Contract Failures",
            "",
        ]
        if self.contract_failures:
            lines.extend(f"- {failure}" for failure in self.contract_failures)
        else:
            lines.append("- None")

        lines.extend(["", "## Proof Ladder", ""])
        for key, value in _proof_ladder().items():
            lines.append(f"- `{key}`: {value}")

        lines.extend(
            [
                "",
                "## Product Scaffold Rows",
                "",
                "| Product | Slug | Lane | Capability | Scaffold stage | Required UI | Preconditions before checkout |",
                "|---|---|---|---|---|---|---|",
            ]
        )
        for row in self.rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _md(row.source_name),
                        f"`{_md(row.slug)}`",
                        _md(row.current_website_lane),
                        _md(row.current_capability),
                        _md(row.scaffold_stage),
                        "<br>".join(_md(value) for value in row.required_ui_components),
                        "<br>".join(_md(value) for value in row.preconditions_before_checkout),
                    ]
                )
                + " |"
            )
        return "\n".join(lines).rstrip() + "\n"


def build_complex_checkout_scaffold_report(
    product_pattern_artifact: dict[str, Any],
    *,
    metadata: dict[str, Any] | None = None,
    expected_source_products: int | None = EXPECTED_SOURCE_PRODUCTS,
    expected_direct_checkout_products: int | None = EXPECTED_DIRECT_CHECKOUT_PRODUCTS,
) -> ComplexCheckoutScaffoldReport:
    """Build a read-only product-by-product complex checkout scaffold."""

    products = product_pattern_artifact.get("products") or []
    rows = tuple(_build_row(row) for row in products if isinstance(row, dict))
    failures = _contract_failures(
        product_pattern_artifact,
        rows,
        expected_source_products=expected_source_products,
        expected_direct_checkout_products=expected_direct_checkout_products,
    )
    return ComplexCheckoutScaffoldReport(
        rows=rows,
        metadata=dict(metadata or {}),
        source_summary=dict(product_pattern_artifact.get("summary") or {}),
        contract_failures=tuple(failures),
    )


def _build_row(row: dict[str, Any]) -> ComplexCheckoutScaffoldRow:
    slug = str(row.get("slug") or "").strip()
    axes = _source_axes(row)
    patterns = tuple(str(pattern) for pattern in row.get("patterns") or ())
    checkout = row.get("checkout_eligibility") or {}
    website_item = row.get("website_item") or {}
    stage = _scaffold_stage(row, axes)
    ui_components = _required_ui_components(row, axes, stage)
    preconditions = _preconditions_before_checkout(row, axes, stage)
    return ComplexCheckoutScaffoldRow(
        slug=slug,
        source_name=str(row.get("source_name") or slug),
        route=str(website_item.get("route") or ""),
        current_website_lane=_website_lane(row),
        current_capability=str(row.get("capability") or ""),
        patterns=patterns,
        scaffold_stage=stage,
        proof_ladder_stage=_proof_ladder_stage(slug, stage, axes, patterns),
        required_ui_components=ui_components,
        required_server_contracts=_required_server_contracts(row, axes, stage),
        required_payload_keys=_required_payload_keys(row),
        preconditions_before_checkout=preconditions,
        gate_verifiers=_gate_verifiers(stage, axes, patterns),
        lane_flip_policy=_lane_flip_policy(stage, preconditions),
        source_axes=axes,
        catalog_counts={key: int(value or 0) for key, value in (row.get("live_counts") or {}).items()},
        special_rules=_special_rules(slug),
        notes=_notes(row, axes, stage),
    )


def _scaffold_stage(row: dict[str, Any], axes: dict[str, list[str]]) -> ScaffoldStage:
    lane = _website_lane(row)
    capability = str(row.get("capability") or "")
    if lane == "checkout" and capability == "direct_checkout_ready":
        return "direct_checkout_regression_guard"
    if lane == "checkout":
        return "checkout_architecture_gap"
    if capability == "needs_review_or_missing" or lane in {"missing", "needs_review", ""}:
        return "needs_review_or_missing"
    if _requires_add_on_or_conditional_mapping(row, axes):
        return "add_on_or_conditional_pricing_blocked"
    if _requires_multi_color_ui(row, axes):
        return "multi_color_recipe_ui_required"
    return "simple_axis_lane_flip_candidate"


def _required_ui_components(
    row: dict[str, Any],
    axes: dict[str, list[str]],
    stage: ScaffoldStage,
) -> tuple[str, ...]:
    components: list[str] = ["product_page_checkout_contract"]
    if stage == "direct_checkout_regression_guard":
        components.extend(
            [
                "preserve_current_direct_checkout_controls",
            ]
        )

    if axes.get("required_sale_unit_axes"):
        components.append("required_axis_selector")
    if _requires_multi_color_ui(row, axes):
        components.extend(
            [
                "multi_slot_color_recipe_builder",
                "palette_picker",
                "backend_driven_image_updates",
                "color_recipe_summary_parity",
            ]
        )
    if axes.get("add_on_axes") or axes.get("review_only_axes"):
        components.append("add_on_contract_ui")
    if axes.get("conditional_pricing_axes") or "conditional_pricing" in set(row.get("patterns") or []):
        components.append("conditional_pricing_panel")
    if axes.get("freeform_customer_text_axes") or "freeform_customer_text" in set(row.get("patterns") or []):
        components.append("customer_text_validation")
    components.extend(
        [
            "cart_checkout_receipt_summary_parity",
        ]
    )
    if stage != "direct_checkout_regression_guard":
        components.append("mobile_and_desktop_product_journey")
    return tuple(_unique(components))


def _required_server_contracts(
    row: dict[str, Any],
    axes: dict[str, list[str]],
    stage: ScaffoldStage,
) -> tuple[str, ...]:
    contracts = [
        "ProductPatternContract source mapper",
        "Website Item lt_product_page_type and lt_commerce_lane",
        "selected_config schema version lt-product-config-v1",
        "cart line key canonical configuration JSON",
        "Sales Order/Sales Invoice line summary and JSON fields",
    ]
    if stage != "direct_checkout_regression_guard":
        contracts.append("per-product lane-flip proof artifact")
    if _requires_multi_color_ui(row, axes):
        contracts.append("color_recipes checkout validation and receipt preservation")
    if axes.get("add_on_axes") or axes.get("review_only_axes"):
        contracts.append("priced add-on item registry or quote-only review mapping")
    if axes.get("conditional_pricing_axes") or "conditional_pricing" in set(row.get("patterns") or []):
        contracts.append("conditional pricing matrix with ERPNext price provenance")
    return tuple(_unique(contracts))


def _required_payload_keys(row: dict[str, Any]) -> tuple[str, ...]:
    schema = ((row.get("server_boundary") or {}).get("selected_config_schema") or {})
    keys = [key for key in ("website_item_code", "selected_options", "color_recipes", "add_ons", "customizations") if key in schema]
    return tuple(keys or ["website_item_code", "selected_options", "color_recipes", "add_ons", "customizations"])


def _preconditions_before_checkout(
    row: dict[str, Any],
    axes: dict[str, list[str]],
    stage: ScaffoldStage,
) -> tuple[str, ...]:
    if stage == "direct_checkout_regression_guard":
        return ("keep current direct-checkout verifiers green",)

    checkout = row.get("checkout_eligibility") or {}
    preconditions: list[str] = [str(value) for value in checkout.get("blocking_reasons") or []]
    if stage == "simple_axis_lane_flip_candidate":
        preconditions.append("focused local lane-flip rehearsal proof required")
    if _requires_multi_color_ui(row, axes):
        preconditions.append("multi-color recipe UI and backend validation required")
    if axes.get("add_on_axes") or axes.get("review_only_axes"):
        preconditions.append("add-on mapping, pricing, quantity/value limits, and SO/SI preservation required")
    if axes.get("conditional_pricing_axes") or "conditional_pricing" in set(row.get("patterns") or []):
        preconditions.append("conditional pricing matrix and totals provenance required")
    if axes.get("freeform_customer_text_axes") or "freeform_customer_text" in set(row.get("patterns") or []):
        preconditions.append("freeform customer text validation and summary preservation required")
    if not checkout.get("representative_priced_item_ready") and stage != "needs_review_or_missing":
        preconditions.append("representative priced item required")
    if not checkout.get("line_configuration_fields_ready"):
        preconditions.append("Sales Order/Sales Invoice line configuration fields required")
    if stage == "needs_review_or_missing":
        preconditions.append("Website Item, source mapper, lane, and product-page type review required")
    return tuple(_unique(preconditions or ["explicit checkout proof required"]))


def _gate_verifiers(stage: ScaffoldStage, axes: dict[str, list[str]], patterns: tuple[str, ...]) -> tuple[str, ...]:
    gates = [
        "python scripts/verify/product_pattern_contract.py",
        "python scripts/verify/product_pattern_contract_report.py",
        "python scripts/verify/product_page_runtime_contract.py",
        "python scripts/verify/cart_checkout_contract.py",
    ]
    if stage == "direct_checkout_regression_guard":
        gates.extend(
            [
                "python scripts/verify/checkout_product_family_contract.py",
                "python scripts/verify/product_add_on_dependency_contract.py",
            ]
        )
    else:
        gates.append("python scripts/verify/checkout_product_family_contract.py")
    if axes.get("customization_axes") or set(patterns) & {"large_single_choice_color", "multi_color_recipes"}:
        gates.extend(
            [
                "node scripts/verify/post_import_checkout_proof.js",
                "python scripts/verify/product_quote_customization_contract.py",
            ]
        )
    if axes.get("add_on_axes") or axes.get("review_only_axes") or "add_ons" in set(patterns):
        gates.extend(
            [
                "python scripts/verify/product_add_on_approval_packet.py",
                "python scripts/verify/product_add_on_dependency_contract.py",
            ]
        )
    if axes.get("conditional_pricing_axes") or "conditional_pricing" in set(patterns):
        gates.extend(
            [
                "python scripts/verify/product_page_price_enrichment_contract.py",
                "python scripts/verify/product_page_price_review_packet.py",
            ]
        )
    return tuple(_unique(gates))


def _lane_flip_policy(stage: ScaffoldStage, preconditions: tuple[str, ...]) -> dict[str, Any]:
    return {
        "live_site_update_allowed": False,
        "customer_checkout_enablement_allowed_by_this_report": False,
        "already_checkout_guarded": stage == "direct_checkout_regression_guard",
        "may_enter_focused_local_lane_flip_rehearsal": stage == "simple_axis_lane_flip_candidate",
        "do_not_flip_until": [] if stage == "direct_checkout_regression_guard" else list(preconditions),
    }


def _notes(row: dict[str, Any], axes: dict[str, list[str]], stage: ScaffoldStage) -> tuple[str, ...]:
    notes: list[str] = []
    if stage == "simple_axis_lane_flip_candidate":
        notes.append("Candidate only; this report does not flip the ERPNext lane.")
    if _requires_multi_color_ui(row, axes):
        notes.append("Color choices must be preserved as color_recipes, not flattened selected_options.")
    if stage == "direct_checkout_regression_guard":
        notes.append("Existing checkout product; protect it while complex products are built.")
    return tuple(notes)


def _contract_failures(
    artifact: dict[str, Any],
    rows: tuple[ComplexCheckoutScaffoldRow, ...],
    *,
    expected_source_products: int | None,
    expected_direct_checkout_products: int | None,
) -> list[str]:
    failures: list[str] = []
    if artifact.get("schema_version") != SOURCE_SCHEMA_VERSION:
        failures.append(f"expected source schema {SOURCE_SCHEMA_VERSION}, found {artifact.get('schema_version')}")
    if artifact.get("read_only") is not True:
        failures.append("source ProductPatternContract artifact must be read_only")
    if artifact.get("destructive_allowed") is not False:
        failures.append("source ProductPatternContract artifact must be non-destructive")
    if expected_source_products is not None and len(rows) < expected_source_products:
        failures.append(f"expected at least {expected_source_products} source products, found {len(rows)}")

    direct_checkout_count = sum(1 for row in rows if row.current_website_lane == "checkout")
    if expected_direct_checkout_products is not None and direct_checkout_count != expected_direct_checkout_products:
        failures.append(
            "current checkout-lane product count changed; expected "
            f"{expected_direct_checkout_products}, found {direct_checkout_count}"
        )

    checkout_gaps = sorted(row.slug for row in rows if row.scaffold_stage == "checkout_architecture_gap")
    if checkout_gaps:
        failures.append(f"explicit checkout products have architecture gaps: {checkout_gaps}")

    seen_slugs: set[str] = set()
    for row in rows:
        if not row.slug:
            failures.append("scaffold row missing slug")
        if row.slug in seen_slugs:
            failures.append(f"duplicate scaffold row slug: {row.slug}")
        seen_slugs.add(row.slug)
        if not row.required_ui_components:
            failures.append(f"{row.slug} missing required_ui_components")
        if not row.required_server_contracts:
            failures.append(f"{row.slug} missing required_server_contracts")
        if not row.gate_verifiers:
            failures.append(f"{row.slug} missing gate_verifiers")
        if row.scaffold_stage != "direct_checkout_regression_guard":
            if row.lane_flip_policy.get("customer_checkout_enablement_allowed_by_this_report") is not False:
                failures.append(f"{row.slug} scaffold must not authorize customer checkout enablement")
            if not row.lane_flip_policy.get("do_not_flip_until"):
                failures.append(f"{row.slug} missing do_not_flip_until preconditions")
        if _row_requires_multi_color(row) and "multi_slot_color_recipe_builder" not in row.required_ui_components:
            failures.append(f"{row.slug} missing multi-slot color recipe builder requirement")
        if _row_requires_multi_color(row) and "color_recipe_summary_parity" not in row.required_ui_components:
            failures.append(f"{row.slug} missing color recipe summary parity requirement")
        if _row_requires_multi_color(row) and not any("post_import_checkout_proof" in gate for gate in row.gate_verifiers):
            failures.append(f"{row.slug} missing multi-color browser proof gate")
        if _row_requires_add_on_or_conditional(row) and row.scaffold_stage == "simple_axis_lane_flip_candidate":
            failures.append(f"{row.slug} cannot be a simple lane-flip candidate while add-on/conditional work remains")
        if (
            row.slug == "classic-arch"
            and row.scaffold_stage != "direct_checkout_regression_guard"
            and row.proof_ladder_stage != "06_classic_arch_last"
        ):
            failures.append("classic-arch must remain the last stress product in the proof ladder")
    return failures


def _source_axes(row: dict[str, Any]) -> dict[str, list[str]]:
    raw = row.get("source_axes") or {}
    return {
        "required_sale_unit_axes": _string_list(raw.get("required_sale_unit_axes")),
        "customization_axes": _string_list(raw.get("customization_axes")),
        "add_on_axes": _string_list(raw.get("add_on_axes")),
        "review_only_axes": _string_list(raw.get("review_only_axes")),
        "conditional_pricing_axes": _string_list(raw.get("conditional_pricing_axes")),
        "freeform_customer_text_axes": _string_list(raw.get("freeform_customer_text_axes")),
    }


def _requires_multi_color_ui(row: dict[str, Any], axes: dict[str, list[str]]) -> bool:
    patterns = set(row.get("patterns") or [])
    return bool(axes.get("customization_axes") or patterns & {"large_single_choice_color", "multi_color_recipes"})


def _requires_add_on_or_conditional_mapping(row: dict[str, Any], axes: dict[str, list[str]]) -> bool:
    patterns = set(row.get("patterns") or [])
    return bool(
        axes.get("add_on_axes")
        or axes.get("review_only_axes")
        or axes.get("conditional_pricing_axes")
        or axes.get("freeform_customer_text_axes")
        or patterns & {"add_ons", "conditional_pricing", "freeform_customer_text"}
    )


def _row_requires_multi_color(row: ComplexCheckoutScaffoldRow) -> bool:
    return bool(
        row.source_axes.get("customization_axes")
        or set(row.patterns) & {"large_single_choice_color", "multi_color_recipes"}
    )


def _row_requires_add_on_or_conditional(row: ComplexCheckoutScaffoldRow) -> bool:
    return bool(
        row.source_axes.get("add_on_axes")
        or row.source_axes.get("review_only_axes")
        or row.source_axes.get("conditional_pricing_axes")
        or row.source_axes.get("freeform_customer_text_axes")
        or set(row.patterns) & {"add_ons", "conditional_pricing", "freeform_customer_text"}
    )


def _proof_ladder_stage(
    slug: str,
    stage: ScaffoldStage,
    axes: dict[str, list[str]],
    patterns: tuple[str, ...],
) -> str:
    if stage == "direct_checkout_regression_guard":
        return "01_preserve_existing_direct_checkout"
    if stage == "simple_axis_lane_flip_candidate":
        return "02_simple_axis_lane_flip_rehearsal"
    if slug in {"classic-column", "classic-organic-columns"}:
        return "04_classic_column_before_arch"
    if slug == "classic-arch":
        return "06_classic_arch_last"
    if _requires_add_on_or_conditional_mapping({"patterns": patterns}, axes):
        return "05_add_on_or_conditional_after_mapping"
    if _requires_multi_color_ui({"patterns": patterns}, axes):
        return "03_first_multi_color_recipe_case"
    return "07_review_or_catalog_repair"


def _proof_ladder() -> dict[str, str]:
    return {
        "01_preserve_existing_direct_checkout": "Keep all 53 legacy_source-imported checkout products green.",
        "02_simple_axis_lane_flip_rehearsal": "Locally prove any internal-hold product before checkout exposure.",
        "03_first_multi_color_recipe_case": "Build and prove one multi-color recipe product before broader rollout.",
        "04_classic_column_before_arch": "Prove the column-shaped complex product path before the full arch path.",
        "05_add_on_or_conditional_after_mapping": "Build approved add-on and conditional pricing controls only after mapping is explicit.",
        "06_classic_arch_last": "Use Classic Arch as the final stress case because design-dependent color limits are hardest.",
        "07_review_or_catalog_repair": "Repair missing/needs-review records before they enter checkout planning.",
    }


def _special_rules(slug: str) -> dict[str, Any]:
    if slug != "classic-arch":
        return {}
    return {
        "proof_position": "last_complex_stress_case",
        "design_dependent_color_limits": [
            {"design_value": "Swirl", "max_color_count": 4},
            {"design_value": "Layered", "max_color_count": 8},
        ],
        "source": "storefront-proof-and-complex-ui handoff",
    }


def _website_lane(row: dict[str, Any]) -> str:
    checkout = row.get("checkout_eligibility") or {}
    if checkout.get("website_lane"):
        return str(checkout.get("website_lane"))
    website_item = row.get("website_item") or {}
    return str(website_item.get("lt_commerce_lane") or "missing")


def _string_list(values: Any) -> list[str]:
    if not values:
        return []
    return [str(value) for value in values if str(value or "").strip()]


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            result.append(value)
            seen.add(value)
    return result


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
