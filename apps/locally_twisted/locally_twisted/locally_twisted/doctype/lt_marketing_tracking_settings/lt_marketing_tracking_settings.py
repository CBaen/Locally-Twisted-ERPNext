"""Validated marketing tracking settings for public website tags."""
from __future__ import annotations

import re
from typing import Any

import frappe
from frappe import _
from frappe.model.document import Document


DEFAULT_GA4_MEASUREMENT_ID = "G-0Z0WY5XQRB"

_GA4_RE = re.compile(r"^G-[A-Z0-9]{4,20}$")
_GTM_RE = re.compile(r"^GTM-[A-Z0-9]{4,20}$")
_GOOGLE_ADS_RE = re.compile(r"^AW-[0-9]{6,20}$")
_META_PIXEL_RE = re.compile(r"^[0-9]{5,32}$")
_CONVERSION_LABEL_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


class LTMarketingTrackingSettings(Document):
    def validate(self) -> None:
        _validate_optional("GA4 Measurement ID", self.ga4_measurement_id, _GA4_RE)
        _validate_optional("GTM Container ID", self.gtm_container_id, _GTM_RE)
        _validate_optional("Google Ads Conversion ID", self.google_ads_conversion_id, _GOOGLE_ADS_RE)
        _validate_optional("Google Ads Purchase Label", self.google_ads_purchase_label, _CONVERSION_LABEL_RE)
        _validate_optional("Google Ads Lead Label", self.google_ads_lead_label, _CONVERSION_LABEL_RE)
        _validate_optional("Meta Pixel ID", self.meta_pixel_id, _META_PIXEL_RE)


def public_tracking_config() -> dict[str, Any]:
    """Return public, non-secret tracking IDs for the browser consent loader."""
    config = {
        "enabled": True,
        "ga4_measurement_id": DEFAULT_GA4_MEASUREMENT_ID,
        "gtm_container_id": "",
        "google_ads_conversion_id": "",
        "google_ads_purchase_label": "",
        "google_ads_lead_label": "",
        "meta_pixel_id": "",
    }

    if not frappe.db.exists("DocType", "LT Marketing Tracking Settings"):
        return config

    try:
        doc = frappe.get_single("LT Marketing Tracking Settings")
    except Exception as exc:
        frappe.log_error(
            title="LT Marketing Tracking Settings",
            message=f"Unable to read public tracking config: {exc}",
        )
        return config

    config.update(
        {
            "enabled": bool(int(doc.enabled or 0)),
            "ga4_measurement_id": _clean(doc.ga4_measurement_id) or DEFAULT_GA4_MEASUREMENT_ID,
            "gtm_container_id": _clean(doc.gtm_container_id),
            "google_ads_conversion_id": _clean(doc.google_ads_conversion_id),
            "google_ads_purchase_label": _clean(doc.google_ads_purchase_label),
            "google_ads_lead_label": _clean(doc.google_ads_lead_label),
            "meta_pixel_id": _clean(doc.meta_pixel_id),
        }
    )
    return config


def _validate_optional(label: str, value: str | None, pattern: re.Pattern[str]) -> None:
    value = _clean(value)
    if not value:
        return
    if not pattern.match(value):
        frappe.throw(_(f"{label} has an invalid format: {value}"), frappe.ValidationError)


def _clean(value: str | None) -> str:
    return str(value or "").strip()
