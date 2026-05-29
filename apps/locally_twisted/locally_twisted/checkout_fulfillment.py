"""Line-level fulfillment helpers for LT guest checkout."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from frappe.utils import flt

from locally_twisted import commerce_rules


LINE_FULFILLMENT_FIELDNAMES = {
    "policy": "custom_lt_fulfillment_policy",
    "method": "custom_lt_line_fulfillment_method",
    "zone": "custom_lt_line_fulfillment_zone",
    "note": "custom_lt_line_fulfillment_note",
}


@dataclass(frozen=True)
class CheckoutFulfillmentPlan:
    method: str
    label: str
    delivery: commerce_rules.FulfillmentResult | None
    pickup: commerce_rules.FulfillmentResult | None
    has_delivery_only_lines: bool
    has_pickup_allowed_lines: bool

    @property
    def requires_delivery(self) -> bool:
        return self.delivery is not None

    @property
    def requires_pickup(self) -> bool:
        return self.pickup is not None

    @property
    def can_checkout(self) -> bool:
        return not self.delivery or self.delivery.can_checkout

    @property
    def message(self) -> str:
        return self.delivery.message if self.delivery else self.pickup.message if self.pickup else ""

    @property
    def delivery_fee(self) -> Decimal:
        return self.delivery.delivery_fee if self.delivery else commerce_rules.money(0)

    @property
    def delivery_item_code(self) -> str | None:
        return self.delivery.delivery_item_code if self.delivery else None

    @property
    def zone(self) -> str:
        if self.method == "mixed":
            return "mixed"
        if self.delivery:
            return self.delivery.zone
        if self.pickup:
            return self.pickup.zone
        return ""

    def as_public_dict(self) -> dict:
        return {
            "method": self.method,
            "label": self.label,
            "zone": self.zone,
            "delivery_fee": float(self.delivery_fee),
            "delivery_item_code": self.delivery_item_code,
            "can_checkout": self.can_checkout,
            "message": self.message,
            "has_delivery_only_lines": self.has_delivery_only_lines,
            "has_pickup_allowed_lines": self.has_pickup_allowed_lines,
            "requires_delivery": self.requires_delivery,
            "requires_pickup": self.requires_pickup,
        }


def line_policy_for_item_group(item_group: str | None) -> str:
    return commerce_rules.fulfillment_policy_for_item_group(item_group)


def has_delivery_only_lines(lines: list[dict]) -> bool:
    return any(_is_product_line(line) and line_policy_for_item_group(line.get("item_group")) == "delivery_only" for line in lines)


def has_pickup_allowed_lines(lines: list[dict]) -> bool:
    return any(_is_product_line(line) and line_policy_for_item_group(line.get("item_group")) != "delivery_only" for line in lines)


def build_plan(
    *,
    lines: list[dict],
    requested_method: str,
    pickup_location: str,
    city: str,
    postal_code: str,
) -> CheckoutFulfillmentPlan:
    method = (requested_method or "delivery").strip().lower()
    if method not in {"pickup", "delivery"}:
        method = "delivery"

    delivery_only = has_delivery_only_lines(lines)
    pickup_allowed = has_pickup_allowed_lines(lines)
    requires_delivery = method == "delivery" or delivery_only
    requires_pickup = method == "pickup" and pickup_allowed

    delivery = (
        commerce_rules.resolve_fulfillment(
            method="delivery",
            postal_code=postal_code,
            city=city,
            pickup_location="",
        )
        if requires_delivery
        else None
    )
    pickup = (
        commerce_rules.resolve_fulfillment(
            method="pickup",
            postal_code="",
            city="",
            pickup_location=pickup_location,
        )
        if requires_pickup
        else None
    )

    if requires_delivery and requires_pickup:
        plan_method = "mixed"
        label = "Delivery plus pickup"
    elif requires_delivery:
        plan_method = "delivery"
        label = delivery.label if delivery else "Delivery"
    else:
        plan_method = "pickup"
        label = pickup.label if pickup else "Pickup"

    return CheckoutFulfillmentPlan(
        method=plan_method,
        label=label,
        delivery=delivery,
        pickup=pickup,
        has_delivery_only_lines=delivery_only,
        has_pickup_allowed_lines=pickup_allowed,
    )


def line_method(line: dict, plan: CheckoutFulfillmentPlan) -> str:
    if not _is_product_line(line):
        return "Delivery"
    if line_policy_for_item_group(line.get("item_group")) == "delivery_only":
        return "Delivery"
    if plan.method in {"pickup", "mixed"}:
        return "Pickup"
    return "Delivery"


def tax_context(
    *,
    plan: CheckoutFulfillmentPlan,
    pickup_location: str,
    city: str,
    postal_code: str,
) -> dict[str, commerce_rules.TaxRateResult]:
    context = {}
    if plan.requires_delivery:
        context["Delivery"] = commerce_rules.resolve_tax_rate(postal_code=postal_code, city=city)
    if plan.requires_pickup:
        location = commerce_rules.PICKUP_LOCATIONS[pickup_location]
        context["Pickup"] = commerce_rules.resolve_tax_rate(
            postal_code=location["postal_code"],
            city=location["city"],
        )
    return context


def default_tax(taxes: dict[str, commerce_rules.TaxRateResult]) -> commerce_rules.TaxRateResult:
    if "Delivery" in taxes:
        return taxes["Delivery"]
    return taxes["Pickup"]


def build_totals(
    lines: list[dict],
    plan: CheckoutFulfillmentPlan,
    taxes: dict[str, commerce_rules.TaxRateResult],
) -> dict:
    subtotal = commerce_rules.money(sum(_line_total(row) for row in lines))
    taxable_subtotals_by_rate: dict[Decimal, Decimal] = {}
    for row in lines:
        if not commerce_rules.is_taxable_item(item_code=row.get("item_code"), item_group=row.get("item_group")):
            continue
        method = line_method(row, plan)
        tax = taxes[method]
        line_total = _line_total(row)
        taxable_subtotals_by_rate[tax.rate] = (
            taxable_subtotals_by_rate.get(tax.rate, commerce_rules.money(0)) + line_total
        )
    tax_amount = sum(
        (
            commerce_rules.money(taxable_subtotal * tax_rate / Decimal("100"))
            for tax_rate, taxable_subtotal in taxable_subtotals_by_rate.items()
        ),
        commerce_rules.money(0),
    )
    delivery_fee = commerce_rules.money(plan.delivery_fee)
    total = commerce_rules.money(subtotal + delivery_fee + tax_amount)
    tax = default_tax(taxes)
    return {
        "subtotal": float(subtotal),
        "delivery_fee": float(delivery_fee),
        "tax_rate": float(tax.rate),
        "tax_amount": float(tax_amount),
        "total": float(total),
    }


def _line_total(row: dict) -> Decimal:
    return commerce_rules.money(Decimal(str(flt(row["rate"]))) * Decimal(str(int(row["qty"]))))


def line_fulfillment_note(line: dict, plan: CheckoutFulfillmentPlan) -> str:
    method = line_method(line, plan)
    if method == "Delivery" and line_policy_for_item_group(line.get("item_group")) == "delivery_only":
        return "Delivery only by product category."
    if method == "Delivery":
        return "Customer chose delivery for this line."
    return "Customer chose pickup for pickup-eligible line."


def _is_product_line(line: dict) -> bool:
    item_code = str(line.get("item_code") or "")
    return not item_code.startswith("DELIVERY-")
