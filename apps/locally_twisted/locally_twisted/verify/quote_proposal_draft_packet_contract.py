"""Fake-data contract for draft-only quote/proposal packet rendering."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from locally_twisted.paperwork import quote_proposal_draft_packet


FIXED_GENERATED_AT = "2026-05-08T00:00:00"
GUARD_COUNTS = {
    "Quotation": 2,
    "Lead": 12,
    "Customer": 4,
    "Sales Order": 8,
    "Sales Invoice": 1,
    "Payment Request": 8,
    "Email Queue": 30,
    "Communication": 12,
    "File": 0,
    "Comment": 0,
    "Error Log": 0,
}


def run() -> dict[str, object]:
    scenario_specs: list[tuple[str, Callable[[], dict[str, Any]], Callable[[dict[str, Any]], list[str]]]] = [
        ("normal_quote_review_packet", _review_normal_quote, _expect_one_clean_packet),
        ("corporate_proposal_review_packet", _review_corporate_proposal, _expect_proposal_copy),
        ("missing_acceptance_path_blocks_readiness", _review_missing_acceptance_path, _expect_acceptance_blocker),
        ("empty_review_ok", _review_empty, _expect_no_packets),
        ("malformed_send_ready_source_fails", _review_malformed_send_enabled, _expect_malformed_failure),
    ]

    scenarios = []
    failures: list[str] = []
    for scenario_id, review_factory, expectation in scenario_specs:
        result = _render(review_factory())
        scenario_failures = expectation(result)
        scenarios.append(
            {
                "id": scenario_id,
                "passed": not scenario_failures,
                "packet_count": result.get("packet_count"),
                "render_ok": result.get("ok"),
                "failures": scenario_failures,
            }
        )
        failures.extend(f"{scenario_id}: {failure}" for failure in scenario_failures)

    return {
        "ok": not failures,
        "generated_at": FIXED_GENERATED_AT,
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "customer_delivery_enabled": False,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "failures": failures,
    }


def _render(review: dict[str, Any]) -> dict[str, Any]:
    return quote_proposal_draft_packet.render_from_review(
        review,
        guard_counts_before=deepcopy(GUARD_COUNTS),
        guard_counts_after=deepcopy(GUARD_COUNTS),
        generated_at=FIXED_GENERATED_AT,
    )


def _review_normal_quote() -> dict[str, Any]:
    return _review([_candidate("QTN-TEST-0001", "Normal Event Buyer", scope="Graduation balloon arch")])


def _review_corporate_proposal() -> dict[str, Any]:
    return _review(
        [
            _candidate(
                "QTN-TEST-0002",
                "Corporate Events Team",
                scope="Corporate entrance and sponsor photo moment",
                proof_photos="Approved corporate examples pending final selection",
            )
        ]
    )


def _review_missing_acceptance_path() -> dict[str, Any]:
    candidate = _candidate("QTN-TEST-0003", "Procurement Contact", scope="School stage decor")
    for document in candidate["draft_documents"]:
        document["key_fields_to_review"]["acceptance_path"] = ""
        document["send_readiness"]["blocked_send_until"].append("required_field:acceptance_path")
        document["send_readiness"]["send_ready"] = False
        document["send_readiness"]["send_allowed"] = False
    return _review([candidate])


def _review_empty() -> dict[str, Any]:
    return _review([])


def _review_malformed_send_enabled() -> dict[str, Any]:
    candidate = _candidate("QTN-TEST-0004", "Malformed Buyer", scope="Retail display")
    candidate["draft_documents"][0]["send_status"] = "ready_to_send"
    candidate["draft_documents"][0]["send_readiness"]["send_ready"] = True
    return _review([candidate])


def _review(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ok": True,
        "generated_at": FIXED_GENERATED_AT,
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "review_surface": "quotation_review",
        "candidate_count": len(candidates),
        "review_candidates": candidates,
    }


def _candidate(source_name: str, customer_name: str, *, scope: str, proof_photos: str = "Photo use not approved yet") -> dict[str, Any]:
    key_fields = {
        "quote_number": source_name,
        "customer_name": customer_name,
        "event_date": "2026-06-01",
        "event_location": "Ogden, Utah",
        "scope": scope,
        "line_items": "Arch, delivery, install",
        "assumptions": "Indoor install, normal access, no weather exposure",
        "subtotal": "USD 450.00",
        "taxes": "Review tax treatment",
        "total": "USD 450.00",
        "acceptance_path": "Human-reviewed quote acceptance path",
        "event_goal": scope,
        "client_context": customer_name,
        "proof_photos": proof_photos,
        "proposed_scope": scope,
        "venue_assumptions": "Indoor venue access confirmed by human review",
        "investment": "USD 450.00",
        "approval_steps": "Scope, pricing, terms, recipient, and photo-use review",
        "next_event_prompt": "Ask about annual support only after review",
        "recipient": "buyer@example.invalid",
        "company_branding": "Locally Twisted approved quote/proposal branding",
        "payment_terms": "Review payment terms before delivery",
    }
    return {
        "source_doctype": "Quotation",
        "source_name": source_name,
        "customer_name": customer_name,
        "status": "Draft",
        "priority": "proposal_review" if "corporate" in scope.lower() else "quote_review",
        "draft_document_ids": ["quote_estimate", "event_proposal_packet"],
        "draft_documents": [_document("quote_estimate", key_fields), _document("event_proposal_packet", key_fields)],
        "human_review": {"required": True, "send_status": "not_sent"},
    }


def _document(document_id: str, key_fields: dict[str, Any]) -> dict[str, Any]:
    return {
        "document_id": document_id,
        "title": "Quote / Estimate" if document_id == "quote_estimate" else "Event Proposal Packet",
        "audience": "Event buyer, procurement contact, or department coordinator",
        "delivery_channels": ["PDF", "reviewed email"],
        "review_gate": "Human approval of scope, pricing, recipient, terms, and proof-photo use",
        "do_not_send_without": "human_approval | correct_recipient | reviewed_scope | reviewed_pricing | approved_terms_language",
        "automation_ready": "generator_ready_review_required",
        "send_status": "draft_only_not_sent",
        "send_readiness": {
            "send_ready": False,
            "send_allowed": False,
            "blocked_send_until": ["approval_gate:human_approval_recorded"],
        },
        "key_fields_to_review": deepcopy(key_fields),
    }


def _expect_one_clean_packet(result: dict[str, Any]) -> list[str]:
    failures = []
    if result.get("ok") is not True:
        failures.append("expected render_ok true")
    if result.get("packet_count") != 1:
        failures.append(f"expected 1 packet, found {result.get('packet_count')}")
    packet = _first_packet(result)
    if packet and packet.get("send_status") != "draft_only_not_sent":
        failures.append("packet is not draft-only")
    if packet and len(packet.get("sections") or []) != 2:
        failures.append("packet does not have two sections")
    for section in packet.get("sections") or []:
        readiness = section.get("send_readiness") or {}
        if readiness.get("send_ready") is True:
            failures.append(f"{section.get('document_id')} should not be send-ready before review")
    return failures


def _expect_proposal_copy(result: dict[str, Any]) -> list[str]:
    failures = _expect_one_clean_packet(result)
    proposal = _section(result, "event_proposal_packet")
    if "Corporate Events Team" not in (proposal.get("answer_first") or ""):
        failures.append("proposal answer-first copy did not include customer context")
    if "Approved corporate examples" not in (proposal.get("body_preview") or ""):
        failures.append("proposal body did not carry proof-photo review context")
    return failures


def _expect_acceptance_blocker(result: dict[str, Any]) -> list[str]:
    failures = _expect_one_clean_packet(result)
    quote = _section(result, "quote_estimate")
    blockers = quote.get("send_readiness", {}).get("blocked_send_until") or []
    if "required_field:acceptance_path" not in blockers:
        failures.append("quote readiness did not block missing acceptance path")
    return failures


def _expect_no_packets(result: dict[str, Any]) -> list[str]:
    if result.get("ok") is not True:
        return ["empty quote review should render ok"]
    if result.get("packet_count") != 0:
        return [f"expected 0 packets, found {result.get('packet_count')}"]
    return []


def _expect_malformed_failure(result: dict[str, Any]) -> list[str]:
    if result.get("ok") is not False:
        return ["malformed send-ready packet should fail"]
    failures = result.get("failures") or []
    if not any("send-ready" in failure or "draft" in failure.lower() for failure in failures):
        return ["malformed result did not explain draft/send-ready failure"]
    return []


def _first_packet(result: dict[str, Any]) -> dict[str, Any]:
    return (result.get("packets") or [{}])[0]


def _section(result: dict[str, Any], document_id: str) -> dict[str, Any]:
    for packet in result.get("packets") or []:
        for section in packet.get("sections") or []:
            if section.get("document_id") == document_id:
                return section
    return {}
