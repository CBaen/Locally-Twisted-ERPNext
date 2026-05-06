"""Sync Locally Twisted branded Sales Invoice print output.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_invoice_branding.execute
"""
from __future__ import annotations

import json

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


PRINT_FORMAT_NAME = "Locally Twisted Sales Invoice"
LETTER_HEAD_NAME = "Locally Twisted"


LETTER_HEAD_CONTENT = """
<div style="border-bottom:1px solid #D8D2CA; padding:0 0 14px; margin:0 0 22px;">
  <div style="display:flex; align-items:flex-start; justify-content:space-between;">
    <div style="max-width:360px;">
      <img src="/assets/locally_twisted/icons/lt-logo.png" alt="Locally Twisted" style="display:block; width:260px; max-width:100%; height:auto;">
      <div style="margin-top:8px; color:#111111; font-size:12px; letter-spacing:0.08em; text-transform:uppercase;">
        Balloon decor for Utah events
      </div>
    </div>
    <div style="text-align:right; color:#111111; font-size:12px; line-height:1.55;">
      <strong style="font-size:13px;">Locally Twisted</strong><br>
      <a href="mailto:hi@locallytwisted.com" style="color:#111111; text-decoration:none;">hi@locallytwisted.com</a><br>
      <span style="color:#111111; text-decoration:none;">(801) 285-0860</span><br>
      <a href="https://locallytwisted.com" style="color:#111111; text-decoration:none;">locallytwisted.com</a>
    </div>
  </div>
</div>
""".strip()


PRINT_FORMAT_HTML = """
<div class="lt-invoice">
  <section class="lt-brand-header">
    <div>
      <img src="/assets/locally_twisted/icons/lt-logo.png" alt="Locally Twisted" class="lt-logo">
      <p>Balloon decor for Utah events</p>
    </div>
    <div class="lt-brand-contact">
      <strong>Locally Twisted</strong>
      <span>hi@locallytwisted.com</span>
      <span>(801) 285-0860</span>
      <span>locallytwisted.com</span>
    </div>
  </section>

  <section class="lt-document-title">
    <div>
      <p class="lt-kicker">Sales Invoice</p>
      <h1><span>Invoice</span> <span class="lt-invoice-number">{{ doc.name }}</span></h1>
      <p class="lt-muted">For accounts payable: please use the invoice number and customer name when logging this expense.</p>
    </div>
    <div class="lt-ap-strip lt-callout" aria-label="Invoice summary">
      <table>
        <tbody>
          <tr>
            <th>Invoice date</th>
            <td>{{ doc.get_formatted("posting_date") }}</td>
          </tr>
          <tr>
            <th>Due date</th>
            <td>{{ doc.get_formatted("due_date") if doc.due_date else "Due on receipt" }}</td>
          </tr>
          <tr>
            <th>Status</th>
            <td>{{ doc.status or "Draft" }}</td>
          </tr>
          <tr>
            <th>Balance due</th>
            <td>{{ doc.get_formatted("outstanding_amount") }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="lt-invoice-parties">
    <div>
      <p class="lt-section-label">Bill to</p>
      <h2>{{ doc.customer_name or doc.customer }}</h2>
      {% if doc.contact_display %}
        <p>{{ doc.contact_display }}</p>
      {% endif %}
      {% if doc.address_display %}
        <div class="lt-address">{{ doc.address_display }}</div>
      {% endif %}
    </div>
    <div>
      <p class="lt-section-label">Invoice details</p>
      <table class="lt-detail-table">
        <tbody>
          <tr>
            <th>Invoice</th>
            <td>{{ doc.name }}</td>
          </tr>
          {% if doc.po_no %}
          <tr>
            <th>Purchase order</th>
            <td>{{ doc.po_no }}</td>
          </tr>
          {% endif %}
          <tr>
            <th>PO / reference</th>
            <td>{{ doc.po_no or doc.name }}</td>
          </tr>
          {% if doc.payment_terms_template %}
          <tr>
            <th>Payment terms</th>
            <td>{{ doc.payment_terms_template }}</td>
          </tr>
          {% endif %}
          <tr>
            <th>Expense category</th>
            <td>Event decor / balloon services</td>
          </tr>
          <tr>
            <th>Currency</th>
            <td>{{ doc.currency }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <table class="lt-items">
    <thead>
      <tr>
        <th class="lt-item-name">Item</th>
        <th class="lt-number">Qty</th>
        <th class="lt-number">Rate</th>
        <th class="lt-number">Amount</th>
      </tr>
    </thead>
    <tbody>
      {% for item in doc.items %}
      <tr>
        <td class="lt-item-name">
          <strong>{{ item.item_name or item.item_code }}</strong>
          {% if item.description and item.description != item.item_name %}
            <div class="lt-item-description">{{ item.description }}</div>
          {% endif %}
        </td>
        <td class="lt-number">{{ item.get_formatted("qty") }}{% if item.uom %} {{ item.uom }}{% endif %}</td>
        <td class="lt-number">{{ item.get_formatted("rate", doc) }}</td>
        <td class="lt-number">{{ item.get_formatted("amount", doc) }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <section class="lt-totals">
    <table>
      <tbody>
        <tr>
          <th>Subtotal</th>
          <td>{{ doc.get_formatted("net_total") }}</td>
        </tr>
        {% if doc.total_taxes_and_charges %}
        <tr>
          <th>Taxes and charges</th>
          <td>{{ doc.get_formatted("total_taxes_and_charges") }}</td>
        </tr>
        {% endif %}
        {% if doc.discount_amount %}
        <tr>
          <th>Discount</th>
          <td>{{ doc.get_formatted("discount_amount") }}</td>
        </tr>
        {% endif %}
        <tr class="lt-grand-total">
          <th>Invoice total</th>
          <td>{{ doc.get_formatted("grand_total") }}</td>
        </tr>
        <tr class="lt-balance-row">
          <th>Balance due</th>
          <td>{{ doc.get_formatted("outstanding_amount") }}</td>
        </tr>
      </tbody>
    </table>
  </section>

  {% set outstanding = doc.outstanding_amount or 0 %}
  {% set payment_terms = doc.payment_terms_template or "" %}
  {% set is_paid = outstanding <= 0 %}
  {% set has_corporate_terms = "Corporate" in payment_terms or "Net 30" in payment_terms %}

  <section class="lt-policy-block lt-callout">
    <div>
      {% if is_paid %}
      <p class="lt-section-label">Payment receipt</p>
      <p>Payment has been recorded for this invoice. Keep this receipt for your records.</p>
      <p>Product, service, delivery, weather, install, and refund terms still apply to the order unless a separate written agreement says otherwise.</p>
      {% elif has_corporate_terms %}
      <p class="lt-section-label">Corporate invoicing</p>
      <p>Approved corporate and institutional clients are invoiced Net 30 after the event unless we agree otherwise in writing. If an invoice goes unpaid past Net 30, Locally Twisted may add a 10% simple late fee on the original balance at company discretion.</p>
      <p>For jobs that require a contract, payment of the invoice is treated as acceptance of the booking terms unless a separate written agreement says otherwise.</p>
      {% else %}
      <p class="lt-section-label">Invoice terms</p>
      <p>Payment is due by the due date shown above unless Locally Twisted agrees otherwise in writing.</p>
      <p>For jobs that require a contract, payment of the invoice is treated as acceptance of the booking terms unless a separate written agreement says otherwise.</p>
      {% endif %}
      <p class="lt-policy-links">
        <a href="/terms-of-service#corporate-invoicing">Terms</a>
        <span>&middot;</span>
        <a href="/refund-policy#corporate-invoicing">Refund policy</a>
        <span>&middot;</span>
        <a href="/privacy">Privacy policy</a>
      </p>
    </div>
  </section>

  <section class="lt-payment-note lt-callout">
    <p><strong>For accounts payable:</strong> hi@locallytwisted.com &middot; (801) 285-0860</p>
    <div class="lt-support-banner">
      <p><strong>Customer Service, Continued Event Support, and Repeat Orders:</strong></p>
      <p>Reply to this invoice and we will route the request to the right person.</p>
    </div>
  </section>
</div>
""".strip()


PRINT_FORMAT_CSS = """
.lt-invoice {
  color: #111111;
  font-family: Lato, Arial, sans-serif;
  font-size: 11px;
  line-height: 1.35;
}

@page {
  margin: 0.45in;
}

.print-format .lt-invoice td,
.print-format .lt-invoice th {
  padding: 5px 0 !important;
}

.print-format .lt-invoice p {
  margin: 2px 0 !important;
}

.lt-brand-header {
  align-items: flex-start;
  border-bottom: 1px solid #D8D2CA;
  display: flex;
  justify-content: space-between;
  margin: 0 0 14px;
  padding: 0 0 10px;
}

.lt-logo {
  display: block;
  height: auto;
  max-width: 100%;
  width: 205px;
}

.lt-brand-header p {
  color: #111111;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  margin: 6px 0 0;
  text-transform: uppercase;
}

.lt-brand-contact {
  color: #111111;
  display: flex;
  flex-direction: column;
  font-size: 12px;
  line-height: 1.55;
  text-align: right;
}

.lt-brand-contact strong {
  font-size: 13px;
}

.lt-invoice h1,
.lt-invoice h2 {
  color: #111111;
  font-family: "Cormorant Garamond", Georgia, serif;
  font-weight: 600;
  margin: 0;
}

.lt-invoice h1 {
  font-size: 20px;
  line-height: 1.15;
  white-space: nowrap;
}

.lt-invoice-number {
  white-space: nowrap;
}

.lt-invoice h2 {
  font-size: 22px;
}

.lt-kicker,
.lt-section-label {
  color: #111111;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  margin: 0 0 6px;
  text-transform: uppercase;
}

.lt-muted {
  color: #111111;
  margin: 4px 0 0;
}

.lt-document-title,
.lt-invoice-parties {
  display: flex;
  gap: 24px;
  justify-content: space-between;
}

.lt-document-title {
  align-items: flex-end;
  background: #FFFFFF;
  border-bottom: 1px solid #D8D2CA;
  margin: 0 0 14px;
  padding: 0 0 12px;
}

.lt-callout {
  background: #F5F5F5;
  border-bottom: 0;
  border-left: 3px solid #B8B8B8;
  border-right: 0;
  border-top: 0;
  box-sizing: border-box;
}

.lt-ap-strip {
  flex: 0 0 42%;
  margin: 0;
  padding: 7px 10px 7px 12px;
}

.lt-document-title > div:first-child {
  flex: 1 1 auto;
  max-width: 54%;
}

.lt-document-title .lt-ap-strip {
  max-width: 310px;
}

.lt-ap-strip table {
  border-collapse: collapse;
  width: 100%;
}

.lt-ap-strip th,
.lt-ap-strip td {
  border: 0;
  margin: 0;
  padding: 3px 0 !important;
  text-align: left;
  white-space: nowrap;
}

.lt-ap-strip th {
  color: #111111;
  font-weight: 700;
  padding-right: 18px !important;
  width: 48%;
}

.lt-ap-strip td {
  color: #111111;
  font-weight: 700;
  text-align: right;
}

.lt-invoice-parties {
  border-bottom: 1px solid #D8D2CA;
  margin: 0 0 12px;
  padding: 0 0 12px;
}

.lt-invoice-parties > div {
  flex: 1;
}

.lt-address {
  color: #111111;
  margin-top: 4px;
}

.lt-detail-table {
  border-collapse: collapse;
  margin-left: auto;
  width: 100%;
}

.lt-detail-table th,
.lt-detail-table td {
  border-bottom: 1px solid #D8D2CA;
  padding: 5px 0 !important;
  text-align: left;
}

.lt-detail-table th {
  color: #111111;
  font-weight: 700;
  width: 42%;
}

.lt-detail-table td {
  color: #111111;
  text-align: right;
}

.lt-items {
  border-collapse: collapse;
  margin: 0 0 10px;
  width: 100%;
}

.lt-items thead th {
  background: #111111;
  border: 1px solid #111111;
  color: #FFFFFF;
  font-size: 10px;
  letter-spacing: 0.08em;
  padding: 7px 8px !important;
  text-transform: uppercase;
}

.print-format .lt-invoice .lt-items thead th {
  padding: 8px 12px !important;
}

.print-format .lt-invoice .lt-items thead th:first-child {
  padding-left: 12px !important;
}

.print-format .lt-invoice .lt-items thead th:last-child {
  padding-right: 12px !important;
}

.print-format .lt-invoice .lt-items td {
  padding: 7px 8px !important;
}

.lt-items td {
  border-bottom: 1px solid #D8D2CA;
  padding: 7px 8px !important;
  vertical-align: top;
}

.lt-item-description {
  color: #111111;
  font-size: 11px;
  margin-top: 2px;
}

.lt-number {
  text-align: right;
  white-space: nowrap;
}

.lt-item-name {
  text-align: left;
  width: 54%;
}

.lt-totals {
  display: flex;
  justify-content: flex-end;
  margin: 0 0 10px;
}

.lt-totals table {
  border-collapse: collapse;
  min-width: 300px;
}

.lt-totals th,
.lt-totals td {
  border-bottom: 1px solid #D8D2CA;
  padding: 5px 0 5px 16px !important;
  text-align: right;
}

.lt-totals th {
  color: #111111;
  font-weight: 700;
}

.lt-grand-total th,
.lt-grand-total td,
.lt-balance-row th,
.lt-balance-row td {
  color: #111111;
  font-size: 13px;
  font-weight: 800;
}

.lt-balance-row th,
.lt-balance-row td {
  color: #111111;
}

.lt-policy-block {
  margin: 0 0 8px;
  padding: 7px 9px 7px 12px;
}

.lt-policy-block p {
  color: #111111;
  margin: 0 0 5px;
}

.lt-policy-links {
  margin-bottom: 0 !important;
}

.lt-policy-links a {
  color: #111111;
  font-weight: 700;
  text-decoration: none;
}

.lt-payment-note {
  color: #111111;
  margin-top: 0;
  padding: 7px 10px 0 12px;
}

.lt-payment-note p {
  margin: 0 0 4px;
}

.lt-support-banner {
  background: #111111;
  color: #FFFFFF;
  margin: 7px -10px 0 -12px;
  padding: 8px 10px;
}

.lt-support-banner p {
  color: #FFFFFF;
  margin: 0 0 2px !important;
}

.lt-support-banner strong {
  color: #FFFFFF;
}
""".strip()


def execute() -> str:
    summary = sync()
    frappe.clear_cache(doctype="Sales Invoice")
    frappe.clear_cache()
    frappe.db.commit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def sync() -> dict[str, object]:
    summary = {
        "ensured_letter_head": "unchanged",
        "ensured_print_format": "unchanged",
        "ensured_default_print_format": "unchanged",
    }
    _ensure_letter_head(summary)
    _ensure_print_format(summary)
    _ensure_default_print_format(summary)
    return summary


def _ensure_letter_head(summary: dict[str, object]) -> None:
    fields = {
        "letter_head_name": LETTER_HEAD_NAME,
        "source": "HTML",
        "content": LETTER_HEAD_CONTENT,
        "disabled": 0,
        "is_default": 1,
    }

    if frappe.db.exists("Letter Head", LETTER_HEAD_NAME):
        doc = frappe.get_doc("Letter Head", LETTER_HEAD_NAME)
        changed = _set_fields(doc, fields)
        if changed:
            doc.save(ignore_permissions=True)
            summary["ensured_letter_head"] = "updated"
        return

    doc = frappe.get_doc({"doctype": "Letter Head", "name": LETTER_HEAD_NAME, **fields})
    doc.insert(ignore_permissions=True)
    # Letter Head.before_insert defaults new records to Image; force the intended
    # HTML source in the same sync run so the first run is launch-ready.
    if _set_fields(doc, fields):
        doc.save(ignore_permissions=True)
    summary["ensured_letter_head"] = "created"


def _ensure_print_format(summary: dict[str, object]) -> None:
    fields = {
        "doc_type": "Sales Invoice",
        "module": "Locally Twisted",
        "standard": "No",
        "custom_format": 1,
        "disabled": 0,
        "print_format_type": "Jinja",
        "html": PRINT_FORMAT_HTML,
        "css": PRINT_FORMAT_CSS,
        "font_size": 12,
        "font": "Lato",
        "page_number": "Hide",
        "margin_top": 10,
        "margin_bottom": 10,
        "margin_left": 10,
        "margin_right": 10,
        "line_breaks": 0,
        "show_section_headings": 0,
        "align_labels_right": 0,
        "absolute_value": 0,
        "raw_printing": 0,
    }

    if frappe.db.exists("Print Format", PRINT_FORMAT_NAME):
        doc = frappe.get_doc("Print Format", PRINT_FORMAT_NAME)
        changed = _set_fields(doc, fields)
        if changed:
            doc.save(ignore_permissions=True)
            summary["ensured_print_format"] = "updated"
        return

    doc = frappe.get_doc({"doctype": "Print Format", "name": PRINT_FORMAT_NAME, **fields})
    doc.insert(ignore_permissions=True)
    summary["ensured_print_format"] = "created"


def _ensure_default_print_format(summary: dict[str, object]) -> None:
    name = frappe.db.get_value(
        "Property Setter",
        {
            "doc_type": "Sales Invoice",
            "property": "default_print_format",
        },
        "name",
    )

    if not name:
        make_property_setter(
            "Sales Invoice",
            "",
            "default_print_format",
            PRINT_FORMAT_NAME,
            "Data",
            for_doctype=True,
            validate_fields_for_doctype=False,
            is_system_generated=True,
        )
        summary["ensured_default_print_format"] = "created"
        return

    doc = frappe.get_doc("Property Setter", name)
    fields = {
        "doctype_or_field": "DocType",
        "field_name": None,
        "property": "default_print_format",
        "value": PRINT_FORMAT_NAME,
        "property_type": "Data",
        "is_system_generated": 1,
    }
    changed = _set_fields(doc, fields)
    if changed:
        doc.flags.validate_fields_for_doctype = False
        doc.save(ignore_permissions=True)
        summary["ensured_default_print_format"] = "updated"


def _set_fields(doc, fields: dict[str, object]) -> bool:
    changed = False
    for key, value in fields.items():
        if not _same_value(getattr(doc, key, None), value):
            setattr(doc, key, value)
            changed = True
    return changed


def _same_value(current, desired) -> bool:
    if current in (None, "") and desired in (None, ""):
        return True
    return current == desired
