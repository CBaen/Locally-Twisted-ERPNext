#!/usr/bin/env python3
"""Render fake-data previews for every outbound document template.

Outputs HTML, PDF, PNG, and a review index under:
  output/playwright/outbound-documents-YYYYMMDD/

The fake data is deliberately varied: every document gets a normal case and an
outlier case so copy, layout, bookkeeping fields, and review gates can be
judged before any live automation is wired.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "apps" / "locally_twisted"
OUT_ROOT = ROOT / "output" / "playwright"
DEFAULT_SLUG = f"outbound-documents-{date.today():%Y%m%d}"
LOGO_PATH = (
    ROOT
    / "apps"
    / "locally_twisted"
    / "locally_twisted"
    / "public"
    / "icons"
    / "lt-logo.png"
)


class PreviewFail(Exception):
    pass


class AttrDict(dict):
    """Dict with attribute access for rendering the simple template previews."""

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc


@dataclass(frozen=True)
class Scenario:
    document_id: str
    variant: str
    title: str
    customer: str
    audience: str
    situation: str
    data: dict[str, Any]
    key_facts: tuple[tuple[str, str], ...]
    line_items: tuple[dict[str, str], ...] = ()
    totals: tuple[tuple[str, str], ...] = ()
    review_flags: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    @property
    def slug(self) -> str:
        return f"{self.document_id}-{self.variant}"


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        document_id="sales_invoice",
        variant="normal-school-stage",
        title="Normal Invoice - School Stage Setup",
        customer="Wasatch Elementary PTA",
        audience="PTA treasurer / school bookkeeper",
        situation="A straightforward submitted invoice for a school stage arch and columns.",
        data={
            "invoice": {"name": "ACC-SINV-2026-0042", "po_no": "PTA-SPRING-2026"},
            "customer": {"name": "Wasatch Elementary PTA"},
        },
        key_facts=(
            ("Invoice", "ACC-SINV-2026-0042"),
            ("Due", "May 20, 2026"),
            ("PO / reference", "PTA-SPRING-2026"),
            ("Balance due", "$1,280.00"),
            ("Expense category", "Event decor / balloon services"),
        ),
        line_items=(
            {"name": "Classic stage arch", "qty": "1", "rate": "$850.00", "amount": "$850.00"},
            {"name": "Matching column pair", "qty": "1", "rate": "$300.00", "amount": "$300.00"},
            {"name": "Local delivery and install", "qty": "1", "rate": "$130.00", "amount": "$130.00"},
        ),
        totals=(("Subtotal", "$1,280.00"), ("Tax", "$0.00"), ("Balance due", "$1,280.00")),
        notes=("Black/gray AP layout; no gold, dog-logo, or proposal-style color treatment.",),
    ),
    Scenario(
        document_id="sales_invoice",
        variant="outlier-ihc-net30-po",
        title="Outlier Invoice - Healthcare Net 30 With PO",
        customer="IHC Intermountain HealthCare",
        audience="Corporate accounts payable",
        situation="Large institutional invoice with PO, Net 30 handling, and approved support routing.",
        data={
            "invoice": {"name": "ACC-SINV-2026-0119", "po_no": "IHC-PO-778821"},
            "customer": {"name": "IHC Intermountain HealthCare"},
        },
        key_facts=(
            ("Invoice", "ACC-SINV-2026-0119"),
            ("Due", "June 5, 2026"),
            ("PO / reference", "IHC-PO-778821"),
            ("Payment terms", "Approved Corporate Net 30"),
            ("Balance due", "$7,940.00"),
        ),
        line_items=(
            {"name": "Hospital lobby welcome moment", "qty": "1", "rate": "$2,850.00", "amount": "$2,850.00"},
            {"name": "Stage backdrop balloon wall", "qty": "1", "rate": "$3,600.00", "amount": "$3,600.00"},
            {"name": "Three sponsor table clusters", "qty": "3", "rate": "$330.00", "amount": "$990.00"},
            {"name": "Install, teardown, and delivery", "qty": "1", "rate": "$500.00", "amount": "$500.00"},
        ),
        totals=(("Subtotal", "$7,940.00"), ("Tax", "$0.00"), ("Balance due", "$7,940.00")),
        review_flags=(
            "Confirm corporate terms are approved before sending.",
            "Support routing should use the approved invoice reply copy.",
            "Invoice number and PO must remain on one line.",
        ),
    ),
    Scenario(
        document_id="payment_receipt",
        variant="normal-ready-to-order-paid",
        title="Normal Receipt - Ready-to-order Pickup Paid",
        customer="Megan Carter",
        audience="Customer personal records",
        situation="Simple paid receipt for a ready-to-order pickup.",
        data={
            "payment": {"name": "PAY-2026-0061", "reference_no": "STRIPE-CH-4M1"},
            "invoice": {"name": "ACC-SINV-2026-0061"},
            "sales_order": {"name": "SO-2026-0088"},
        },
        key_facts=(
            ("Receipt", "PAY-2026-0061"),
            ("Paid", "$165.00 on May 6, 2026"),
            ("Related invoice", "ACC-SINV-2026-0061"),
            ("Remaining balance", "$0.00"),
        ),
        line_items=(
            {"name": "Unicorn balloon bouquet", "qty": "1", "rate": "$150.00", "amount": "$150.00"},
            {"name": "Pickup coordination", "qty": "1", "rate": "$15.00", "amount": "$15.00"},
        ),
        totals=(("Amount paid", "$165.00"), ("Remaining balance", "$0.00")),
    ),
    Scenario(
        document_id="payment_receipt",
        variant="outlier-partial-deposit",
        title="Outlier Receipt - Partial Deposit With Remaining Balance",
        customer="Weber State University Alumni",
        audience="Department coordinator and campus accounting",
        situation="Receipt for a deposit only, with a remaining balance and event terms still active.",
        data={
            "payment": {"name": "PAY-2026-0144", "reference_no": "CARD-DEP-9231"},
            "invoice": {"name": "ACC-SINV-2026-0144"},
            "sales_order": {"name": "SO-2026-0190"},
        },
        key_facts=(
            ("Receipt", "PAY-2026-0144"),
            ("Paid", "$1,000.00 deposit"),
            ("Related invoice", "ACC-SINV-2026-0144"),
            ("Remaining balance", "$3,650.00"),
        ),
        totals=(("Invoice total", "$4,650.00"), ("Amount paid", "$1,000.00"), ("Remaining balance", "$3,650.00")),
        review_flags=("Make it unmistakable this is not a paid-in-full receipt.",),
    ),
    Scenario(
        document_id="quote_estimate",
        variant="normal-backyard-patio",
        title="Normal Quote - Backyard Patio Graduation",
        customer="Avery Nelson",
        audience="Family event buyer",
        situation="Straightforward backyard patio estimate with install and teardown assumptions.",
        data={
            "quotation": {"name": "QTN-2026-0037"},
            "customer": {"name": "Avery Nelson"},
        },
        key_facts=(
            ("Quote", "QTN-2026-0037"),
            ("Event date", "May 30, 2026"),
            ("Location", "South Ogden backyard patio"),
            ("Approval path", "Reply approve, then pay deposit"),
        ),
        line_items=(
            {"name": "Organic-look classic garland placeholder", "qty": "16 ft", "rate": "$38.00", "amount": "$608.00"},
            {"name": "Welcome sign cluster", "qty": "1", "rate": "$210.00", "amount": "$210.00"},
            {"name": "Delivery/install/teardown", "qty": "1", "rate": "$175.00", "amount": "$175.00"},
        ),
        totals=(("Estimated total", "$993.00"), ("Deposit due", "$250.00")),
    ),
    Scenario(
        document_id="quote_estimate",
        variant="outlier-weather-access",
        title="Outlier Quote - Outdoor School Event Weather Hold",
        customer="Canyon Ridge High School",
        audience="School activities director",
        situation="Outdoor event quote with shade, wind, and access assumptions that need confirmation.",
        data={
            "quotation": {"name": "QTN-2026-0092"},
            "customer": {"name": "Canyon Ridge High School"},
        },
        key_facts=(
            ("Quote", "QTN-2026-0092"),
            ("Event date", "June 7, 2026"),
            ("Location", "Football field entrance"),
            ("Open issue", "Shade/wind plan required before final install details"),
        ),
        line_items=(
            {"name": "Field entrance arch", "qty": "1", "rate": "$1,250.00", "amount": "$1,250.00"},
            {"name": "Eight table centerpieces", "qty": "8", "rate": "$55.00", "amount": "$440.00"},
            {"name": "Outdoor install labor", "qty": "1", "rate": "$275.00", "amount": "$275.00"},
        ),
        totals=(("Estimated total", "$1,965.00"), ("Deposit due", "$500.00")),
        review_flags=("Final install details must wait for weather and access confirmation.",),
    ),
    Scenario(
        document_id="event_proposal_packet",
        variant="normal-dealership-opening",
        title="Normal Proposal - Car Dealership Grand Opening",
        customer="Mountain View Auto Group",
        audience="General manager and marketing lead",
        situation="Corporate growth proposal with proof, photo moment, and repeat grand-opening support.",
        data={"customer": {"name": "Mountain View Auto Group"}},
        key_facts=(
            ("Event goal", "Celebrate showroom opening and drive photos"),
            ("Hero moment", "Entrance arch plus vehicle photo moment"),
            ("Proof angle", "Dealership and community opening experience"),
            ("Next step", "Approve scope or request branded color pass"),
        ),
        line_items=(
            {"name": "Showroom entrance arch", "qty": "1", "rate": "$1,650.00", "amount": "$1,650.00"},
            {"name": "Vehicle photo moment", "qty": "1", "rate": "$2,400.00", "amount": "$2,400.00"},
            {"name": "Sales desk clusters", "qty": "6", "rate": "$85.00", "amount": "$510.00"},
        ),
        totals=(("Proposal investment", "$4,560.00"),),
        notes=("This preview can use more brand warmth than the invoice.",),
    ),
    Scenario(
        document_id="event_proposal_packet",
        variant="outlier-healthcare-sponsor-review",
        title="Outlier Proposal - Healthcare Sponsor Photo Permissions",
        customer="Intermountain Foundation",
        audience="Foundation director, sponsor lead, and procurement",
        situation="High-visibility healthcare event where proof photos and sponsor marks need extra review.",
        data={"customer": {"name": "Intermountain Foundation"}},
        key_facts=(
            ("Event goal", "Donor recognition and civic celebration"),
            ("Proof angle", "Healthcare, university, and corporate event credibility"),
            ("Sensitive issue", "Sponsor marks and patient-facing photo zones need approval"),
            ("Next step", "Photo/brand permission review before packet send"),
        ),
        line_items=(
            {"name": "Donor entrance installation", "qty": "1", "rate": "$3,200.00", "amount": "$3,200.00"},
            {"name": "Sponsor backdrop", "qty": "1", "rate": "$3,850.00", "amount": "$3,850.00"},
            {"name": "Table carry-through package", "qty": "20", "rate": "$62.00", "amount": "$1,240.00"},
        ),
        totals=(("Proposal investment", "$8,290.00"),),
        review_flags=(
            "Do not imply endorsement from healthcare clients without permission.",
            "Proof photos and sponsor marks require human approval.",
        ),
    ),
    Scenario(
        document_id="vendor_setup_w9_packet",
        variant="normal-weber-vendor",
        title="Normal Vendor Setup - University AP Packet",
        customer="Weber State University",
        audience="University procurement and accounts payable",
        situation="A university needs vendor setup paperwork before issuing a PO.",
        data={"company": {"name": "Locally Twisted"}},
        key_facts=(
            ("Request", "Vendor setup and W-9 routing"),
            ("Remittance contact", "hi@locallytwisted.com"),
            ("Payment terms", "Per approved quote or invoice"),
            ("PO handling", "PO shown on invoice when provided"),
        ),
        review_flags=("Attach only accounting-approved W-9, never a stale local file.",),
    ),
    Scenario(
        document_id="vendor_setup_w9_packet",
        variant="outlier-security-deadline",
        title="Outlier Vendor Setup - Procurement Deadline And Secure Attachment",
        customer="Northern Utah Health Partners",
        audience="Procurement onboarding team",
        situation="Procurement wants same-day W-9 plus insurance contact, but the file needs secure review.",
        data={"company": {"name": "Locally Twisted"}},
        key_facts=(
            ("Request", "W-9, remittance details, insurance contact"),
            ("Deadline", "Same-day procurement portal upload"),
            ("Sensitive issue", "Tax document must be current and approved"),
            ("Fallback", "Send secure link or reviewed attachment only"),
        ),
        review_flags=(
            "Accounting must approve tax form freshness.",
            "Do not send sensitive attachments to unverified recipients.",
        ),
    ),
    Scenario(
        document_id="statement_of_account",
        variant="normal-single-open-invoice",
        title="Normal Statement - One Open Invoice",
        customer="Ogden Downtown Alliance",
        audience="Accounts payable",
        situation="A simple statement showing one unpaid invoice and no disputes.",
        data={"customer": {"name": "Ogden Downtown Alliance"}},
        key_facts=(
            ("Statement date", "May 6, 2026"),
            ("Date range", "April 1 - May 6, 2026"),
            ("Open invoices", "1"),
            ("Total open balance", "$840.00"),
        ),
        line_items=(
            {"name": "ACC-SINV-2026-0087 - Spring market balloons", "qty": "Due May 15", "rate": "$840.00", "amount": "$840.00"},
        ),
        totals=(("Total open balance", "$840.00"),),
    ),
    Scenario(
        document_id="statement_of_account",
        variant="outlier-multiple-credits-dispute",
        title="Outlier Statement - Multiple Invoices, Credit, PO Dispute",
        customer="Wasatch Auto Mall",
        audience="Dealership accounting office",
        situation="Statement includes multiple invoices, one credit, and a PO mismatch note.",
        data={"customer": {"name": "Wasatch Auto Mall"}},
        key_facts=(
            ("Statement date", "May 6, 2026"),
            ("Date range", "January 1 - May 6, 2026"),
            ("Open invoices", "3"),
            ("Credits", "$250.00"),
            ("Total open balance", "$6,430.00"),
        ),
        line_items=(
            {"name": "ACC-SINV-2026-0012 - New model reveal", "qty": "Past due", "rate": "$2,100.00", "amount": "$2,100.00"},
            {"name": "ACC-SINV-2026-0048 - Presidents Day showroom", "qty": "Due May 12", "rate": "$4,580.00", "amount": "$4,580.00"},
            {"name": "Credit memo - duplicate delivery line", "qty": "Applied", "rate": "($250.00)", "amount": "($250.00)"},
        ),
        totals=(("Total open balance", "$6,430.00"),),
        review_flags=("Statement should read like reconciliation, not a demand letter.",),
    ),
    Scenario(
        document_id="payment_reminder_draft",
        variant="normal-friendly-due-soon",
        title="Normal Reminder Draft - Due Soon",
        customer="Davis County Library",
        audience="Accounts payable",
        situation="Draft-only reminder for an invoice due soon.",
        data={"invoice": {"name": "ACC-SINV-2026-0103"}},
        key_facts=(
            ("Invoice", "ACC-SINV-2026-0103"),
            ("Due date", "May 13, 2026"),
            ("Balance due", "$675.00"),
            ("Status", "Draft only - not sent"),
        ),
        review_flags=("Human must approve reminder timing and recipient.",),
    ),
    Scenario(
        document_id="payment_reminder_draft",
        variant="outlier-overdue-disputed-recipient",
        title="Outlier Reminder Draft - Overdue But Recipient Disputed",
        customer="Community Expo Committee",
        audience="Internal accounting review before contacting customer",
        situation="Overdue invoice where the contact may be wrong and payment may be held for PO correction.",
        data={"invoice": {"name": "ACC-SINV-2026-0026"}},
        key_facts=(
            ("Invoice", "ACC-SINV-2026-0026"),
            ("Due date", "April 12, 2026"),
            ("Balance due", "$2,350.00"),
            ("Hold reason", "PO mismatch and old AP contact"),
        ),
        review_flags=(
            "Do not send until recipient is corrected.",
            "Resolve PO mismatch before reminder.",
        ),
    ),
    Scenario(
        document_id="event_install_work_order",
        variant="normal-backyard-install",
        title="Normal Work Order - Backyard Patio Install",
        customer="Avery Nelson",
        audience="Install crew and day-of customer contact",
        situation="Simple backyard graduation install.",
        data={"sales_order": {"name": "SO-2026-0231"}},
        key_facts=(
            ("Event", "Graduation open house"),
            ("Install", "May 30, 2026, 9:00 AM"),
            ("Teardown", "May 30, 2026, 7:00 PM"),
            ("Onsite contact", "Avery Nelson"),
        ),
        line_items=(
            {"name": "Garland at patio rail", "qty": "16 ft", "rate": "White/gold", "amount": "Crew 1"},
            {"name": "Welcome sign cluster", "qty": "1", "rate": "Front walk", "amount": "Crew 1"},
        ),
        notes=("Client-safe version should omit internal margin or labor notes.",),
    ),
    Scenario(
        document_id="event_install_work_order",
        variant="outlier-dealership-showroom",
        title="Outlier Work Order - Dealership Showroom Clearance",
        customer="Wasatch Auto Mall",
        audience="Venue manager, client marketing lead, and install crew",
        situation="Indoor showroom install around vehicles, ceiling limits, and early access.",
        data={"sales_order": {"name": "SO-2026-0279"}},
        key_facts=(
            ("Event", "New model showroom reveal"),
            ("Install", "June 3, 2026, 5:30 AM before sales floor opens"),
            ("Vehicle clearance", "Do not touch vehicles; keep 36 in walkway"),
            ("Open issue", "Confirm ladder/ceiling attachment rules"),
        ),
        line_items=(
            {"name": "Entrance arch", "qty": "1", "rate": "Brand colors", "amount": "Front doors"},
            {"name": "Vehicle photo moment", "qty": "1", "rate": "No vehicle contact", "amount": "Main floor"},
            {"name": "Sales desk clusters", "qty": "6", "rate": "Low profile", "amount": "Desks"},
        ),
        review_flags=("Separate venue-safe notes from internal production notes before sending.",),
    ),
    Scenario(
        document_id="contract_acceptance_summary",
        variant="normal-invoice-acceptance",
        title="Normal Acceptance Summary - Invoice Payment Accepted",
        customer="Canyon Ridge High School",
        audience="School activities director and accounting",
        situation="Summary of accepted scope where invoice payment acts as acceptance under approved terms.",
        data={"customer": {"name": "Canyon Ridge High School"}},
        key_facts=(
            ("Accepted record", "ACC-SINV-2026-0150"),
            ("Accepted amount", "$1,965.00"),
            ("Acceptance date", "May 8, 2026"),
            ("Terms source", "Invoice plus public policy links"),
        ),
        review_flags=("This summarizes accepted records; it is not an attorney-drafted contract.",),
    ),
    Scenario(
        document_id="contract_acceptance_summary",
        variant="outlier-legal-review-pending",
        title="Outlier Acceptance Summary - Legal Review Pending",
        customer="Intermountain Foundation",
        audience="Procurement and legal",
        situation="Large event has accepted commercial scope but separate legal review is still open.",
        data={"customer": {"name": "Intermountain Foundation"}},
        key_facts=(
            ("Accepted record", "QTN-2026-0185"),
            ("Accepted amount", "$8,290.00"),
            ("Pending", "Legal language and sponsor mark usage"),
            ("Send status", "Hold for review"),
        ),
        review_flags=(
            "Do not send as final contract acceptance.",
            "Legal/accounting-approved language required.",
        ),
    ),
    Scenario(
        document_id="post_event_reorder_followup",
        variant="normal-school-repeat",
        title="Normal Follow-up - School Repeat Event",
        customer="Wasatch Elementary PTA",
        audience="PTA chair and school office",
        situation="Friendly post-event follow-up with annual school event prompt.",
        data={"sales_order": {"name": "SO-2026-0214"}},
        key_facts=(
            ("Event", "Spring program"),
            ("Follow-up timing", "Two business days after event"),
            ("Next prompt", "Reserve fall carnival or next year's program"),
            ("Photo use", "Approved decor-only photo"),
        ),
        notes=("This can be warmer and more relationship-focused than accounting documents.",),
    ),
    Scenario(
        document_id="post_event_reorder_followup",
        variant="outlier-no-photo-open-issue",
        title="Outlier Follow-up - No Photo Permission And Open Issue",
        customer="Northern Utah Youth League",
        audience="Internal review before customer follow-up",
        situation="Event completed, but photo permission is not approved and a service issue is unresolved.",
        data={"sales_order": {"name": "SO-2026-0182"}},
        key_facts=(
            ("Event", "Youth awards night"),
            ("Follow-up status", "Draft only"),
            ("Photo use", "No permission; do not attach photos"),
            ("Open issue", "Customer reported one deflated cluster"),
        ),
        review_flags=(
            "Do not send reorder prompt while service issue is open.",
            "Do not include photos or public proof language.",
        ),
    ),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--slug", default=DEFAULT_SLUG, help="Output folder name under output/playwright/")
    parser.add_argument("--no-open", action="store_true", help="Do not print an open command")
    parser.add_argument("--skip-browser", action="store_true", help="Write HTML only; skip PDF/PNG rendering")
    args = parser.parse_args()

    sys.path.insert(0, str(APP_PATH))
    from locally_twisted.outbound_documents.registry import OUTBOUND_DOCUMENTS, parse_frontmatter

    output_dir = (OUT_ROOT / args.slug).resolve()
    if not output_dir.is_relative_to(OUT_ROOT.resolve()):
        raise PreviewFail(f"Refusing to write outside {OUT_ROOT}: {output_dir}")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logo_data_uri = _logo_data_uri()
    rendered: list[dict[str, str]] = []

    for scenario in SCENARIOS:
        spec = OUTBOUND_DOCUMENTS[scenario.document_id]
        template_text = spec.template_name and (Path(spec.template_name))
        template_path = (
            ROOT
            / "apps"
            / "locally_twisted"
            / "locally_twisted"
            / "outbound_documents"
            / "templates"
            / str(template_text)
        )
        frontmatter, body = parse_frontmatter(template_path.read_text(encoding="utf-8"))
        html_text = render_document(spec, frontmatter, body, scenario, logo_data_uri)
        html_path = output_dir / f"{scenario.slug}.html"
        html_path.write_text(html_text, encoding="utf-8")
        rendered.append(
            {
                "document_id": scenario.document_id,
                "variant": scenario.variant,
                "title": scenario.title,
                "customer": scenario.customer,
                "html": html_path.name,
                "pdf": f"{scenario.slug}.pdf",
                "png": f"{scenario.slug}.png",
            }
        )

    index_html = render_index(rendered, logo_data_uri)
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")
    (output_dir / "manifest.json").write_text(json.dumps(rendered, indent=2) + "\n", encoding="utf-8")

    if not args.skip_browser:
        render_browser_artifacts(output_dir, rendered)

    print("[OUTBOUND DOCUMENT PREVIEWS] OK")
    print(f"  output_dir: {output_dir}")
    print(f"  scenarios: {len(rendered)}")
    print(f"  index: {output_dir / 'index.html'}")
    if not args.no_open:
        print(f"  open: {output_dir / 'index.html'}")
    return 0


def render_browser_artifacts(output_dir: Path, rendered: list[dict[str, str]]) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - surfaced as command failure
        raise PreviewFail("playwright is not installed; cannot render PDFs/PNGs") from exc

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1600}, device_scale_factor=1)
        for item in rendered:
            html_path = output_dir / item["html"]
            page.goto(html_path.as_uri(), wait_until="networkidle")
            page.pdf(
                path=str(output_dir / item["pdf"]),
                format="Letter",
                print_background=True,
                margin={"top": "0.35in", "right": "0.35in", "bottom": "0.35in", "left": "0.35in"},
            )
            page.screenshot(path=str(output_dir / item["png"]), full_page=True)
        page.goto((output_dir / "index.html").as_uri(), wait_until="networkidle")
        page.screenshot(path=str(output_dir / "index.png"), full_page=True)
        browser.close()


def render_document(spec: Any, frontmatter: dict[str, str], body: str, scenario: Scenario, logo_data_uri: str) -> str:
    rendered_body = render_template_text(body, scenario.data)
    body_html = markdown_to_html(rendered_body)
    variant_kind = "outlier" if scenario.variant.startswith("outlier") else "normal"
    line_table = render_line_items(scenario.line_items)
    totals_table = render_totals(scenario.totals)
    flags_html = render_flags(scenario.review_flags)
    notes_html = render_notes(scenario.notes)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(scenario.title)}</title>
  <style>{BASE_CSS}</style>
</head>
<body>
  <main class="page {variant_kind}">
    {brand_header(logo_data_uri)}
    <section class="doc-title">
      <div>
        <p class="kicker">{escape(spec.title)} preview</p>
        <h1>{escape(scenario.title)}</h1>
        <p>{escape(scenario.situation)}</p>
      </div>
      <div class="status-card">
        <span class="badge {variant_kind}">{variant_kind}</span>
        <strong>Fake review data</strong>
        <span>Not a live customer document</span>
      </div>
    </section>
    <section class="facts-grid">
      <div>
        <p class="section-label">Recipient</p>
        <h2>{escape(scenario.customer)}</h2>
        <p>{escape(scenario.audience)}</p>
      </div>
      <div>
        <p class="section-label">Key fields to review</p>
        {definition_list(scenario.key_facts)}
      </div>
    </section>
    {line_table}
    {totals_table}
    {flags_html}
    {notes_html}
    <section class="template-copy">
      <p class="section-label">Template copy with fake data</p>
      {body_html}
    </section>
  </main>
</body>
</html>"""


def render_index(rendered: list[dict[str, str]], logo_data_uri: str) -> str:
    cards = []
    for item in rendered:
        kind = "outlier" if item["variant"].startswith("outlier") else "normal"
        cards.append(
            f"""
            <article class="index-card {kind}">
              <span class="badge {kind}">{kind}</span>
              <h2>{escape(item["title"])}</h2>
              <p>{escape(item["customer"])}</p>
              <div class="links">
                <a href="{escape(item["html"])}">HTML</a>
                <a href="{escape(item["pdf"])}">PDF</a>
                <a href="{escape(item["png"])}">PNG</a>
              </div>
            </article>
            """
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Locally Twisted Outbound Document Previews</title>
  <style>{BASE_CSS}</style>
</head>
<body>
  <main class="index-page">
    {brand_header(logo_data_uri)}
    <section class="doc-title">
      <div>
        <p class="kicker">Outbound document review</p>
        <h1>Normal and outlier fake-data previews</h1>
        <p>These are generated review artifacts for document design, copy, and automation boundaries. They are not live customer records.</p>
      </div>
      <div class="status-card">
        <strong>{len(rendered)} previews</strong>
        <span>{sum(1 for item in rendered if item["variant"].startswith("outlier"))} outliers</span>
      </div>
    </section>
    <section class="index-grid">
      {''.join(cards)}
    </section>
  </main>
</body>
</html>"""


def brand_header(logo_data_uri: str) -> str:
    logo = f'<img src="{logo_data_uri}" alt="Locally Twisted">' if logo_data_uri else "<strong>Locally Twisted</strong>"
    return f"""
    <header class="brand-header">
      <div class="brand-logo">{logo}</div>
      <div class="brand-contact">
        <strong>Locally Twisted</strong>
        <span>hi@locallytwisted.com</span>
        <span>(801) 285-0860</span>
        <span>locallytwisted.com</span>
      </div>
    </header>
    """


def render_template_text(text: str, context: dict[str, Any]) -> str:
    safe_context = to_attr_dict(context)

    def replace(match: re.Match[str]) -> str:
        expression = match.group(1).strip()
        try:
            value = eval(expression, {"__builtins__": {}}, safe_context)  # noqa: S307 - local preview expressions only
        except Exception:
            value = f"[missing: {expression}]"
        return str(value)

    return re.sub(r"\{\{\s*(.*?)\s*\}\}", replace, text)


def markdown_to_html(text: str) -> str:
    blocks: list[str] = []
    list_items: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            blocks.append("<ul>" + "".join(list_items) + "</ul>")
            list_items.clear()

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            flush_paragraph()
            flush_list()
            continue
        if line.startswith("## "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h3>{inline(line[3:].strip())}</h3>")
        elif line.startswith("- "):
            flush_paragraph()
            list_items.append(f"<li>{inline(line[2:].strip())}</li>")
        else:
            flush_list()
            paragraph.append(line.strip())
    flush_paragraph()
    flush_list()
    return "\n".join(blocks)


def inline(text: str) -> str:
    escaped = escape(text)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)


def definition_list(rows: tuple[tuple[str, str], ...] | list[tuple[str, str]]) -> str:
    items = "\n".join(
        f"<div><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>"
        for label, value in rows
    )
    return f"<dl>{items}</dl>"


def render_line_items(items: tuple[dict[str, str], ...]) -> str:
    if not items:
        return ""
    rows = "\n".join(
        f"""
        <tr>
          <td>{escape(item.get("name", ""))}</td>
          <td>{escape(item.get("qty", ""))}</td>
          <td>{escape(item.get("rate", ""))}</td>
          <td>{escape(item.get("amount", ""))}</td>
        </tr>
        """
        for item in items
    )
    return f"""
    <section>
      <p class="section-label">Line detail</p>
      <table class="items">
        <thead><tr><th>Item / note</th><th>Qty / status</th><th>Rate / detail</th><th>Amount / owner</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    """


def render_totals(totals: tuple[tuple[str, str], ...]) -> str:
    if not totals:
        return ""
    return f"""
    <section class="totals">
      {definition_list(totals)}
    </section>
    """


def render_flags(flags: tuple[str, ...]) -> str:
    if not flags:
        return ""
    items = "".join(f"<li>{escape(flag)}</li>" for flag in flags)
    return f"""
    <section class="review-flags">
      <p class="section-label">Review flags</p>
      <ul>{items}</ul>
    </section>
    """


def render_notes(notes: tuple[str, ...]) -> str:
    if not notes:
        return ""
    items = "".join(f"<li>{escape(note)}</li>" for note in notes)
    return f"""
    <section class="notes">
      <p class="section-label">Notes</p>
      <ul>{items}</ul>
    </section>
    """


def to_attr_dict(value: Any) -> Any:
    if isinstance(value, dict):
        return AttrDict({key: to_attr_dict(item) for key, item in value.items()})
    if isinstance(value, list):
        return [to_attr_dict(item) for item in value]
    return value


def _logo_data_uri() -> str:
    if not LOGO_PATH.exists():
        return ""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


BASE_CSS = """
:root {
  color-scheme: light;
  --ink: #2f2a26;
  --muted: #645d56;
  --rule: #d8d2ca;
  --paper: #fffdf9;
  --soft: #f8f6f2;
  --berry: #8f2534;
  --navy: #0e2240;
  --brass: #b89a5b;
}

* { box-sizing: border-box; }

body {
  background: #ece7df;
  color: var(--ink);
  font-family: Arial, Helvetica, sans-serif;
  font-size: 12px;
  line-height: 1.42;
  margin: 0;
  padding: 28px;
}

.page,
.index-page {
  background: var(--paper);
  margin: 0 auto;
  max-width: 920px;
  min-height: 11in;
  padding: 34px;
}

.brand-header {
  align-items: flex-start;
  border-bottom: 1px solid var(--rule);
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding-bottom: 16px;
}

.brand-logo img {
  display: block;
  height: auto;
  max-width: 245px;
}

.brand-contact {
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-align: right;
}

.doc-title {
  align-items: flex-end;
  border-bottom: 1px solid var(--rule);
  display: flex;
  gap: 24px;
  justify-content: space-between;
  padding: 22px 0 18px;
}

h1,
h2,
h3,
p {
  margin: 0;
}

h1 {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 26px;
  line-height: 1.1;
}

h2 {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 20px;
}

h3 {
  border-top: 1px solid var(--rule);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 17px;
  margin-top: 18px;
  padding-top: 12px;
}

.kicker,
.section-label {
  color: var(--muted);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .12em;
  margin-bottom: 6px;
  text-transform: uppercase;
}

.doc-title p:not(.kicker) {
  color: var(--muted);
  margin-top: 6px;
  max-width: 560px;
}

.status-card {
  background: var(--soft);
  border-left: 3px solid var(--rule);
  min-width: 210px;
  padding: 10px 12px;
}

.status-card strong,
.status-card span {
  display: block;
}

.badge {
  border: 1px solid var(--rule);
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .12em;
  margin-bottom: 8px;
  padding: 4px 7px;
  text-transform: uppercase;
}

.badge.normal { color: var(--navy); }
.badge.outlier { color: var(--berry); border-color: rgba(143,37,52,.35); }

section {
  margin-top: 18px;
}

.facts-grid {
  display: grid;
  gap: 24px;
  grid-template-columns: 1fr 1.35fr;
}

dl {
  display: grid;
  gap: 7px;
  margin: 0;
}

dl div {
  align-items: start;
  border-bottom: 1px solid rgba(216,210,202,.7);
  display: grid;
  gap: 12px;
  grid-template-columns: 150px 1fr;
  padding-bottom: 6px;
}

dt {
  color: var(--muted);
  font-weight: 700;
}

dd {
  margin: 0;
}

table {
  border-collapse: collapse;
  width: 100%;
}

th {
  color: var(--muted);
  font-size: 10px;
  letter-spacing: .08em;
  text-align: left;
  text-transform: uppercase;
}

th,
td {
  border-bottom: 1px solid var(--rule);
  padding: 8px 6px;
  vertical-align: top;
}

td:last-child,
th:last-child {
  text-align: right;
}

.totals {
  display: flex;
  justify-content: flex-end;
}

.totals dl {
  min-width: 310px;
}

.review-flags {
  border-left: 3px solid var(--berry);
  padding-left: 14px;
}

.notes {
  border-left: 3px solid var(--brass);
  padding-left: 14px;
}

ul {
  margin: 8px 0 0 18px;
  padding: 0;
}

li + li {
  margin-top: 4px;
}

.template-copy {
  background: #fff;
  border-top: 2px solid var(--ink);
  margin-top: 22px;
  padding-top: 8px;
}

code {
  background: var(--soft);
  border: 1px solid var(--rule);
  padding: 1px 4px;
}

.index-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.index-card {
  background: #fff;
  border-top: 2px solid var(--rule);
  padding: 14px;
}

.index-card.outlier {
  border-top-color: var(--berry);
}

.index-card h2 {
  font-size: 18px;
}

.links {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

a {
  color: var(--navy);
  font-weight: 700;
}

@media print {
  body {
    background: #fff;
    padding: 0;
  }

  .page,
  .index-page {
    box-shadow: none;
    max-width: none;
    min-height: 0;
    padding: 0;
  }

  a {
    color: var(--ink);
    text-decoration: none;
  }
}
"""


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PreviewFail as exc:
        print(f"[OUTBOUND DOCUMENT PREVIEWS] FAIL\n  - {exc}")
        sys.exit(1)
