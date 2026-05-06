"""Customer policy lane helpers for emails, receipts, and invoice terms."""
from __future__ import annotations

from collections.abc import Iterable


LANE_EVENT_DECOR = "event_decor"
LANE_READY_TO_ORDER = "ready_to_order"
LANE_ARTIST_SERVICE = "artist_service"
LANE_CORPORATE = "corporate"
LANE_GENERAL = "general"


POLICY_LANES = {
    LANE_EVENT_DECOR: {
        "label": "Event balloon decor",
        "terms": "/terms-of-service#event-balloon-decor",
        "refund": "/refund-policy#event-balloon-decor",
        "summary": (
            "Event balloon decor is quote-led. For jobs that require a contract, "
            "payment of the invoice is treated as acceptance of the booking terms "
            "unless a separate written agreement says otherwise. Balloon decor is temporary "
            "and can be affected by weather, heat, cold, wind, sunlight, altitude, venue "
            "conditions, handling, intended use, guest interaction, interference, third-party "
            "movement, and changes after setup."
        ),
    },
    LANE_READY_TO_ORDER: {
        "label": "Ready-to-order pickup and delivery",
        "terms": "/terms-of-service#ready-to-order-pickup-delivery",
        "refund": "/refund-policy#ready-to-order-pickup-delivery",
        "summary": (
            "Pickup and delivery windows are requests until confirmed. Ready-to-order "
            "balloon products are not returnable once they are prepared, delivered, "
            "or picked up. If something arrives damaged, contact us the same day so "
            "we can review it."
        ),
    },
    LANE_ARTIST_SERVICE: {
        "label": "Face painting and balloon twisting",
        "terms": "/terms-of-service#face-painting-balloon-twisting",
        "refund": "/refund-policy#face-painting-balloon-twisting",
        "summary": (
            "Face painting and balloon twisting bookings use a $50 per artist deposit "
            "after availability and scope are confirmed. The remaining balance is due "
            "72 hours before your event. Outdoor events need suitable conditions, and "
            "shade is required for outdoor artist services."
        ),
    },
    LANE_CORPORATE: {
        "label": "Corporate invoicing",
        "terms": "/terms-of-service#corporate-invoicing",
        "refund": "/refund-policy#corporate-invoicing",
        "summary": (
            "Corporate clients are invoiced Net 30 after the event unless we agree otherwise. "
            "If an invoice goes unpaid after day 30, Locally Twisted may add a 10% simple "
            "late fee on the original balance at company discretion."
        ),
    },
    LANE_GENERAL: {
        "label": "General booking and ordering",
        "terms": "/terms-of-service",
        "refund": "/refund-policy",
        "summary": (
            "Submitting a form does not lock in an event date. Your booking is confirmed "
            "when Locally Twisted accepts the job and the required payment or deposit is complete."
        ),
    },
}


def normalize_lanes(lanes: Iterable[str] | None) -> list[str]:
    seen = set()
    normalized: list[str] = []
    for lane in lanes or []:
        if lane not in POLICY_LANES or lane in seen:
            continue
        seen.add(lane)
        normalized.append(lane)
    return normalized or [LANE_GENERAL]


def lanes_for_services(services: Iterable[str] | None) -> list[str]:
    labels = {str(service or "").strip() for service in services or []}
    lanes = []
    if labels & {"Balloon Decor", "Events Inquiry"}:
        lanes.append(LANE_EVENT_DECOR)
    if labels & {"Delivery", "Pickup"}:
        lanes.append(LANE_READY_TO_ORDER)
    if labels & {"Face Painting", "Balloon Twisting"}:
        lanes.append(LANE_ARTIST_SERVICE)
    return normalize_lanes(lanes)


def lanes_for_lead(doc) -> list[str]:
    rows = doc.get("custom_event_type") or []
    labels = []
    for row in rows:
        label = row.get("service_type") or row.get("service_type_name") or row.get("name1")
        if label:
            labels.append(label)
    if not labels and doc.get("custom_services"):
        labels = [part.strip() for part in str(doc.get("custom_services")).split(",")]
    return lanes_for_services(labels)


def customer_policy_block(
    lanes: Iterable[str] | None,
    *,
    include_privacy: bool = False,
    heading: str = "Important policy details",
) -> str:
    normalized = normalize_lanes(lanes)
    items = []
    for lane in normalized:
        spec = POLICY_LANES[lane]
        items.append(
            "<li>"
            f"<strong>{spec['label']}:</strong> {spec['summary']} "
            f"<a href=\"{spec['terms']}\">Terms</a> "
            f"&middot; <a href=\"{spec['refund']}\">Refund policy</a>"
            "</li>"
        )
    privacy = ""
    if include_privacy:
        privacy = '<p style="margin:12px 0 0;"><a href="/privacy">Privacy policy</a></p>'
    return f"""
<div style="background:#FAF7F2; border:1px solid rgba(14,34,64,0.16); border-radius:6px; padding:16px; margin:20px 0;">
  <p style="font-size:13px; font-weight:700; color:#0A0A0B; margin:0 0 8px;">{heading}</p>
  <ul style="font-size:13px; color:#4a4a4a; line-height:1.5; margin:0; padding-left:18px;">
    {''.join(items)}
  </ul>
  {privacy}
</div>
""".strip()
