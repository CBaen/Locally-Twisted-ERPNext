"""Registry for Locally Twisted outbound document templates.

The registry is metadata only. It gives future generators a stable source of
truth for what documents exist, which records they need, and which review gate
blocks sending.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

REQUIRED_DOCUMENT_IDS = [
    "sales_invoice",
    "payment_receipt",
    "quote_estimate",
    "event_proposal_packet",
    "vendor_setup_w9_packet",
    "statement_of_account",
    "payment_reminder_draft",
    "event_install_work_order",
    "contract_acceptance_summary",
    "post_event_reorder_followup",
]

REQUIRED_FRONTMATTER_KEYS = [
    "id",
    "title",
    "audience",
    "owner",
    "stage",
    "status",
    "automation_ready",
    "trigger",
    "delivery_channel",
    "record_source",
    "policy_lanes",
    "required_fields",
    "do_not_send_without",
    "verification",
    "template_type",
]

REQUIRED_BODY_SECTIONS = [
    "## Audience",
    "## Answer First",
    "## Required Data",
    "## Recipient Outcome",
    "## Automation Notes",
    "## Boundaries",
]


@dataclass(frozen=True)
class OutboundDocumentSpec:
    document_id: str
    title: str
    audience: str
    owner: str
    stage: str
    template_name: str
    record_sources: tuple[str, ...]
    delivery_channels: tuple[str, ...]
    review_gate: str


OUTBOUND_DOCUMENTS: dict[str, OutboundDocumentSpec] = {
    "sales_invoice": OutboundDocumentSpec(
        document_id="sales_invoice",
        title="Sales Invoice",
        audience="Accounts payable and customer bookkeepers",
        owner="Accounting / operations",
        stage="issued_invoice",
        template_name="sales_invoice.md",
        record_sources=("Sales Invoice", "Customer", "Contact", "Address", "Payment Terms Template"),
        delivery_channels=("branded invoice print format", "PDF", "reviewed email"),
        review_gate="Submitted Sales Invoice with approved terms",
    ),
    "payment_receipt": OutboundDocumentSpec(
        document_id="payment_receipt",
        title="Payment Receipt",
        audience="Customer accounting and accounts receivable reconciliation",
        owner="Accounting / operations",
        stage="payment_recorded",
        template_name="payment_receipt.md",
        record_sources=("Payment Entry", "Sales Invoice", "Sales Order", "Customer"),
        delivery_channels=("email body", "PDF when needed"),
        review_gate="Payment Entry or paid Sales Invoice exists",
    ),
    "quote_estimate": OutboundDocumentSpec(
        document_id="quote_estimate",
        title="Quote / Estimate",
        audience="Event buyer, procurement contact, or department coordinator",
        owner="Sales / event planning",
        stage="quote_sent",
        template_name="quote_estimate.md",
        record_sources=("Lead", "Quotation", "Customer", "Item", "Address"),
        delivery_channels=("PDF", "reviewed email"),
        review_gate="Scope, pricing, date, and terms reviewed",
    ),
    "event_proposal_packet": OutboundDocumentSpec(
        document_id="event_proposal_packet",
        title="Event Proposal Packet",
        audience="Corporate buyer, sponsor, venue partner, or executive approver",
        owner="Sales / event planning",
        stage="proposal_review",
        template_name="event_proposal_packet.md",
        record_sources=("Lead", "Quotation", "Portfolio proof", "Customer", "Address"),
        delivery_channels=("PDF packet", "reviewed email"),
        review_gate="Design direction, proof photos, and commercial terms reviewed",
    ),
    "vendor_setup_w9_packet": OutboundDocumentSpec(
        document_id="vendor_setup_w9_packet",
        title="Vendor Setup / W-9 Packet",
        audience="Procurement and accounts payable",
        owner="Accounting / operations",
        stage="vendor_setup",
        template_name="vendor_setup_w9_packet.md",
        record_sources=("Company", "Customer", "Address", "approved W-9 file"),
        delivery_channels=("PDF packet", "secure attachment after review"),
        review_gate="Current W-9 and vendor facts approved by accounting",
    ),
    "statement_of_account": OutboundDocumentSpec(
        document_id="statement_of_account",
        title="Statement Of Account",
        audience="Accounts payable or customer accounting",
        owner="Accounting / operations",
        stage="account_reconciliation",
        template_name="statement_of_account.md",
        record_sources=("Customer", "Sales Invoice", "Payment Entry", "Payment Request"),
        delivery_channels=("PDF", "reviewed email"),
        review_gate="Customer ledger reviewed for date range and open balance",
    ),
    "payment_reminder_draft": OutboundDocumentSpec(
        document_id="payment_reminder_draft",
        title="Payment Reminder Draft",
        audience="Accounts payable or customer payment contact",
        owner="Accounting / operations",
        stage="collections_review",
        template_name="payment_reminder_draft.md",
        record_sources=("Sales Invoice", "Customer", "Contact", "Payment Request"),
        delivery_channels=("draft email only",),
        review_gate="Human approval of recipient, cadence, and copy",
    ),
    "event_install_work_order": OutboundDocumentSpec(
        document_id="event_install_work_order",
        title="Event Install Work Order",
        audience="Venue contact, client day-of contact, and install crew",
        owner="Operations / production",
        stage="event_execution",
        template_name="event_install_work_order.md",
        record_sources=("Sales Order", "Lead", "Customer", "Address", "Item", "Task"),
        delivery_channels=("PDF", "internal print", "reviewed email"),
        review_gate="Install details, venue rules, and weather assumptions reviewed",
    ),
    "contract_acceptance_summary": OutboundDocumentSpec(
        document_id="contract_acceptance_summary",
        title="Contract Acceptance Summary",
        audience="Corporate buyer, procurement, legal, or event owner",
        owner="Sales / accounting",
        stage="booking_acceptance",
        template_name="contract_acceptance_summary.md",
        record_sources=("Quotation", "Sales Order", "Sales Invoice", "Customer"),
        delivery_channels=("PDF", "reviewed email"),
        review_gate="Legal/accounting-approved contract language or accepted invoice terms",
    ),
    "post_event_reorder_followup": OutboundDocumentSpec(
        document_id="post_event_reorder_followup",
        title="Post-event Reorder Follow-up",
        audience="Event buyer, office manager, school admin, or dealership marketing contact",
        owner="Sales / customer success",
        stage="post_event",
        template_name="post_event_reorder_followup.md",
        record_sources=("Sales Order", "Sales Invoice", "Customer", "Lead", "Portfolio proof"),
        delivery_channels=("draft email", "reviewed email"),
        review_gate="Human approval of timing, photos, and next-event suggestion",
    ),
}


def template_path(document_id: str) -> Path:
    return TEMPLATE_DIR / OUTBOUND_DOCUMENTS[document_id].template_name


def load_template(document_id: str) -> str:
    return template_path(document_id).read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields, body


def validate_registry() -> dict[str, object]:
    failures: list[str] = []
    evidence: dict[str, object] = {
        "template_dir": str(TEMPLATE_DIR),
        "document_count": len(OUTBOUND_DOCUMENTS),
        "document_ids": sorted(OUTBOUND_DOCUMENTS),
        "required_document_ids": REQUIRED_DOCUMENT_IDS,
        "templates": {},
    }

    missing_ids = sorted(set(REQUIRED_DOCUMENT_IDS) - set(OUTBOUND_DOCUMENTS))
    extra_ids = sorted(set(OUTBOUND_DOCUMENTS) - set(REQUIRED_DOCUMENT_IDS))
    if missing_ids:
        failures.append("Registry missing required document ids: " + ", ".join(missing_ids))
    if extra_ids:
        failures.append("Registry has unreviewed extra document ids: " + ", ".join(extra_ids))

    if not TEMPLATE_DIR.exists():
        failures.append(f"Template directory is missing: {TEMPLATE_DIR}")
        return {"ok": False, "failures": failures, "evidence": evidence}

    registered_templates = {spec.template_name for spec in OUTBOUND_DOCUMENTS.values()}
    actual_templates = {path.name for path in TEMPLATE_DIR.glob("*.md")}
    stray_templates = sorted(actual_templates - registered_templates)
    if stray_templates:
        failures.append("Template directory has unregistered templates: " + ", ".join(stray_templates))

    for document_id in REQUIRED_DOCUMENT_IDS:
        spec = OUTBOUND_DOCUMENTS.get(document_id)
        if not spec:
            continue
        _validate_document_spec(spec, failures, evidence["templates"])  # type: ignore[index]

    return {
        "ok": not failures,
        "failures": failures,
        "evidence": evidence,
    }


def _validate_document_spec(
    spec: OutboundDocumentSpec,
    failures: list[str],
    template_evidence: dict[str, object],
) -> None:
    path = template_path(spec.document_id)
    doc_evidence: dict[str, object] = {
        "template": spec.template_name,
        "exists": path.exists(),
        "record_sources": list(spec.record_sources),
        "delivery_channels": list(spec.delivery_channels),
        "review_gate": spec.review_gate,
    }
    template_evidence[spec.document_id] = doc_evidence

    if isinstance(spec.record_sources, str):
        failures.append(f"{spec.document_id}: record_sources must be a tuple, not a string")
    if isinstance(spec.delivery_channels, str):
        failures.append(f"{spec.document_id}: delivery_channels must be a tuple, not a string")

    if not path.exists():
        failures.append(f"{spec.document_id}: missing template {path}")
        return

    text = path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    doc_evidence["frontmatter_keys"] = sorted(frontmatter)
    doc_evidence["body_length"] = len(body)

    if not frontmatter:
        failures.append(f"{spec.document_id}: missing frontmatter block")
        return

    for key in REQUIRED_FRONTMATTER_KEYS:
        if not frontmatter.get(key):
            failures.append(f"{spec.document_id}: missing frontmatter key {key}")

    expected = {
        "id": spec.document_id,
        "title": spec.title,
        "audience": spec.audience,
        "owner": spec.owner,
        "stage": spec.stage,
        "template_type": "outbound_markdown_v1",
    }
    for key, expected_value in expected.items():
        actual = frontmatter.get(key)
        if actual != expected_value:
            failures.append(
                f"{spec.document_id}: frontmatter {key} is {actual!r}, expected {expected_value!r}"
            )

    if frontmatter.get("status") != "source_template_ready":
        failures.append(f"{spec.document_id}: status must be source_template_ready")
    if frontmatter.get("automation_ready") != "generator_ready_review_required":
        failures.append(f"{spec.document_id}: automation_ready must be generator_ready_review_required")

    for source in spec.record_sources:
        if source not in frontmatter.get("record_source", ""):
            failures.append(f"{spec.document_id}: frontmatter record_source missing {source}")
    for channel in spec.delivery_channels:
        if channel not in frontmatter.get("delivery_channel", ""):
            failures.append(f"{spec.document_id}: frontmatter delivery_channel missing {channel}")

    if "auto-send" not in body.lower() and "automatic sending" not in body.lower():
        failures.append(f"{spec.document_id}: body must state the no-auto-send boundary")

    for section in REQUIRED_BODY_SECTIONS:
        if section not in body:
            failures.append(f"{spec.document_id}: missing body section {section}")

    answer_index = body.find("## Answer First")
    automation_index = body.find("## Automation Notes")
    if answer_index != -1 and automation_index != -1 and answer_index > automation_index:
        failures.append(f"{spec.document_id}: Answer First must appear before Automation Notes")

    if "{{" not in body or "}}" not in body:
        failures.append(f"{spec.document_id}: template body has no variable placeholders")
