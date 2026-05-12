"""Inquiry upload fail-loud contract.

This verifier submits a fake inquiry with an invalid inspiration file and
proves the customer-facing response plus Lead timeline carry the rejection.
It intercepts commits/logs and rolls the transaction back.
"""
from __future__ import annotations

from io import BytesIO
import inspect
import time

import frappe


class ContractFail(Exception):
    pass


def run() -> dict[str, object]:
    original_commit = frappe.db.commit
    original_log_error = frappe.log_error
    original_form_dict = getattr(frappe.local, "form_dict", None)
    original_request = getattr(frappe, "request", None)
    from locally_twisted.www import book as book_module

    original_deferred_confirmation = book_module._send_deferred_customer_confirmation
    intercepted_commits = []
    log_error_calls = []

    def no_commit(*args, **kwargs):
        intercepted_commits.append(True)

    def fake_log_error(*args, **kwargs):
        log_error_calls.append({"args": args, "kwargs": kwargs})
        return f"ROLLBACK-ERROR-LOG-{len(log_error_calls)}"

    def fake_deferred_confirmation(*args, **kwargs):
        return {"ok": True, "queued": False, "synthetic_upload_contract": True}

    try:
        frappe.db.commit = no_commit
        frappe.log_error = fake_log_error
        book_module._send_deferred_customer_confirmation = fake_deferred_confirmation
        result = _run_contract(log_error_calls)
        result["commit_calls_intercepted"] = len(intercepted_commits)
        result["log_error_calls_intercepted"] = len(log_error_calls)
        result["rolled_back"] = True
        return result
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        frappe.db.commit = original_commit
        frappe.log_error = original_log_error
        book_module._send_deferred_customer_confirmation = original_deferred_confirmation
        if original_form_dict is None:
            frappe.local.form_dict = frappe._dict()
        else:
            frappe.local.form_dict = original_form_dict
        if original_request is None:
            try:
                delattr(frappe, "request")
            except AttributeError:
                pass
        else:
            frappe.request = original_request
        frappe.db.rollback()


def _run_contract(log_error_calls: list[dict[str, object]]) -> dict[str, object]:
    no_photo_result = _assert_empty_upload_slot_is_ignored()
    log_count_before_invalid = len(log_error_calls)
    invalid_result = _assert_invalid_upload_records_failure(log_error_calls)
    invalid_result["empty_upload_slot"] = no_photo_result
    invalid_result["log_error_calls_for_invalid_upload"] = (
        len(log_error_calls) - log_count_before_invalid
    )
    return invalid_result


def _assert_empty_upload_slot_is_ignored() -> dict[str, object]:
    from locally_twisted.www.book import submit_book_inquiry

    token = str(int(time.time()))
    marker = f"LT Empty Upload {token}"
    empty = _FakeFile("", "", b"")

    frappe.local.form_dict = frappe._dict(
        {
            "contact_name": marker,
            "email_from": f"lt-empty-upload-{token}@example.invalid",
            "phone": "801-555-0188",
            "x_services": '["Balloon Twisting"]',
            "description": "Synthetic empty upload slot contract.",
        }
    )
    frappe.request = _FakeRequest([empty])

    response = inspect.unwrap(submit_book_inquiry)()
    upload_summary = response.get("photo_uploads") or {}
    failures = []

    if not response.get("ok"):
        failures.append(f"empty-upload inquiry returned not-ok: {response!r}")
    if response.get("photos") != 0:
        failures.append(f"empty upload should not attach, photos={response.get('photos')!r}")
    if upload_summary.get("submitted") != 0:
        failures.append(f"empty upload should not count as submitted, found {upload_summary.get('submitted')!r}")
    if upload_summary.get("rejected") or upload_summary.get("failed"):
        failures.append(f"empty upload should not create upload issues: {upload_summary!r}")
    if upload_summary.get("customer_message"):
        failures.append("empty upload should not create a customer photo warning")

    if failures:
        raise ContractFail("; ".join(failures))

    return {
        "ok": True,
        "lead": response.get("lead"),
        "photo_uploads": upload_summary,
    }


def _assert_invalid_upload_records_failure(log_error_calls: list[dict[str, object]]) -> dict[str, object]:
    from locally_twisted.failure_recorder import record_health_failures
    from locally_twisted.www.book import submit_book_inquiry

    token = str(int(time.time()))
    marker = f"LT Upload Failure {token}"
    invalid = _FakeFile("not-an-image.txt", "text/plain", b"hello")

    frappe.local.form_dict = frappe._dict(
        {
            "contact_name": marker,
            "email_from": f"lt-upload-failure-{token}@example.invalid",
            "phone": "801-555-0188",
            "x_services": '["Balloon Decor"]',
            "description": "Synthetic invalid upload contract.",
        }
    )
    frappe.request = _FakeRequest([invalid])

    response = inspect.unwrap(submit_book_inquiry)()
    lead_name = response.get("lead")
    upload_summary = response.get("photo_uploads") or {}
    failures = []

    if not response.get("ok"):
        failures.append(f"inquiry submit returned not-ok: {response!r}")
    if response.get("photos") != 0:
        failures.append(f"invalid file should not attach, photos={response.get('photos')!r}")
    if upload_summary.get("submitted") != 1:
        failures.append(f"photo_uploads.submitted expected 1, found {upload_summary.get('submitted')!r}")
    rejected = upload_summary.get("rejected") or []
    if len(rejected) != 1:
        failures.append(f"photo_uploads.rejected expected 1 item, found {rejected!r}")
    elif rejected[0].get("reason") != "unsupported_type":
        failures.append(f"rejection reason expected unsupported_type, found {rejected[0]!r}")
    if not upload_summary.get("customer_message"):
        failures.append("photo_uploads missing customer_message")

    record_rows = record_health_failures(primary_doctype="Lead", primary_name=lead_name, limit=20)
    matching = [
        row for row in record_rows
        if row.get("surface") == "public_contact_to_lead"
        and row.get("step") == "photo_rejected_unsupported_type"
    ]
    if not matching:
        failures.append("Lead record health rows do not include rejected upload evidence")
    if len(log_error_calls) < 1:
        failures.append("upload rejection did not call frappe.log_error through the recorder")

    if failures:
        raise ContractFail("; ".join(failures))

    return {
        "ok": True,
        "lead": lead_name,
        "photo_uploads": upload_summary,
        "record_health_failures": len(record_rows),
    }


class _FakeRequest:
    def __init__(self, files):
        self.files = _FakeFiles(files)


class _FakeFiles:
    def __init__(self, files):
        self._files = files

    def getlist(self, field_name):
        return list(self._files)


class _FakeFile:
    def __init__(self, filename: str, content_type: str, content: bytes):
        self.filename = filename
        self.content_type = content_type
        self.stream = BytesIO(content)

    def read(self):
        return self.stream.read()
