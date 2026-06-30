#!/usr/bin/env python3
"""Create a targeted read-only local ERPNext product authority snapshot.

Default dry run:
  python scripts/dev/lt_readonly_product_db_snapshot.py --dry-run

Local LT container snapshot:
  python scripts/dev/lt_readonly_product_db_snapshot.py \
    --output /tmp/lt-large-head-missionary-db-snapshot.json

This helper reads through `bench execute frappe.get_all` in the local backend
container. It does not write ERPNext data, clear cache, run migrations, deploy,
or touch provider/payment settings. The only write is the caller-provided local
JSON output file.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONTAINER = "locally-twisted-erpnext-v15-backend-1"
DEFAULT_SITE = "frontend"
DEFAULT_ITEM_CODE = "large-head-missionary"
DEFAULT_ROUTE = "shop-items/bouquets/large-head-missionary"


class SnapshotBlocked(RuntimeError):
    """Raised when a requested action is outside the read-only contract."""


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        enforce_contract(args)
        if args.dry_run:
            print("[LT PRODUCT DB SNAPSHOT] DRY RUN")
            print(f"  container: {args.container}")
            print(f"  site: {args.site}")
            print(f"  item_code: {args.item_code}")
            print(f"  route: {args.route}")
            print("  operations: frappe.get_all reads only")
            return 0
        report = build_snapshot(args)
        write_report(args.output, report)
    except SnapshotBlocked as exc:
        print(f"[LT PRODUCT DB SNAPSHOT] BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[LT PRODUCT DB SNAPSHOT] FAIL: {exc}", file=sys.stderr)
        return 1

    status = "PASS" if not report["failures"] else "FAIL"
    print(f"[LT PRODUCT DB SNAPSHOT] {status}")
    print(f"  output: {Path(args.output).resolve()}")
    print("  mutation: none")
    for failure in report["failures"]:
        print(f"  failure: {failure}")
    return 0 if not report["failures"] else 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--container", default=DEFAULT_CONTAINER, help="Local backend container name")
    parser.add_argument("--site", default=DEFAULT_SITE, help="Local Frappe site name")
    parser.add_argument("--item-code", default=DEFAULT_ITEM_CODE, help="Template item code")
    parser.add_argument("--route", default=DEFAULT_ROUTE, help="Website Item route without leading slash")
    parser.add_argument("--output", help="Caller-provided local JSON output path")
    parser.add_argument("--timeout", type=int, default=120, help="Per-read timeout in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Show planned read-only scope without touching Docker")
    parser.add_argument("--clear-cache", action="store_true", help="Unsupported; included so accidental use fails loudly")
    parser.add_argument("--write-erpnext", action="store_true", help="Unsupported; included so accidental use fails loudly")
    return parser.parse_args(argv)


def enforce_contract(args: argparse.Namespace) -> None:
    if args.clear_cache:
        raise SnapshotBlocked("cache clearing is outside this helper's contract")
    if args.write_erpnext:
        raise SnapshotBlocked("ERPNext writes are outside this helper's contract")
    if not args.dry_run:
        if not args.output:
            raise SnapshotBlocked("--output is required unless --dry-run is used")
        validate_local_output(args.output)


def build_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    failures: list[str] = []
    snapshot: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "read_only": True,
        "container": args.container,
        "site": args.site,
        "item_code": args.item_code,
        "route": args.route,
        "contract": {
            "erpnext_writes": "blocked",
            "cache_clear": "blocked",
            "deploy": "blocked",
            "payment_provider": "blocked",
            "operation": "frappe.get_all reads only",
        },
        "rows": {},
        "failures": failures,
    }

    assert_container_available(args.container)

    website_items = get_all(
        args,
        "Website Item",
        fields=[
            "name",
            "item_code",
            "web_item_name",
            "published",
            "route",
            "item_group",
            "website_image",
            "slideshow",
            "modified",
            "modified_by",
            "owner",
        ],
        filters=[["route", "=", args.route]],
    )
    if not website_items:
        website_items = get_all(
            args,
            "Website Item",
            fields=[
                "name",
                "item_code",
                "web_item_name",
                "published",
                "route",
                "item_group",
                "website_image",
                "slideshow",
                "modified",
                "modified_by",
                "owner",
            ],
            filters=[["item_code", "=", args.item_code]],
        )
    snapshot["rows"]["website_items"] = website_items

    item_codes = {args.item_code}
    website_item_names = {row.get("name") for row in website_items if row.get("name")}
    for row in website_items:
        if row.get("item_code"):
            item_codes.add(row["item_code"])

    template_items = get_all(
        args,
        "Item",
        fields=[
            "name",
            "item_code",
            "item_name",
            "item_group",
            "variant_of",
            "has_variants",
            "disabled",
            "is_sales_item",
            "is_stock_item",
            "image",
            "modified",
            "modified_by",
            "owner",
        ],
        filters=[["item_code", "in", sorted(item_codes)]],
    )
    variants = get_all(
        args,
        "Item",
        fields=[
            "name",
            "item_code",
            "item_name",
            "item_group",
            "variant_of",
            "disabled",
            "is_sales_item",
            "image",
            "modified",
            "modified_by",
        ],
        filters=[["variant_of", "=", args.item_code]],
        order_by="item_code asc",
    )
    snapshot["rows"]["template_items"] = template_items
    snapshot["rows"]["variant_items"] = variants

    all_item_codes = sorted(item_codes | {row["item_code"] for row in variants if row.get("item_code")})
    snapshot["rows"]["item_prices"] = get_all(
        args,
        "Item Price",
        fields=[
            "name",
            "item_code",
            "price_list",
            "price_list_rate",
            "currency",
            "uom",
            "selling",
            "valid_from",
            "valid_upto",
            "modified",
            "modified_by",
        ],
        filters=[["item_code", "in", all_item_codes], ["selling", "=", 1]],
        order_by="item_code asc, price_list asc, name asc",
    )
    snapshot["rows"]["item_variant_attributes"] = get_all(
        args,
        "Item Variant Attribute",
        fields=["name", "parent", "idx", "attribute", "attribute_value", "modified", "modified_by"],
        filters=[["parent", "in", all_item_codes]],
        order_by="parent asc, idx asc",
    )

    blueprints = []
    if doctype_exists(args, "LT Product Blueprint"):
        blueprints = get_all(
            args,
            "LT Product Blueprint",
            fields=[
                "name",
                "product_name",
                "product_slug",
                "item_group",
                "page_template",
                "buying_path",
                "publish_status",
                "shop_visibility",
                "base_price",
                "primary_image",
                "validation_status",
                "ready_for_live",
                "target_item_code",
                "target_website_item",
                "modified",
                "modified_by",
                "owner",
            ],
            filters=[["product_slug", "in", [args.item_code, args.item_code.replace(" ", "-")]]],
            order_by="modified desc",
        )
        target_blueprints = get_all(
            args,
            "LT Product Blueprint",
            fields=[
                "name",
                "product_name",
                "product_slug",
                "item_group",
                "page_template",
                "buying_path",
                "publish_status",
                "shop_visibility",
                "base_price",
                "primary_image",
                "validation_status",
                "ready_for_live",
                "target_item_code",
                "target_website_item",
                "modified",
                "modified_by",
                "owner",
            ],
            filters=[["target_item_code", "=", args.item_code]],
            order_by="modified desc",
        )
        by_name = {row["name"]: row for row in [*blueprints, *target_blueprints] if row.get("name")}
        blueprints = list(by_name.values())
    snapshot["rows"]["product_blueprints"] = blueprints

    blueprint_names = [row["name"] for row in blueprints if row.get("name")]
    for child_doctype, key in [
        ("LT Product Blueprint Price", "product_blueprint_prices"),
        ("LT Product Blueprint Option", "product_blueprint_options"),
        ("LT Product Blueprint Add On", "product_blueprint_add_ons"),
        ("LT Product Blueprint Media Rule", "product_blueprint_media_rules"),
        ("LT Product Blueprint Gallery Image", "product_blueprint_gallery_images"),
        ("LT Product Blueprint Content Rule", "product_blueprint_content_rules"),
    ]:
        if blueprint_names and doctype_exists(args, child_doctype):
            snapshot["rows"][key] = get_all(
                args,
                child_doctype,
                fields=["*"],
                filters=[["parent", "in", blueprint_names]],
                order_by="parent asc, idx asc",
            )
        else:
            snapshot["rows"][key] = []

    slideshow_names = [row.get("slideshow") for row in website_items if row.get("slideshow")]
    snapshot["rows"]["website_slideshows"] = (
        get_all(args, "Website Slideshow", fields=["*"], filters=[["name", "in", slideshow_names]])
        if slideshow_names and doctype_exists(args, "Website Slideshow")
        else []
    )
    snapshot["rows"]["website_slideshow_items"] = (
        get_all(args, "Website Slideshow Item", fields=["*"], filters=[["parent", "in", slideshow_names]], order_by="parent asc, idx asc")
        if slideshow_names and doctype_exists(args, "Website Slideshow Item")
        else []
    )

    file_urls = {
        row.get("website_image")
        for row in website_items
        if row.get("website_image")
    } | {
        row.get("image")
        for row in [*template_items, *variants]
        if row.get("image")
    } | {
        row.get("primary_image")
        for row in blueprints
        if row.get("primary_image")
    }
    file_urls = {url for url in file_urls if url}
    snapshot["rows"]["files_by_url"] = (
        get_all(
            args,
            "File",
            fields=[
                "name",
                "file_name",
                "file_url",
                "is_private",
                "attached_to_doctype",
                "attached_to_name",
                "modified",
                "modified_by",
            ],
            filters=[["file_url", "in", sorted(file_urls)]],
            order_by="file_url asc, name asc",
        )
        if file_urls
        else []
    )
    snapshot["rows"]["files_by_attachment"] = get_all(
        args,
        "File",
        fields=[
            "name",
            "file_name",
            "file_url",
            "is_private",
            "attached_to_doctype",
            "attached_to_name",
            "modified",
            "modified_by",
        ],
        filters=[
            ["attached_to_doctype", "in", ["Item", "Website Item", "LT Product Blueprint"]],
            ["attached_to_name", "in", sorted(set(all_item_codes) | website_item_names | set(blueprint_names))],
        ],
        order_by="attached_to_doctype asc, attached_to_name asc, name asc",
    )

    summarize(snapshot)
    return snapshot


def get_all(
    args: argparse.Namespace,
    doctype: str,
    *,
    fields: list[str],
    filters: list[Any] | None = None,
    order_by: str = "name asc",
) -> list[dict[str, Any]]:
    kwargs: dict[str, Any] = {
        "doctype": doctype,
        "fields": fields,
        "filters": filters or [],
        "order_by": order_by,
        "limit_page_length": 100000,
    }
    return bench_execute(args, "frappe.get_all", kwargs)


def doctype_exists(args: argparse.Namespace, doctype: str) -> bool:
    rows = bench_execute(
        args,
        "frappe.get_all",
        {
            "doctype": "DocType",
            "fields": ["name"],
            "filters": [["name", "=", doctype]],
            "limit_page_length": 1,
        },
    )
    return bool(rows)


def bench_execute(args: argparse.Namespace, method: str, kwargs: dict[str, Any]) -> Any:
    cmd = [
        "docker",
        "exec",
        args.container,
        "bench",
        "--site",
        args.site,
        "execute",
        method,
        "--kwargs",
        json.dumps(kwargs),
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=args.timeout)
    if proc.returncode != 0:
        raise RuntimeError(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return parse_bench_json(proc.stdout)


def parse_bench_json(stdout: str) -> Any:
    text = stdout.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("[")
        if start < 0:
            start = text.find("{")
        if start < 0:
            raise RuntimeError(f"bench output did not contain JSON: {text[:500]}")
        parsed = json.loads(text[start:])
    if isinstance(parsed, str):
        return json.loads(parsed)
    return parsed


def assert_container_available(container: str) -> None:
    proc = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", container],
        text=True,
        capture_output=True,
        timeout=20,
    )
    if proc.returncode != 0:
        raise SnapshotBlocked(f"local backend container is unavailable: {container}")
    if proc.stdout.strip() != "true":
        raise SnapshotBlocked(f"local backend container is not running: {container}")


def summarize(snapshot: dict[str, Any]) -> None:
    rows = snapshot["rows"]
    snapshot["summary"] = {
        "website_items": len(rows.get("website_items") or []),
        "template_items": len(rows.get("template_items") or []),
        "variant_items": len(rows.get("variant_items") or []),
        "item_prices": len(rows.get("item_prices") or []),
        "item_variant_attributes": len(rows.get("item_variant_attributes") or []),
        "product_blueprints": len(rows.get("product_blueprints") or []),
        "files_by_url": len(rows.get("files_by_url") or []),
        "files_by_attachment": len(rows.get("files_by_attachment") or []),
    }
    if not rows.get("website_items"):
        snapshot["failures"].append("Website Item not found by route or item_code")
    if not rows.get("template_items"):
        snapshot["failures"].append("Template Item not found")
    if not rows.get("product_blueprints"):
        snapshot["failures"].append("No Product Setup record found by product_slug or target_item_code")


def validate_local_output(value: str) -> None:
    path = Path(value)
    if "://" in value:
        raise SnapshotBlocked("--output must be a local file path, not a URL")
    if path.exists() and path.is_dir():
        raise SnapshotBlocked("--output must name a JSON file, not a directory")
    if path.suffix.lower() != ".json":
        raise SnapshotBlocked("--output must end in .json")


def write_report(output: str, report: dict[str, Any]) -> None:
    output_path = Path(output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
