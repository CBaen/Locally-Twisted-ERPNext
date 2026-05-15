"""Email body contract for the repeat-email/photo public form verifier."""
from __future__ import annotations

import json
import re
from email import policy
from email.parser import Parser
from html import unescape
from quopri import decodestring
from typing import Any

import frappe

from locally_twisted.communication_copy_policy import BUSINESS_DOCUMENT_COPY
from locally_twisted.lead_cascade import BUSINESS_INQUIRY_SUBJECT_PREFIX, CUSTOMER_EMAIL_NOTE_PREFIX


EMAIL_PREFIX = "lt-repeat-email-photo-"
EMAIL_SUFFIX = "@example.invalid"


def verify_email_delivery(email: str, expected_labels: str | list[str] | None = None) -> dict[str, Any]:
    """Verify current customer and owner emails include the submitted details."""
    _validate_scope(email)
    labels = _as_list(expected_labels)
    lead_names = _lead_names(email=email)
    leads = [frappe.get_doc("Lead", name) for name in lead_names]
    leads.sort(key=lambda lead: (lead.get("creation"), lead.name))

    failures: list[str] = []
    results = []
    if len(leads) != len(labels):
        failures.append(f"expected {len(labels)} verifier leads, found {len(leads)}")

    for index, lead in enumerate(leads):
        label = labels[index] if index < len(labels) else ""
        result = _verify_lead_email_delivery(lead, email=email, expected_label=label)
        failures.extend(result.pop("failures"))
        results.append(result)

    return {
        "ok": not failures,
        "email": email,
        "lead_count": len(leads),
        "leads": results,
        "failures": failures,
    }


def _validate_scope(email: str | None) -> None:
    if not _is_verifier_email(email or ""):
        frappe.throw("Refusing repeat-email/photo email inspection outside verifier email namespace")


def _is_verifier_email(email: str) -> bool:
    return str(email or "").startswith(EMAIL_PREFIX) and str(email or "").endswith(EMAIL_SUFFIX)


def _as_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    raw = str(value)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return [raw]
    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    return [str(parsed)]


def _lead_names(email: str) -> list[str]:
    names: set[str] = set()
    names.update(frappe.get_all("Lead", filters={"email_id": email}, pluck="name", limit_page_length=1000))
    names.update(
        frappe.get_all(
            "Lead",
            filters={"custom_anything_else": ["like", f"%Customer email: {email}%"]},
            pluck="name",
            limit_page_length=1000,
        )
    )
    return sorted(names)


def _verify_lead_email_delivery(lead, *, email: str, expected_label: str) -> dict[str, Any]:
    failures: list[str] = []
    file_rows = _lead_file_rows(lead)
    photo_rows = _lead_photo_rows(lead)
    queue_rows = _current_email_queue_rows(lead)
    inspected = [_inspect_queue_row(row) for row in queue_rows]

    customer_queue = _first_matching_queue(
        inspected,
        recipient=email,
        required_texts=("Here is what we received", "Thanks for choosing Locally Twisted"),
    )
    business_queue = _first_matching_queue(
        inspected,
        recipient=BUSINESS_DOCUMENT_COPY,
        required_texts=(BUSINESS_INQUIRY_SUBJECT_PREFIX, "Customer-submitted details"),
    )

    if not customer_queue:
        failures.append(f"{lead.name} missing current customer confirmation queue for {email}")
    else:
        failures.extend(_customer_email_failures(lead, customer_queue, email=email, expected_label=expected_label))

    if not business_queue:
        failures.append(f"{lead.name} missing current business owner notification queue for {BUSINESS_DOCUMENT_COPY}")
    else:
        failures.extend(
            _business_email_failures(
                lead,
                business_queue,
                email=email,
                expected_label=expected_label,
                expected_files=file_rows,
            )
        )

    failures.extend(_lead_photo_storage_failures(lead, file_rows=file_rows, photo_rows=photo_rows))

    return {
        "lead": lead.name,
        "creation": str(lead.get("creation")),
        "lead_file_count": len(file_rows),
        "lead_photo_table_count": len(photo_rows),
        "customer_queue": _queue_summary(customer_queue),
        "business_queue": _queue_summary(business_queue),
        "current_queue_count": len(inspected),
        "failures": failures,
    }


def _lead_file_rows(lead) -> list[dict[str, Any]]:
    return frappe.get_all(
        "File",
        filters={"attached_to_doctype": "Lead", "attached_to_name": lead.name},
        fields=["name", "file_name", "file_url", "is_private"],
        order_by="creation asc",
        limit_page_length=100,
    )


def _lead_photo_rows(lead) -> list[dict[str, Any]]:
    return [
        {
            "photo": row.get("photo"),
            "caption": row.get("caption"),
        }
        for row in (lead.get("custom_inspiration_photos") or [])
    ]


def _current_email_queue_rows(lead) -> list[dict[str, Any]]:
    filters: dict[str, Any] = {"reference_doctype": "Lead", "reference_name": lead.name}
    if lead.get("creation"):
        filters["creation"] = [">=", lead.get("creation")]
    return frappe.get_all(
        "Email Queue",
        filters=filters,
        fields=["name", "creation", "message", "status", "attachments"],
        order_by="creation asc",
        limit_page_length=100,
    )


def _inspect_queue_row(row: dict[str, Any]) -> dict[str, Any]:
    readable = _readable_message(row.get("message") or "")
    searchable = _searchable_text(readable)
    return {
        "name": row.get("name"),
        "creation": row.get("creation"),
        "status": row.get("status"),
        "recipients": _email_queue_recipients(row.get("name")),
        "subjects": _message_subjects(row.get("message") or ""),
        "attachment_refs": _attachment_refs(row.get("attachments")),
        "attachment_filenames": _attachment_filenames(row.get("message") or ""),
        "searchable": searchable,
    }


def _first_matching_queue(
    inspected: list[dict[str, Any]],
    *,
    recipient: str,
    required_texts: tuple[str, ...],
) -> dict[str, Any] | None:
    normalized_recipient = _normalize_email(recipient)
    for row in inspected:
        if normalized_recipient not in row["recipients"]:
            continue
        haystack = " ".join([row["searchable"], *row["subjects"]])
        if all(_contains_marker(haystack, marker) for marker in required_texts):
            return row
    return None


def _customer_email_failures(lead, row: dict[str, Any], *, email: str, expected_label: str) -> list[str]:
    failures = _missing_marker_failures(
        lead,
        row,
        audience="customer email",
        markers=[
            "Here is what we received",
            "Thanks for choosing Locally Twisted",
            "If anything you submitted appears incorrect",
            "We received 5 files for reference.",
            *_submitted_detail_markers(email=email, expected_label=expected_label),
        ],
    )
    failures.extend(
        _forbidden_marker_failures(
            lead,
            row,
            audience="customer email",
            markers=[
                "A customer submitted this website inquiry",
                "Internal action",
                "Open Lead in desk",
                CUSTOMER_EMAIL_NOTE_PREFIX,
            ],
        )
    )
    if row.get("attachment_refs") or row.get("attachment_filenames"):
        failures.append(
            f"{lead.name} customer email {row['name']} should not include customer photo attachments: "
            f"refs={row.get('attachment_refs') or []}, mime={sorted(row.get('attachment_filenames') or [])}"
        )
    return failures


def _business_email_failures(
    lead,
    row: dict[str, Any],
    *,
    email: str,
    expected_label: str,
    expected_files: list[dict[str, Any]],
) -> list[str]:
    failures = _missing_marker_failures(
        lead,
        row,
        audience="business owner email",
        markers=[
            "Internal action",
            "A customer submitted this website inquiry",
            "Customer-submitted details",
            "Open Lead in desk",
            "5 of 5 attached",
            lead.name,
            *_submitted_detail_markers(email=email, expected_label=expected_label),
        ],
    )
    failures.extend(
        _forbidden_marker_failures(
            lead,
            row,
            audience="business owner email",
            markers=[
                "Thanks for choosing Locally Twisted",
                "If anything you submitted appears incorrect",
                "Here is what we received",
                CUSTOMER_EMAIL_NOTE_PREFIX,
            ],
        )
    )
    expected_file_ids = [file_row.get("name") for file_row in expected_files if file_row.get("name")]
    expected_file_urls = {
        file_row.get("file_url")
        for file_row in expected_files
        if file_row.get("file_url")
    }
    attachment_refs = row.get("attachment_refs") or []
    attachment_fids = [ref.get("fid") for ref in attachment_refs if ref.get("fid")]
    attachment_file_urls = [ref.get("file_url") for ref in attachment_refs if ref.get("file_url")]
    if len(attachment_refs) != len(expected_file_ids):
        failures.append(
            f"{lead.name} business owner email {row['name']} expected {len(expected_file_ids)} "
            f"queued photo attachment ref(s), found {len(attachment_refs)}: {attachment_refs}"
        )
    for file_row in expected_files:
        if file_row.get("name") in attachment_fids:
            continue
        if file_row.get("file_url") in attachment_file_urls:
            continue
        failures.append(
            f"{lead.name} business owner email {row['name']} missing queued photo attachment "
            f"for File {file_row.get('name')!r}"
        )
    for ref in attachment_refs:
        if ref.get("fid"):
            continue
        if ref.get("file_url") in expected_file_urls:
            continue
        if ref.get("print_format_attachment") == 1:
            failures.append(
                f"{lead.name} business owner email {row['name']} includes forbidden print/PDF attachment ref"
            )
            continue
        failures.append(f"{lead.name} business owner email {row['name']} has unexpected attachment ref {ref}")
    return failures


def _lead_photo_storage_failures(
    lead,
    *,
    file_rows: list[dict[str, Any]],
    photo_rows: list[dict[str, Any]],
) -> list[str]:
    failures = []
    if len(file_rows) != 5:
        failures.append(f"{lead.name} expected 5 private Lead File records, found {len(file_rows)}")
    for file_row in file_rows:
        if int(file_row.get("is_private") or 0) != 1:
            failures.append(f"{lead.name} photo File {file_row.get('name')} is not private")
    if len(photo_rows) != len(file_rows):
        failures.append(
            f"{lead.name} expected {len(file_rows)} CRM Inspiration Photos row(s), found {len(photo_rows)}"
        )
    file_urls = {file_row.get("file_url") for file_row in file_rows if file_row.get("file_url")}
    captions = {file_row.get("file_name") for file_row in file_rows if file_row.get("file_name")}
    for row in photo_rows:
        if not row.get("photo"):
            failures.append(f"{lead.name} CRM Inspiration Photos row missing photo value")
        elif row.get("photo") not in file_urls:
            failures.append(
                f"{lead.name} CRM Inspiration Photos row points at unknown file URL {row.get('photo')!r}"
            )
        if row.get("caption") and row.get("caption") not in captions:
            failures.append(
                f"{lead.name} CRM Inspiration Photos row caption {row.get('caption')!r} does not match an uploaded file"
            )
    return failures


def _submitted_detail_markers(*, email: str, expected_label: str) -> list[str]:
    markers = [
        "Repeat Email Photo Test",
        email,
        "(801) 555-0100",
        "Preferred contact method",
        "Text",
        "Test",
        "Birthday Party",
        "2026-06-20",
        "4:00 PM",
        "5:00 PM",
        "Test City",
        "33",
        "Balloon Twisting",
        "Face Painting",
    ]
    if expected_label:
        markers.append(expected_label)
    return markers


def _missing_marker_failures(
    lead,
    row: dict[str, Any],
    *,
    audience: str,
    markers: list[str],
) -> list[str]:
    return [
        f"{lead.name} {audience} {row['name']} missing {marker!r}"
        for marker in markers
        if marker and not _contains_marker(row["searchable"], marker)
    ]


def _forbidden_marker_failures(
    lead,
    row: dict[str, Any],
    *,
    audience: str,
    markers: list[str],
) -> list[str]:
    return [
        f"{lead.name} {audience} {row['name']} contains customer/owner-wrong marker {marker!r}"
        for marker in markers
        if marker and _contains_marker(row["searchable"], marker)
    ]


def _queue_summary(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    return {
        "name": row["name"],
        "creation": str(row["creation"]),
        "status": row.get("status"),
        "recipients": sorted(row["recipients"]),
        "subjects": sorted(row["subjects"]),
        "attachment_refs": row.get("attachment_refs") or [],
        "attachment_filenames": sorted(row.get("attachment_filenames") or []),
    }


def _email_queue_recipients(queue_name: str | None) -> set[str]:
    if not queue_name:
        return set()
    rows = frappe.get_all(
        "Email Queue Recipient",
        filters={"parent": queue_name},
        fields=["recipient"],
    )
    return {
        _normalize_email(row.get("recipient"))
        for row in rows
        if row.get("recipient")
    }


def _readable_message(message: str) -> str:
    pieces = [message or ""]
    try:
        parsed = Parser(policy=policy.default).parsestr(message or "")
        if parsed.is_multipart():
            for part in parsed.walk():
                if part.get_content_maintype() == "text":
                    pieces.append(str(part.get_content()))
        elif parsed.get_content_maintype() == "text":
            pieces.append(str(parsed.get_content()))
    except Exception:
        pass
    for piece in list(pieces):
        try:
            pieces.append(decodestring(piece.encode("utf-8", errors="ignore")).decode("utf-8", errors="ignore"))
        except Exception:
            pass
    return unescape("\n".join(pieces))


def _message_subjects(message: str) -> set[str]:
    subjects = set()
    for line in (message or "").splitlines():
        if line.lower().startswith("subject:"):
            subjects.add(line.split(":", 1)[1].strip())
            break
    try:
        parsed_subject = Parser(policy=policy.default).parsestr(message or "").get("Subject")
        if parsed_subject:
            subjects.add(str(parsed_subject))
    except Exception:
        pass
    return {subject for subject in subjects if subject}


def _attachment_filenames(message: str) -> set[str]:
    filenames: set[str] = set()
    try:
        parsed = Parser(policy=policy.default).parsestr(message or "")
        for part in parsed.walk():
            disposition = (part.get_content_disposition() or "").lower()
            if disposition != "attachment":
                continue
            filename = part.get_filename()
            if filename:
                filenames.add(str(filename))
    except Exception:
        pass
    return filenames


def _attachment_refs(value) -> list[dict[str, Any]]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except Exception as exc:
        return [{"parse_error": str(exc), "raw": str(value)}]
    if not isinstance(parsed, list):
        return [{"unexpected_attachments_shape": type(parsed).__name__, "raw": str(value)}]
    refs: list[dict[str, Any]] = []
    for item in parsed:
        if isinstance(item, dict):
            refs.append(dict(item))
        else:
            refs.append({"unexpected_attachment_ref": str(item)})
    return refs


def _searchable_text(message: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", message or "")
    return re.sub(r"\s+", " ", unescape(without_tags).replace("\xa0", " ")).strip()


def _contains_marker(haystack: str, marker: str) -> bool:
    return marker.lower() in (haystack or "").lower()


def _normalize_email(value) -> str:
    return str(value or "").strip().lower()
