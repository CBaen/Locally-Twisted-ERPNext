"""Read-only map from Odoo source export to purchasable product repair lanes."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any


SCHEMA_VERSION = "lt-product-source-repair-map-v1"
PRICE_SCHEMA_VERSION = "lt-product-page-price-enrichment-v1"
SCAFFOLD_SCHEMA_VERSION = "lt-complex-checkout-scaffold-v1"

STAGE_REPAIR_LANES = {
    "direct_checkout_regression_guard": "certified_current_checkout",
    "simple_axis_lane_flip_candidate": "simple_purchasable_rehearsal",
    "multi_color_recipe_ui_required": "multi_color_recipe_checkout_build",
    "add_on_or_conditional_pricing_blocked": "add_on_conditional_pricing_build",
    "needs_review_or_missing": "source_backend_review",
    "checkout_architecture_gap": "checkout_architecture_repair",
}


@dataclass(frozen=True)
class ProductSourceRepairRow:
    slug: str
    source_name: str
    odoo_id: str
    source_url: str
    source_export_found: bool
    business_target: str
    current_customer_state: str
    repair_lane: str
    scaffold_stage: str
    current_website_lane: str
    source_attributes: tuple[str, ...] = ()
    source_variant_count: int = 0
    source_media: dict[str, Any] = field(default_factory=dict)
    price_evidence: dict[str, Any] = field(default_factory=dict)
    required_next_gates: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProductSourceRepairReport:
    rows: tuple[ProductSourceRepairRow, ...]
    metadata: dict[str, Any] = field(default_factory=dict)
    contract_failures: tuple[str, ...] = ()

    def summary(self) -> dict[str, Any]:
        repair_counts = Counter(row.repair_lane for row in self.rows)
        state_counts = Counter(row.current_customer_state for row in self.rows)
        stage_counts = Counter(row.scaffold_stage for row in self.rows)
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": not self.contract_failures,
            "products": len(self.rows),
            "source_export_found": sum(1 for row in self.rows if row.source_export_found),
            "source_export_missing": sum(1 for row in self.rows if not row.source_export_found),
            "certified_checkout_products": state_counts.get("certified_checkout", 0),
            "blocked_until_certified_products": state_counts.get("blocked_until_certified", 0),
            "repair_lane_counts": dict(sorted(repair_counts.items())),
            "current_customer_state_counts": dict(sorted(state_counts.items())),
            "scaffold_stage_counts": dict(sorted(stage_counts.items())),
        }

    def to_artifact(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "metadata": dict(self.metadata),
            "read_only": True,
            "destructive_allowed": False,
            "live_site_update_allowed": False,
            "purpose": (
                "Map every existing Locally Twisted source product to a purchasable-product "
                "repair lane. Legacy quote_first values are treated as internal holds, not "
                "business categories."
            ),
            "summary": self.summary(),
            "contract_failures": list(self.contract_failures),
            "products": [row.to_dict() for row in self.rows],
        }

    def to_markdown(self) -> str:
        summary = self.summary()
        lines = [
            "# Product Source Repair Map",
            "",
            "Read-only map from the Odoo product export to ERPNext purchasable-product repair lanes.",
            "",
            "## Rule",
            "",
            "There are no business quote-first products. If it is a product, the target state is purchasable. "
            "Rows that are not certified are blocked until the source data, pricing, media, and checkout cascade are proven.",
            "",
            "## Summary",
            "",
            f"- Products mapped: {summary['products']}",
            f"- Source export found: {summary['source_export_found']}",
            f"- Source export missing: {summary['source_export_missing']}",
            f"- Certified checkout products: {summary['certified_checkout_products']}",
            f"- Blocked until certified: {summary['blocked_until_certified_products']}",
            f"- Repair lanes: {_format_counts(summary['repair_lane_counts'])}",
            "",
            "## Contract Failures",
            "",
        ]
        if self.contract_failures:
            lines.extend(f"- {failure}" for failure in self.contract_failures)
        else:
            lines.append("- None")

        lines.extend(
            [
                "",
                "## Products",
                "",
                "| Product | Slug | State | Repair lane | Source evidence | Price units | Next gates |",
                "|---|---|---|---|---|---:|---|",
            ]
        )
        for row in self.rows:
            price_units = int(row.price_evidence.get("candidate_units") or 0)
            source_evidence = "found" if row.source_export_found else "missing - repull required"
            lines.append(
                "| "
                + " | ".join(
                    [
                        _md(row.source_name),
                        f"`{_md(row.slug)}`",
                        _md(row.current_customer_state),
                        _md(row.repair_lane),
                        source_evidence,
                        str(price_units),
                        "<br>".join(_md(value) for value in row.required_next_gates),
                    ]
                )
                + " |"
            )
        return "\n".join(lines).rstrip() + "\n"


def build_product_source_repair_map(
    *,
    source_products: list[dict[str, Any]],
    price_enrichment_artifact: dict[str, Any],
    scaffold_artifact: dict[str, Any],
    metadata: dict[str, Any] | None = None,
    expected_source_products: int | None = 53,
    expected_direct_checkout_products: int | None = 18,
) -> ProductSourceRepairReport:
    source_by_slug = _by_slug(source_products)
    price_by_slug = _by_slug(price_enrichment_artifact.get("products") or [])
    scaffold_products = [row for row in scaffold_artifact.get("products") or [] if isinstance(row, dict)]
    rows = tuple(
        _build_row(scaffold_row, source_by_slug.get(_slug(scaffold_row)), price_by_slug.get(_slug(scaffold_row)))
        for scaffold_row in scaffold_products
    )
    failures = _contract_failures(
        rows,
        source_by_slug=source_by_slug,
        price_by_slug=price_by_slug,
        price_enrichment_artifact=price_enrichment_artifact,
        scaffold_artifact=scaffold_artifact,
        expected_source_products=expected_source_products,
        expected_direct_checkout_products=expected_direct_checkout_products,
    )
    return ProductSourceRepairReport(
        rows=rows,
        metadata=dict(metadata or {}),
        contract_failures=tuple(failures),
    )


def _build_row(
    scaffold_row: dict[str, Any],
    source_row: dict[str, Any] | None,
    price_row: dict[str, Any] | None,
) -> ProductSourceRepairRow:
    stage = str(scaffold_row.get("scaffold_stage") or "needs_review_or_missing")
    source_found = bool(source_row)
    current_state = "certified_checkout" if stage == "direct_checkout_regression_guard" else "blocked_until_certified"
    repair_lane = STAGE_REPAIR_LANES.get(stage, "source_backend_review")
    return ProductSourceRepairRow(
        slug=_slug(scaffold_row),
        source_name=str((source_row or {}).get("name") or scaffold_row.get("source_name") or _slug(scaffold_row)),
        odoo_id=str((source_row or {}).get("odoo_id") or ""),
        source_url=str((source_row or {}).get("url") or ""),
        source_export_found=source_found,
        business_target="purchasable_product",
        current_customer_state=current_state,
        repair_lane=repair_lane,
        scaffold_stage=stage,
        current_website_lane=str(scaffold_row.get("current_website_lane") or ""),
        source_attributes=tuple(sorted(str(key) for key in ((source_row or {}).get("attributes") or {}).keys())),
        source_variant_count=int((source_row or {}).get("variant_count") or 0),
        source_media=_source_media(source_row),
        price_evidence=_price_evidence(price_row),
        required_next_gates=_required_next_gates(stage, source_found),
        notes=_notes(scaffold_row, price_row),
    )


def _contract_failures(
    rows: tuple[ProductSourceRepairRow, ...],
    *,
    source_by_slug: dict[str, dict[str, Any]],
    price_by_slug: dict[str, dict[str, Any]],
    price_enrichment_artifact: dict[str, Any],
    scaffold_artifact: dict[str, Any],
    expected_source_products: int | None,
    expected_direct_checkout_products: int | None,
) -> list[str]:
    failures: list[str] = []
    if price_enrichment_artifact.get("schema_version") != PRICE_SCHEMA_VERSION:
        failures.append(
            f"expected price schema {PRICE_SCHEMA_VERSION}, found {price_enrichment_artifact.get('schema_version')}"
        )
    if scaffold_artifact.get("schema_version") != SCAFFOLD_SCHEMA_VERSION:
        failures.append(f"expected scaffold schema {SCAFFOLD_SCHEMA_VERSION}, found {scaffold_artifact.get('schema_version')}")
    if expected_source_products is not None and len(source_by_slug) != expected_source_products:
        failures.append(f"expected {expected_source_products} Odoo source products, found {len(source_by_slug)}")
    if expected_source_products is not None and len(rows) != expected_source_products:
        failures.append(f"expected {expected_source_products} scaffold products, found {len(rows)}")
    if expected_direct_checkout_products is not None:
        direct_count = sum(1 for row in rows if row.current_customer_state == "certified_checkout")
        if direct_count != expected_direct_checkout_products:
            failures.append(f"expected {expected_direct_checkout_products} certified checkout products, found {direct_count}")

    row_slugs = [row.slug for row in rows]
    duplicate_rows = sorted(slug for slug in set(row_slugs) if row_slugs.count(slug) > 1)
    if duplicate_rows:
        failures.append(f"duplicate repair-map rows: {duplicate_rows}")

    missing_source = sorted(row.slug for row in rows if not row.source_export_found)
    if missing_source:
        failures.append(f"missing Odoo source rows: {missing_source}")
    missing_price = sorted(row.slug for row in rows if row.slug not in price_by_slug)
    if missing_price:
        failures.append(f"missing price-enrichment rows: {missing_price}")

    unscaffolded_source = sorted(set(source_by_slug) - set(row_slugs))
    if unscaffolded_source:
        failures.append(f"Odoo source rows missing scaffold rows: {unscaffolded_source}")

    for row in rows:
        business_values = [row.business_target, row.current_customer_state, row.repair_lane]
        if any("quote" in value.lower() for value in business_values):
            failures.append(f"{row.slug} uses quote terminology in business repair fields")
        if row.current_customer_state != "certified_checkout" and not row.required_next_gates:
            failures.append(f"{row.slug} blocked product missing next gates")
        if row.source_export_found and int(row.price_evidence.get("candidate_units") or 0) <= 0:
            failures.append(f"{row.slug} has source export but no candidate price units")
    return failures


def _by_slug(rows: Any) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        slug = _slug(row)
        if slug:
            result[slug] = row
    return result


def _slug(row: dict[str, Any]) -> str:
    return str(row.get("slug") or "").strip()


def _source_media(source_row: dict[str, Any] | None) -> dict[str, Any]:
    source_row = source_row or {}
    return {
        "primary_image_url": str(source_row.get("image_url") or ""),
        "additional_image_count": len(source_row.get("additional_image_urls") or []),
    }


def _price_evidence(price_row: dict[str, Any] | None) -> dict[str, Any]:
    price_row = price_row or {}
    return {
        "price_status": str(price_row.get("price_status") or "missing"),
        "expected_units": int(price_row.get("expected_units") or 0),
        "candidate_units": int(price_row.get("candidate_units") or 0),
        "source_base_units": int(price_row.get("source_base_units") or 0),
        "source_resolver_units": int(price_row.get("source_resolver_units") or 0),
        "live_snapshot_units": int(price_row.get("live_snapshot_units") or 0),
    }


def _required_next_gates(stage: str, source_found: bool) -> tuple[str, ...]:
    if not source_found:
        return ("repull or repair Odoo product export row",)
    if stage == "direct_checkout_regression_guard":
        return (
            "keep checkout_product_family_contract green",
            "keep post_import_checkout_proof green",
        )
    if stage == "simple_axis_lane_flip_candidate":
        return (
            "Payment Request/Payment Entry cascade proof",
            "receipt/operator/welcome email proof",
            "final owner/product-scope approval before customer exposure",
        )
    if stage == "multi_color_recipe_ui_required":
        return (
            "customer-facing multi-color recipe UI",
            "backend color recipe validation",
            "checkout/payment/invoice/receipt cascade proof",
        )
    if stage == "add_on_or_conditional_pricing_blocked":
        return (
            "explicit add-on or conditional pricing contract",
            "ERPNext price provenance",
            "checkout/payment/invoice/receipt cascade proof",
        )
    return (
        "source export meaning review",
        "backend product type and buying path repair",
        "price/media/checkout proof",
    )


def _notes(scaffold_row: dict[str, Any], price_row: dict[str, Any] | None) -> tuple[str, ...]:
    notes = []
    if str(scaffold_row.get("current_website_lane") or "") == "quote_first":
        notes.append("legacy internal hold state; not a business product lane")
    if price_row and int(price_row.get("live_snapshot_units") or 0):
        notes.append("uses live snapshot price evidence; review provenance before destructive reimport")
    return tuple(notes)


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
