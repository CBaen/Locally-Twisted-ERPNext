"""Disabled-by-default marketing attribution and event envelope helpers."""
from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit

try:
    import frappe
except ImportError:  # pragma: no cover - host-side contract tests run outside bench.
    frappe = None


ATTRIBUTION_FORM_FIELD = "lt_marketing_attribution"
MAX_ATTRIBUTION_VALUE_LENGTH = 180
MAX_ATTRIBUTION_JSON_BYTES = 4096
ALLOWED_ATTRIBUTION_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "gbraid",
    "wbraid",
    "fbclid",
    "landing_path",
    "referrer",
}
SAFE_VALUE_RE = re.compile(r"[^a-zA-Z0-9 _.,:/?&=+#@%~-]+")


def normalize_public_attribution(raw: Any) -> dict[str, str]:
    """Return a small, safe attribution map from a public form payload."""
    if raw in (None, "", {}):
        return {}
    if isinstance(raw, str):
        if len(raw.encode("utf-8")) > MAX_ATTRIBUTION_JSON_BYTES:
            return {}
        try:
            raw = json.loads(raw)
        except (TypeError, ValueError):
            return {}
    if not isinstance(raw, dict):
        return {}

    normalized: dict[str, str] = {}
    for key in ALLOWED_ATTRIBUTION_KEYS:
        value = _safe_attribution_value(raw.get(key))
        if not value:
            continue
        if key in {"landing_path", "referrer"}:
            value = _strip_query_and_fragment(value)
        normalized[key] = value
    return normalized


def build_no_send_event_envelope(
    *,
    event_name: str,
    source_record: str,
    attribution: dict[str, str] | None = None,
    value: float | int | None = None,
    currency: str = "USD",
) -> dict[str, Any]:
    """Build a verifiable event payload without sending it to any platform."""
    event_name = _safe_attribution_value(event_name).replace(" ", "_").lower()
    source_record = _safe_attribution_value(source_record)
    dedupe_prefix = "lead" if event_name in {"generate_lead", "lead"} else event_name
    envelope = {
        "schema_version": "lt-marketing-event-v1",
        "send_enabled": False,
        "event_name": event_name,
        "source_record": source_record,
        "dedupe_id": f"{dedupe_prefix}:{source_record}" if source_record else "",
        "currency": _safe_attribution_value(currency or "USD") or "USD",
        "attribution": dict(attribution or {}),
    }
    if value is not None:
        envelope["value"] = float(value)
    return envelope


def record_lead_attribution_note(lead, attribution: dict[str, str] | None) -> None:
    """Attach safe attribution evidence to a newly-created Lead."""
    attribution = dict(attribution or {})
    if not attribution:
        return
    if frappe is None:
        raise RuntimeError("record_lead_attribution_note requires Frappe")
    event = build_no_send_event_envelope(
        event_name="generate_lead",
        source_record=lead.name,
        attribution=attribution,
    )
    content = (
        "Marketing attribution captured. No platform event was sent.\n\n"
        f"<pre>{frappe.utils.escape_html(json.dumps(event, indent=2, sort_keys=True))}</pre>"
    )
    frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Lead",
            "reference_name": lead.name,
            "content": content,
        }
    ).insert(ignore_permissions=True)


def _safe_attribution_value(value: Any) -> str:
    text = " ".join(str(value or "").split())
    if not text:
        return ""
    text = SAFE_VALUE_RE.sub("", text)
    return text[:MAX_ATTRIBUTION_VALUE_LENGTH].strip()


def _strip_query_and_fragment(value: str) -> str:
    parts = urlsplit(value)
    if parts.scheme or parts.netloc:
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    return (parts.path or value.split("?", 1)[0].split("#", 1)[0])[:MAX_ATTRIBUTION_VALUE_LENGTH]
