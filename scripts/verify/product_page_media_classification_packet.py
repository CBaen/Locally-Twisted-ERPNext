#!/usr/bin/env python3
"""Build and verify the source media classification packet.

Run:
  python scripts/verify/product_page_media_classification_packet.py
  python scripts/verify/product_page_media_classification_packet.py --json
  python scripts/verify/product_page_media_classification_packet.py --report output/product-page-media-classification-packet.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

from locally_twisted.catalog_contract.media_classification import build_media_classification_packet


SOURCE_CATALOG = ROOT / "_resources/catalog-source/catalog.json"
SLUG_TO_GROUP = ROOT / "_resources/catalog-source/slug_to_group.json"
DEFAULT_REPORT = ROOT / "audits/catalog-import-audit-2026-05-08/23-product-page-media-classification-packet.json"
DEFAULT_MARKDOWN = ROOT / "audits/catalog-import-audit-2026-05-08/23-product-page-media-classification-packet.md"
EXPECTED_ALLOWED_ROLES = ["primary", "gallery", "variant_image", "reference", "ignored_artifact"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full packet JSON")
    parser.add_argument("--report", help="Write packet JSON to a file")
    parser.add_argument("--markdown", help="Write packet Markdown to a file")
    args = parser.parse_args()

    packet = build_media_classification_packet(_products(), slug_to_group=_slug_to_group())
    failures = _contract_failures(packet)
    rendered = json.dumps(packet, indent=2, sort_keys=True)

    report_path = _rooted(args.report) if args.report else DEFAULT_REPORT
    markdown_path = _rooted(args.markdown) if args.markdown else DEFAULT_MARKDOWN
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(rendered + "\n", encoding="utf-8")
    markdown_path.write_text(_to_markdown(packet), encoding="utf-8")

    print(f"[PRODUCT PAGE MEDIA CLASSIFICATION PACKET] wrote {report_path.relative_to(ROOT)}")
    print(f"[PRODUCT PAGE MEDIA CLASSIFICATION PACKET] wrote {markdown_path.relative_to(ROOT)}")
    if args.json:
        print(rendered)
    else:
        _print_summary(packet, failures)

    return 0 if not failures else 1


def _contract_failures(packet: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if packet.get("allowed_roles") != EXPECTED_ALLOWED_ROLES:
        failures.append(f"packet allowed roles drifted: {packet.get('allowed_roles')}")
    if packet.get("safe_default") != "ignored_artifact":
        failures.append("packet safe default must hold unclassified images as ignored_artifact")
    if packet.get("hold_status") != "hold_until_classified":
        failures.append("packet hold_status must be hold_until_classified")
    if int(packet.get("approved_gallery_count") or 0) <= 0:
        failures.append("packet approved no product gallery media")
    if packet.get("assigned_variant_image_count") != 0:
        failures.append("packet assigned variant images")
    if packet.get("approved_reference_count") != 0:
        failures.append("packet approved reference images")
    if int(packet.get("held_back_ignored_artifact_count") or 0) != 0:
        failures.append("packet held approved product-gallery media as ignored_artifact")
    if packet.get("unsafe_unclassified_image_count") != 0:
        failures.append("packet has unsafe unclassified source extra images")
    if packet.get("unclassified_image_count") != 0:
        failures.append("packet unclassified_image_count should report only unsafe unclassified media")
    if int(packet.get("source_extra_image_count") or 0) <= 0:
        failures.append("packet has no source extra images")
    rows = packet.get("products")
    if not isinstance(rows, list):
        return failures + ["products must be a list"]
    expected_total = sum(len(row.get("images") or []) for row in rows if isinstance(row, dict))
    if expected_total != packet.get("source_extra_image_count"):
        failures.append("source_extra_image_count does not match image rows")
    for row in rows:
        if not isinstance(row, dict):
            failures.append("products contains a non-object row")
            continue
        if int(row.get("extra_image_count") or 0) != len(row.get("images") or []):
            failures.append(f"{row.get('slug')} extra_image_count does not match images list")
        for image in row.get("images") or []:
            if image.get("current_role") != "gallery":
                failures.append(f"{row.get('slug')} image is not approved as gallery")
            if image.get("classification_status") != "approved":
                failures.append(f"{row.get('slug')} image classification_status is not approved")
            if image.get("render_policy") != "render":
                failures.append(f"{row.get('slug')} image render_policy is not render")
            if not image.get("role_reason"):
                failures.append(f"{row.get('slug')} image missing role_reason")
            if image.get("safe_default") != "ignored_artifact":
                failures.append(f"{row.get('slug')} image safe_default is not ignored_artifact")
            if image.get("allowed_roles") != EXPECTED_ALLOWED_ROLES:
                failures.append(f"{row.get('slug')} image missing allowed_roles")
    return failures


def _print_summary(packet: dict[str, Any], failures: list[str]) -> None:
    print("[PRODUCT PAGE MEDIA CLASSIFICATION PACKET] " + ("PASS" if not failures else "FAIL"))
    print(f"  source_products: {packet.get('source_product_count')}")
    print(f"  products_with_extra_images: {packet.get('products_with_extra_images')}")
    print(f"  source_extra_urls: {packet.get('source_extra_url_count')}")
    print(f"  source_extra_images: {packet.get('source_extra_image_count')}")
    print(f"  held_back_ignored_artifacts: {packet.get('held_back_ignored_artifact_count')}")
    print(f"  unsafe_unclassified_images: {packet.get('unsafe_unclassified_image_count')}")
    print(f"  allowed_roles: {packet.get('allowed_roles')}")
    print(f"  safe_default: {packet.get('safe_default')}")
    print(f"  approved_gallery_count: {packet.get('approved_gallery_count')}")
    for row in (packet.get("products") or [])[:8]:
        print(f"  - {row.get('slug')}: {row.get('extra_image_count')} image(s), lane={row.get('commerce_lane_label')}")
    extra = len(packet.get("products") or []) - 8
    if extra > 0:
        print(f"  - ... {extra} more product(s)")
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")


def _to_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Product Page Media Classification Packet",
        "",
        "This packet is source-backed and read-only. It does not upload, move, or delete images.",
        "Approved product-gallery media must project through Product Setup and Website Slideshow.",
        "",
        "## Summary",
        "",
        f"- Source products: {packet.get('source_product_count')}",
        f"- Products with extra images: {packet.get('products_with_extra_images')}",
        f"- Source extra URLs: {packet.get('source_extra_url_count')}",
        f"- Source extra images: {packet.get('source_extra_image_count')}",
        f"- Held-back ignored artifacts: {packet.get('held_back_ignored_artifact_count')}",
        f"- Unsafe unclassified images: {packet.get('unsafe_unclassified_image_count')}",
        f"- Allowed roles: {', '.join(packet.get('allowed_roles') or [])}",
        f"- Safe default role: {packet.get('safe_default')}",
        f"- Approved gallery images: {packet.get('approved_gallery_count')}",
        f"- Assigned variant images: {packet.get('assigned_variant_image_count')}",
        f"- Approved reference images: {packet.get('approved_reference_count')}",
        "",
        "## Product Rows",
        "",
        "| Product | Template | Lane | Extra URLs | Approved gallery images | Safe default |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in packet.get("products") or []:
        lines.append(
            f"| `{row.get('slug')}` {row.get('title')} | {row.get('product_page_type_label')} | "
            f"{row.get('commerce_lane_label')} | {row.get('source_extra_url_count')} | "
            f"{row.get('extra_image_count')} | ignored_artifact for future unclassified media |"
        )
    lines.extend(["", "## Image Rows", ""])
    for row in packet.get("products") or []:
        lines.extend([f"### {row.get('slug')}", ""])
        for image in row.get("images") or []:
            lines.append(
                f"- `{image.get('source_index')}` {image.get('url')} -> "
                f"gallery / approved / render. Reason: {image.get('role_reason')}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _products() -> list[dict[str, Any]]:
    data = json.loads(SOURCE_CATALOG.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return list(data.get("products") or [])
    return list(data or [])


def _slug_to_group() -> dict[str, str]:
    if not SLUG_TO_GROUP.exists():
        return {}
    data = json.loads(SLUG_TO_GROUP.read_text(encoding="utf-8"))
    return {str(key): str(value) for key, value in data.items() if not str(key).startswith("_")}


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
