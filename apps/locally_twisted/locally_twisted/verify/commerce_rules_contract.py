"""Contracts for Locally Twisted commerce, delivery, tax, and lane rules."""
from __future__ import annotations


class ContractFail(Exception):
    pass


def run():
    try:
        from locally_twisted import commerce_rules

        failures = []
        failures.extend(_check_delivery_zones(commerce_rules))
        failures.extend(_check_pickup_windows(commerce_rules))
        failures.extend(_check_product_lanes(commerce_rules))
        failures.extend(_check_tax_rates(commerce_rules))
        failures.extend(_check_taxable_item_rules(commerce_rules))
        failures.extend(_check_payment_terms(commerce_rules))

        if failures:
            return {"ok": False, "failures": failures}
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "failures": [f"{type(exc).__name__}: {exc}"]}


def _check_delivery_zones(rules) -> list[str]:
    failures = []
    cases = [
        ("84088", "West Jordan", "standard_delivery", 15.0),
        ("84405", "Riverdale", "standard_delivery", 15.0),
        ("84003", "American Fork", "standard_delivery", 15.0),
        ("84060", "Park City", "park_city_delivery", 50.0),
        ("84068", "Park City", "park_city_delivery", 50.0),
        ("84098", "Park City", "park_city_delivery", 50.0),
        ("84770", "St. George", "out_of_area_quote", None),
        ("84770", "West Jordan", "out_of_area_quote", None),
    ]
    for postal_code, city, expected_zone, expected_fee in cases:
        result = rules.resolve_fulfillment(
            method="delivery",
            postal_code=postal_code,
            city=city,
        )
        if result.zone != expected_zone:
            failures.append(f"{postal_code} expected zone {expected_zone}, found {result.zone}")
        if expected_fee is not None and float(result.delivery_fee) != expected_fee:
            failures.append(
                f"{postal_code} expected delivery fee {expected_fee}, found {result.delivery_fee}"
            )
        if expected_fee is None and result.can_checkout:
            failures.append(f"{postal_code} should be quote-only, not checkout-enabled")
    return failures


def _check_pickup_windows(rules) -> list[str]:
    failures = []
    valid = rules.validate_requested_window("13:00", "13:30")
    if not valid.ok:
        failures.append(f"13:00-13:30 pickup window should be valid: {valid.message}")
    invalid = rules.validate_requested_window("13:00", "14:00")
    if invalid.ok:
        failures.append("13:00-14:00 pickup window should be rejected as not 30 minutes")
    tuesday_pickup = rules.validate_pickup_window(
        pickup_location="West Jordan",
        requested_date="2026-05-26",
        start="12:00",
        end="12:30",
    )
    if not tuesday_pickup.ok:
        failures.append(f"Tuesday 12:00-12:30 pickup window should be valid: {tuesday_pickup.message}")
    monday_pickup = rules.validate_pickup_window(
        pickup_location="West Jordan",
        requested_date="2026-05-25",
        start="12:00",
        end="12:30",
    )
    if monday_pickup.ok:
        failures.append("Monday pickup window should be rejected because pickup is closed")
    early_pickup = rules.validate_pickup_window(
        pickup_location="Riverdale",
        requested_date="2026-05-26",
        start="11:30",
        end="12:00",
    )
    if early_pickup.ok:
        failures.append("11:30 Tuesday pickup should be rejected before opening")
    return failures


def _check_product_lanes(rules) -> list[str]:
    failures = []
    expected = {
        "Bouquets": "retail_checkout",
        "Get-Well Bouquets": "retail_checkout",
        "Grab & Go": "retail_checkout",
        "Deliveries": "retail_checkout",
        "Arches": "retail_checkout",
        "Columns": "retail_checkout",
        "Garlands": "retail_checkout",
        "Drops": "retail_checkout",
    }
    for item_group, lane in expected.items():
        actual = rules.checkout_lane_for_item_group(item_group)
        if actual != lane:
            failures.append(f"{item_group} expected lane {lane}, found {actual}")
    return failures


def _check_tax_rates(rules) -> list[str]:
    failures = []
    expected = [
        ("84088", "West Jordan", 7.45),
        ("84405", "Riverdale", 7.45),
        ("84003", "American Fork", 7.45),
        ("84004", "Alpine", 7.45),
        ("84060", "Park City", 9.55),
        ("84098", "Park City", 9.05),
    ]
    for postal_code, city, rate in expected:
        result = rules.resolve_tax_rate(postal_code=postal_code, city=city)
        if round(float(result.rate), 2) != rate:
            failures.append(f"{postal_code} expected tax {rate}, found {result.rate}")
    for city in sorted(rules.STANDARD_DELIVERY_CITIES):
        try:
            rules.resolve_tax_rate(postal_code="", city=city)
        except ValueError:
            failures.append(f"{city} is a standard delivery city but has no city tax rate")
    return failures


def _check_taxable_item_rules(rules) -> list[str]:
    failures = []
    cases = [
        ("mothers-day-bouquet", "Bouquets", True),
        ("unicorn-bouquet-SMA", "Bouquets", True),
        ("DELIVERY-STANDARD", "Services", False),
        ("DELIVERY-PARK-CITY", "Services", False),
        ("face-painting-deposit", "Services", False),
        ("balloon-twisting-deposit", "Services", False),
    ]
    for item_code, item_group, expected in cases:
        taxable = rules.is_taxable_item(item_code=item_code, item_group=item_group)
        if taxable is not expected:
            failures.append(f"{item_code} in {item_group} expected taxable={expected}, found {taxable}")
    return failures


def _check_payment_terms(rules) -> list[str]:
    failures = []
    artist = rules.payment_rule_for_lane("artist_service", artist_count=2, corporate=False)
    if float(artist.deposit_amount) != 100.0:
        failures.append(f"2 artist services expected $100 deposit, found {artist.deposit_amount}")
    corporate = rules.payment_rule_for_lane("corporate_event", artist_count=0, corporate=True)
    if corporate.payment_timing != "net_30" or float(corporate.deposit_amount) != 0.0:
        failures.append("corporate event should be no-deposit Net 30")
    retail = rules.payment_rule_for_lane("retail_checkout", artist_count=0, corporate=False)
    if retail.payment_timing != "full_upfront":
        failures.append("retail checkout should be full upfront")
    return failures
