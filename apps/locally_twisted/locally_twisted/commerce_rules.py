"""Shared Locally Twisted commerce rules.

This module is the single source for checkout lane, fulfillment, delivery fee,
pickup request, tax-rate, and payment-term behavior used by public templates,
checkout code, and verification scripts.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP


PRICE_LIST = "Standard Selling"
DELIVERY_STANDARD_ITEM = "DELIVERY-STANDARD"
DELIVERY_PARK_CITY_ITEM = "DELIVERY-PARK-CITY"
TAX_ACCOUNT_HEAD = "2300 - Duties and Taxes - LT"
NON_TAXABLE_ITEM_TAX_TEMPLATE = "LT Non-Taxable Sales"
NON_TAXABLE_ITEM_CODES = {DELIVERY_STANDARD_ITEM, DELIVERY_PARK_CITY_ITEM}
NON_TAXABLE_ITEM_GROUPS = {"services"}

RETAIL_CHECKOUT_GROUPS = {
    "Bouquets",
    "Deliveries",
    "Get-Well Bouquets",
    "Grab & Go",
    "Seasonal & Specialty",
}
# Product group alone must not make a cart item quote-only. A customer-facing
# quote fallback is a fulfillment rule, currently driven by delivery zone.
QUOTE_REQUIRED_GROUPS = set()

PICKUP_LOCATIONS = {
    "West Jordan": {
        "label": "West Jordan",
        "address_line1": "8969 S 2700 W",
        "city": "West Jordan",
        "state": "UT",
        "postal_code": "84088",
        "tax_rate": Decimal("7.45"),
    },
    "Riverdale": {
        "label": "Riverdale",
        "address_line1": "913 W 4400 S",
        "city": "Riverdale",
        "state": "UT",
        "postal_code": "84405",
        "tax_rate": Decimal("7.45"),
    },
}

PARK_CITY_ZIPS = {"84060", "84068", "84098"}
STANDARD_DELIVERY_ZIPS = {
    # Salt Lake County
    "84020", "84044", "84047", "84065", "84070", "84081", "84084", "84088",
    "84092", "84093", "84094", "84095", "84096", "84101", "84102", "84103",
    "84104", "84105", "84106", "84107", "84108", "84109", "84110", "84111",
    "84112", "84113", "84114", "84115", "84116", "84117", "84118", "84119",
    "84120", "84121", "84123", "84124", "84128", "84129", "84132", "84133",
    "84134", "84138", "84139", "84141", "84143", "84145", "84148", "84150",
    "84151", "84152", "84157", "84158", "84165", "84170", "84171", "84180",
    "84184", "84189", "84190", "84199",
    # Davis County
    "84010", "84014", "84015", "84025", "84037", "84040", "84041", "84054",
    "84056", "84067", "84075", "84087", "84089",
    # Weber County
    "84310", "84315", "84317", "84339", "84401", "84402", "84403", "84404",
    "84405", "84407", "84408", "84409", "84412", "84414", "84415",
    # Utah County
    "84003", "84004", "84005", "84013", "84042", "84043", "84045", "84057",
    "84058", "84059", "84062", "84097", "84601", "84602", "84604", "84605",
    "84606", "84626", "84633", "84651", "84653", "84655", "84660", "84663",
    "84664",
}

STANDARD_DELIVERY_CITIES = {
    "alpine", "american fork", "bountiful", "bluffdale", "centerville",
    "clearfield", "cottonwood heights", "draper", "farmington", "herriman",
    "holladay", "kaysville", "layton", "lehi", "lindon", "magna", "midvale",
    "millcreek", "murray", "north salt lake", "ogden", "orem", "pleasant grove",
    "provo", "riverton", "riverdale", "roy", "salt lake city", "sandy",
    "south jordan", "south ogden", "south salt lake", "spanish fork", "springville",
    "syracuse", "taylorsville", "west bountiful", "west jordan",
    "west valley city", "woods cross",
}

CITY_TAX_RATES = {
    "alta": Decimal("9.05"),
    "alpine": Decimal("7.45"),
    "american fork": Decimal("7.45"),
    "bountiful": Decimal("7.25"),
    "bluffdale": Decimal("7.45"),
    "centerville": Decimal("7.25"),
    "clearfield": Decimal("7.25"),
    "cottonwood heights": Decimal("7.45"),
    "draper": Decimal("7.45"),
    "farmington": Decimal("7.25"),
    "herriman": Decimal("7.45"),
    "holladay": Decimal("7.45"),
    "kaysville": Decimal("7.25"),
    "layton": Decimal("7.25"),
    "lehi": Decimal("7.45"),
    "lindon": Decimal("7.45"),
    "magna": Decimal("7.45"),
    "midvale": Decimal("7.45"),
    "millcreek": Decimal("7.45"),
    "murray": Decimal("7.65"),
    "north salt lake": Decimal("7.25"),
    "ogden": Decimal("7.25"),
    "orem": Decimal("7.45"),
    "park city": Decimal("9.55"),
    "pleasant grove": Decimal("7.45"),
    "provo": Decimal("7.45"),
    "riverdale": Decimal("7.45"),
    "riverton": Decimal("7.45"),
    "roy": Decimal("7.25"),
    "salt lake city": Decimal("8.45"),
    "sandy": Decimal("7.45"),
    "south jordan": Decimal("7.45"),
    "south ogden": Decimal("7.25"),
    "south salt lake": Decimal("7.65"),
    "spanish fork": Decimal("7.45"),
    "springville": Decimal("7.45"),
    "syracuse": Decimal("7.25"),
    "taylorsville": Decimal("7.45"),
    "west bountiful": Decimal("7.25"),
    "west jordan": Decimal("7.45"),
    "west valley city": Decimal("7.45"),
    "woods cross": Decimal("7.25"),
}

ZIP_TAX_RATES = {
    "84060": Decimal("9.55"),
    "84068": Decimal("9.55"),
    "84098": Decimal("9.05"),
    "84088": Decimal("7.45"),
    "84405": Decimal("7.45"),
}


@dataclass(frozen=True)
class FulfillmentResult:
    method: str
    zone: str
    label: str
    delivery_fee: Decimal
    delivery_item_code: str | None
    can_checkout: bool
    message: str


@dataclass(frozen=True)
class WindowValidation:
    ok: bool
    message: str = ""


@dataclass(frozen=True)
class TaxRateResult:
    rate: Decimal
    label: str
    source: str


@dataclass(frozen=True)
class PaymentRule:
    lane: str
    deposit_amount: Decimal
    payment_timing: str
    balance_timing: str
    label: str


def money(value: Decimal | float | int | str) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def normalize_postal_code(postal_code: str | None) -> str:
    return "".join(ch for ch in str(postal_code or "") if ch.isdigit())[:5]


def normalize_city(city: str | None) -> str:
    return " ".join(str(city or "").strip().lower().split())


def checkout_lane_for_item_group(item_group: str | None) -> str:
    return "retail_checkout"


def is_taxable_item(*, item_code: str | None = "", item_group: str | None = "") -> bool:
    if str(item_code or "").strip() in NON_TAXABLE_ITEM_CODES:
        return False
    if normalize_city(item_group) in NON_TAXABLE_ITEM_GROUPS:
        return False
    return True


def resolve_fulfillment(
    *,
    method: str,
    postal_code: str | None = "",
    city: str | None = "",
    pickup_location: str | None = "",
) -> FulfillmentResult:
    clean_method = normalize_city(method).replace(" ", "_")
    if clean_method == "pickup":
        label = pickup_location if pickup_location in PICKUP_LOCATIONS else "Pickup"
        return FulfillmentResult(
            method="pickup",
            zone="pickup",
            label=label,
            delivery_fee=money(0),
            delivery_item_code=None,
            can_checkout=True,
            message="Pickup date and window are requested until confirmed by Locally Twisted.",
        )

    zip5 = normalize_postal_code(postal_code)
    city_key = normalize_city(city)
    if zip5 in PARK_CITY_ZIPS:
        return FulfillmentResult(
            method="delivery",
            zone="park_city_delivery",
            label="Park City Delivery",
            delivery_fee=money(50),
            delivery_item_code=DELIVERY_PARK_CITY_ITEM,
            can_checkout=True,
            message="Park City delivery is added at checkout.",
        )
    if zip5:
        if zip5 in STANDARD_DELIVERY_ZIPS:
            return FulfillmentResult(
                method="delivery",
                zone="standard_delivery",
                label="Standard Delivery",
                delivery_fee=money(15),
                delivery_item_code=DELIVERY_STANDARD_ITEM,
                can_checkout=True,
                message="Standard local delivery is added at checkout.",
            )
        return FulfillmentResult(
            method="delivery",
            zone="out_of_area_quote",
            label="Delivery Quote Needed",
            delivery_fee=money(0),
            delivery_item_code=None,
            can_checkout=False,
            message=(
                "We do not currently have standard delivery set up for this location, "
                "but we would love to talk with you about what you are looking for and how we can help."
            ),
        )
    if city_key in STANDARD_DELIVERY_CITIES:
        return FulfillmentResult(
            method="delivery",
            zone="standard_delivery",
            label="Standard Delivery",
            delivery_fee=money(15),
            delivery_item_code=DELIVERY_STANDARD_ITEM,
            can_checkout=True,
            message="Standard local delivery is added at checkout.",
        )
    return FulfillmentResult(
        method="delivery",
        zone="out_of_area_quote",
        label="Delivery Quote Needed",
        delivery_fee=money(0),
        delivery_item_code=None,
        can_checkout=False,
        message=(
            "We do not currently have standard delivery set up for this location, "
            "but we would love to talk with you about what you are looking for and how we can help."
        ),
    )


def validate_requested_window(start: str | None, end: str | None) -> WindowValidation:
    if not start or not end:
        return WindowValidation(False, "Please choose a requested 30-minute window.")
    try:
        start_time = datetime.strptime(start.strip(), "%H:%M")
        end_time = datetime.strptime(end.strip(), "%H:%M")
    except ValueError:
        return WindowValidation(False, "Requested window must use HH:MM time.")
    if end_time - start_time != timedelta(minutes=30):
        return WindowValidation(False, "Requested windows must be exactly 30 minutes.")
    return WindowValidation(True)


def resolve_tax_rate(*, postal_code: str | None, city: str | None) -> TaxRateResult:
    zip5 = normalize_postal_code(postal_code)
    city_key = normalize_city(city)
    if zip5 in ZIP_TAX_RATES:
        return TaxRateResult(rate=ZIP_TAX_RATES[zip5], label=zip5, source="zip")
    if city_key in CITY_TAX_RATES:
        return TaxRateResult(rate=CITY_TAX_RATES[city_key], label=city or city_key, source="city")
    raise ValueError("Tax rate is not configured for this city/ZIP.")


def payment_rule_for_lane(
    lane: str,
    *,
    artist_count: int = 0,
    corporate: bool = False,
) -> PaymentRule:
    if corporate or lane == "corporate_event":
        return PaymentRule(
            lane="corporate_event",
            deposit_amount=money(0),
            payment_timing="net_30",
            balance_timing="Invoice sent after delivery or event completion.",
            label="Corporate clients are invoiced Net 30.",
        )
    if lane == "artist_service":
        count = max(1, int(artist_count or 1))
        return PaymentRule(
            lane="artist_service",
            deposit_amount=money(50 * count),
            payment_timing="deposit_then_balance",
            balance_timing="Balance due 72 hours before the event.",
            label="$50 per artist deposit, balance due 72 hours before the event.",
        )
    if lane in {"personal_decor", "quote_required"}:
        return PaymentRule(
            lane="personal_decor",
            deposit_amount=money(0),
            payment_timing="full_before_prep",
            balance_timing="Full payment required before prep starts.",
            label="Custom personal decor is paid in full before prep starts.",
        )
    return PaymentRule(
        lane="retail_checkout",
        deposit_amount=money(0),
        payment_timing="full_upfront",
        balance_timing="Paid in full at checkout.",
        label="Ready-to-order checkout is paid in full at order.",
    )


def public_fulfillment_panel(item_group: str | None) -> dict:
    lane = checkout_lane_for_item_group(item_group)
    if lane == "quote_required":
        return {
            "lane": lane,
            "heading": "Quoted event work",
            "body": "This piece starts with a quote so delivery, install, timing, and venue access are planned correctly.",
            "cta_label": "Request a quote",
            "cta_href": "/contact",
        }
    return {
        "lane": lane,
        "heading": "Pickup and delivery",
        "body": (
            "Pickup is requested at checkout. Standard local delivery is $15. "
            "Park City delivery is $50. Out-of-area delivery starts with a quote."
        ),
        "cta_label": "Add to cart",
        "cta_href": "",
    }
