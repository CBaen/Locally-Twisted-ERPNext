"""
seed_catalog.py — Idempotent loud-fail bulk import of LT's full live Odoo catalog.

Runs IN-PROCESS via `bench --site frontend execute locally_twisted.seed.seed_catalog.execute`.
In-process is required because:
  - 53 products × avg 200 variants = ~10,800 Item Variant records + Item Price records
  - HTTP RPC at 0.05s each = 1+ hour just for the network. In-process is ~10x faster.
  - We need ItemVariantsCacheManager.rebuild_cache() per template after variants land.

Sources:
  /workspace/_resources/odoo-live/catalog.json     — 53 products from live Odoo scrape
  /workspace/_resources/odoo-live/slug_to_group.json — BBC taxonomy: slug → Item Group child
  /workspace/_resources/odoo-live/value_normalize_map.json — case-fold attribute values
  Container files dir: /workspace/_resources/odoo-live/images/<slug>.png

Behavior — applies to EVERY product:
  1. Find-or-create parent Item with item_group = mapped child.
     - Existing items: re-tag item_group, update item_name, description, image.
     - New items: insert with stock_uom=Nos, is_stock_item=0, is_sales_item=1.
  2. If product has attributes: set has_variants=1, variant_based_on='Item Attribute',
     link Item Attributes via child table 'attributes'.
  3. For products WITH attributes: generate every valid combination (Odoo's exclusions
     applied at scrape time; we receive valid_variants directly from catalog.json).
     - Each variant: erpnext.controllers.item_variant.create_variant + .save()
     - Each variant: Item Price on 'Standard Selling' from the scraped row's
       ERPNext variant price, falling back to row price and then base price.
  4. For products WITHOUT attributes: Item Price on the template directly.
  5. Attach image: docker-host-side-copied to sites/frontend/public/files/<slug>.png,
     File doc created, Item.image set.
  6. Find-or-create Website Item with published=1, item_group=child group.
  7. ItemVariantsCacheManager.rebuild_cache(template) so webshop selectors render.

Loud-fail discipline (~/.claude/rules/loud-failure.md):
  Any error during a product's seed raises and stops the run. Re-run picks up where
  it left off (idempotent). Better partial success caught loud than silent corruption.

Re-run safety:
  Every step uses find-or-create. Image File records are de-duped on file_url.
  Item Variant Attribute child rows are reset before re-link. Re-running on a fully
  populated DB is a no-op (logs 'unchanged' for everything).
"""
from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path

import frappe
from locally_twisted.catalog_import_subset import (
    assert_must_work_products_included,
    import_exclusion_reasons,
    primary_exclusion_reason,
    reason_counts,
)
from locally_twisted.catalog_contract import build_product_page_contract
from locally_twisted.catalog_variant_rules import (
    dedupe_required_variant_rows,
    normalize_variant_value,
    required_variant_attribute_names,
)
from locally_twisted.product_page_runtime import CONFIG_VERSION, LINE_FIELDNAMES

# Catalog and mapping paths — relative to bench-bench dir or /workspace mount
WORKSPACE_PATHS = [
    # Primary path: bind-mounted via apps/locally_twisted/. Run `python scripts/setup/stage_seed_data.py`
    # on the host before running this module to refresh the staged data.
    Path("/home/frappe/frappe-bench/apps/locally_twisted/locally_twisted/seed/_data"),
    Path("/workspace/_resources/odoo-live"),
    Path("/home/frappe/frappe-bench/_resources/odoo-live"),
    Path("/home/frappe/frappe-bench/sites/_resources/odoo-live"),
]
SITE_FILES_DIR = Path("/home/frappe/frappe-bench/sites/frontend/public/files")
PRICE_LIST = "Standard Selling"


def _find_resources() -> Path:
    """Find the _resources/odoo-live directory inside the container."""
    for p in WORKSPACE_PATHS:
        if p.exists() and (p / "catalog.json").exists():
            return p
    raise SystemExit(
        "FATAL: _resources/odoo-live not found inside container. "
        "Bind-mount the project _resources/ dir into the container at "
        "/workspace/_resources before running."
    )


def _load_inputs():
    base = _find_resources()
    catalog = json.loads((base / "catalog.json").read_text(encoding="utf-8"))
    slug_to_group_raw = json.loads((base / "slug_to_group.json").read_text(encoding="utf-8"))
    slug_to_group = {k: v for k, v in slug_to_group_raw.items() if not k.startswith("_")}
    normalize_map = json.loads((base / "value_normalize_map.json").read_text(encoding="utf-8"))
    return catalog, slug_to_group, normalize_map, base / "images"


# ── Helpers ──────────────────────────────────────────────────────────

def _normalize_value(attr_name: str, raw_value: str, normalize_map: dict) -> str:
    """Map a raw Odoo value to its canonical case-deduped form."""
    key = " ".join(raw_value.split()).lower()
    value = normalize_map.get(attr_name, {}).get(key, raw_value)
    return normalize_variant_value(attr_name, value)


def _find_source_image(slug: str, images_dir: Path) -> Path | None:
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        candidate = images_dir / f"{slug}{ext}"
        if candidate.exists():
            return candidate
    return None


def _ensure_file_attached(item_code: str, slug: str, images_dir: Path) -> str | None:
    """Copy image into site files dir, create File doc, return the file_url.

    Returns None if no source image exists (loud-flagged by caller)."""
    src = _find_source_image(slug, images_dir)
    if not src:
        return None

    file_url = f"/files/{src.name}"
    target = SITE_FILES_DIR / src.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.stat().st_size != src.stat().st_size:
        shutil.copy2(src, target)

    # File doc — find existing attached to this Item, else create
    existing = frappe.db.exists("File", {
        "file_url": file_url,
        "attached_to_doctype": "Item",
        "attached_to_name": item_code,
    })
    if not existing:
        # Also check unattached File doc on same URL (avoids "is_attached" duplication)
        unattached = frappe.db.exists("File", {"file_url": file_url, "attached_to_name": ""})
        if unattached:
            f = frappe.get_doc("File", unattached)
            f.attached_to_doctype = "Item"
            f.attached_to_name = item_code
            f.save(ignore_permissions=True)
        else:
            f = frappe.get_doc({
                "doctype": "File",
                "file_name": src.name,
                "file_url": file_url,
                "is_private": 0,
                "attached_to_doctype": "Item",
                "attached_to_name": item_code,
            })
            f.insert(ignore_permissions=True)
    return file_url


def _upsert_item_price(item_code: str, price: float):
    """Find-or-update Item Price on Standard Selling for the given item_code.

    Item Price cannot exist on a template Item with has_variants=1 (validate_item_template
    throws). Caller must only call this for variants and for single-SKU templates.
    """
    if price is None:
        return
    name = frappe.db.exists("Item Price", {
        "item_code": item_code,
        "price_list": PRICE_LIST,
        "selling": 1,
    })
    if name:
        # Update if price changed
        existing = frappe.db.get_value("Item Price", name, "price_list_rate")
        if existing != price:
            frappe.db.set_value("Item Price", name, "price_list_rate", price)
        return
    doc = frappe.get_doc({
        "doctype": "Item Price",
        "item_code": item_code,
        "price_list": PRICE_LIST,
        "price_list_rate": price,
        "currency": "USD",
        "selling": 1,
    })
    doc.insert(ignore_permissions=True)


def _upsert_template_item(prod: dict, item_group: str, file_url: str | None) -> str:
    """Find-or-create the parent template Item. Returns the item_code."""
    slug = prod["slug"]
    variant_attributes = required_variant_attribute_names(prod.get("attributes") or {})
    has_attrs = bool(variant_attributes)
    item_name = prod["name"][:140]
    description = prod.get("description") or item_name
    base_price = prod.get("base_price")

    if frappe.db.exists("Item", slug):
        item = frappe.get_doc("Item", slug)
        item.item_name = item_name
        item.item_group = item_group
        item.description = description
        item.is_stock_item = 0
        item.is_sales_item = 1
        item.is_purchase_item = 0
        item.include_item_in_manufacturing = 0
        if file_url:
            item.image = file_url
        if has_attrs and not item.has_variants:
            item.has_variants = 1
            item.variant_based_on = "Item Attribute"
        # Reset attributes child rows to match catalog
        if has_attrs:
            item.attributes = []
            for attr_name in variant_attributes:
                item.append("attributes", {"attribute": attr_name})
        item.save(ignore_permissions=True)
        return item.name

    # Create new template
    item = frappe.get_doc({
        "doctype": "Item",
        "item_code": slug,
        "item_name": item_name,
        "item_group": item_group,
        "stock_uom": "Nos",
        "is_stock_item": 0,
        "is_sales_item": 1,
        "is_purchase_item": 0,
        "include_item_in_manufacturing": 0,
        "description": description,
        "image": file_url or "",
        "has_variants": 1 if has_attrs else 0,
        "variant_based_on": "Item Attribute" if has_attrs else None,
        "attributes": [{"attribute": an} for an in variant_attributes] if has_attrs else [],
    })
    item.insert(ignore_permissions=True)
    return item.name


def _clean_route(item_group: str, slug: str) -> str:
    """Build a clean predictable route: '<group_route>/<slug>'.

    Webshop's WebsiteItem.make_route() appends random_string(5) to every
    auto-generated route (line 116 of website_item.py). This produces ugly,
    unstable URLs like '/shop-items/arches/basketball-arch-tljq2'. We override
    by setting `route` explicitly so the if-not-self.route branch doesn't fire.
    """
    group_route = frappe.db.get_value("Item Group", item_group, "route") or ""
    return f"{group_route}/{slug}".lstrip("/")


def _set_website_item_contract(wi, contract) -> None:
    meta = frappe.get_meta("Website Item")
    if meta.has_field("lt_product_page_type"):
        wi.lt_product_page_type = contract.product_page_type
    if meta.has_field("lt_commerce_lane"):
        wi.lt_commerce_lane = contract.commerce_lane


def _upsert_website_item(template_code: str, prod: dict, item_group: str, file_url: str | None, contract) -> str:
    """Find-or-create the Website Item for the template. Returns the Website Item name."""
    existing = frappe.db.exists("Website Item", {"item_code": template_code})
    slug = prod["slug"]
    web_item_name = prod["name"][:140]
    short_desc = prod.get("description") or web_item_name
    long_desc = prod.get("description") or ""
    target_route = _clean_route(item_group, slug)

    if existing:
        wi = frappe.get_doc("Website Item", existing)
        wi.web_item_name = web_item_name
        wi.item_group = item_group
        wi.published = 1
        wi.route = target_route  # force clean route — overrides random_string suffix
        wi.short_description = short_desc[:140] if short_desc else None
        wi.web_long_description = long_desc
        if file_url:
            wi.website_image = file_url
        _set_website_item_contract(wi, contract)
        wi.save(ignore_permissions=True)
        return wi.name

    # New Website Item — go through webshop's helper for correct linkage,
    # then override the random-suffixed route with our clean one.
    from webshop.webshop.doctype.website_item.website_item import make_website_item
    item_doc = frappe.get_doc("Item", template_code)
    web_item_name_returned, _route = make_website_item(item_doc, save=True)
    wi = frappe.get_doc("Website Item", web_item_name_returned)
    wi.web_item_name = web_item_name
    wi.item_group = item_group
    wi.published = 1
    wi.route = target_route
    wi.short_description = short_desc[:140] if short_desc else None
    wi.web_long_description = long_desc
    if file_url:
        wi.website_image = file_url
    _set_website_item_contract(wi, contract)
    wi.save(ignore_permissions=True)
    return wi.name


def _build_import_plan(
    *,
    catalog: dict,
    slug_to_group: dict,
    images_dir: Path,
    max_products: int | None,
    slug_filter: str | None,
    v1_subset_only: bool,
) -> dict:
    products = catalog["products"]
    if slug_filter:
        products = [p for p in products if p["slug"] == slug_filter]
    if max_products:
        products = products[:max_products]

    rows = []
    selected = []
    excluded = []
    missing_groups = []
    missing_images = []
    for prod in products:
        slug = prod["slug"]
        group = slug_to_group.get(slug)
        if not group:
            missing_groups.append(slug)
            rows.append({"slug": slug, "status": "blocked", "blocker": "missing slug_to_group mapping"})
            continue

        contract = build_product_page_contract(prod, category_hint=group)
        exclusion_details = import_exclusion_reasons(prod, contract) if v1_subset_only else []
        exclusion_codes = [reason["code"] for reason in exclusion_details]
        primary_exclusion = primary_exclusion_reason(exclusion_details)
        source_image = _find_source_image(slug, images_dir)
        if not source_image:
            missing_images.append(slug)

        row = {
            "slug": slug,
            "name": prod.get("name"),
            "item_group": group,
            "product_page_type": contract.product_page_type,
            "commerce_lane": contract.commerce_lane,
            "source_variant_rows": contract.source_variant_rows,
            "has_customization_axes": bool(contract.customization_axes),
            "image_status": "present" if source_image else "missing",
            "selected_for_v1_import": not exclusion_details,
            "primary_exclusion_reason": primary_exclusion,
            "excluded_reason_codes": exclusion_codes,
            "excluded_reason_details": exclusion_details,
            "excluded_reasons": [reason["detail"] for reason in exclusion_details],
        }
        rows.append(row)
        if exclusion_details:
            excluded.append(row)
        else:
            selected.append(row)

    return {
        "schema_version": "lt-catalog-import-plan-v1",
        "dry_run_default": True,
        "destructive_import_requires_explicit_flag": True,
        "line_configuration_architecture": {
            "config_version": CONFIG_VERSION,
            "fieldnames": LINE_FIELDNAMES,
            "writer": "locally_twisted.product_page_runtime",
        },
        "summary": {
            "source_products_seen": len(products),
            "selected_for_v1_import": len(selected),
            "excluded_from_v1_import": len(excluded),
            "excluded_counts_by_primary_reason": reason_counts(rows, primary=True),
            "excluded_counts_by_reason": reason_counts(rows, primary=False),
            "must_work_validation_errors": assert_must_work_products_included(rows) if v1_subset_only else [],
            "missing_groups": len(missing_groups),
            "missing_images": len(missing_images),
        },
        "missing_groups": missing_groups,
        "missing_images": missing_images,
        "rows": rows,
    }


def _guard_path_exists(label: str, value: str | None) -> str:
    if not str(value or "").strip():
        raise SystemExit(f"FATAL: destructive import requires {label}.")
    path = Path(str(value))
    if not path.exists():
        raise SystemExit(f"FATAL: destructive import {label} does not exist: {path}")
    return str(path)


def _validate_destructive_guards(
    *,
    destructive: bool,
    backup_path: str | None,
    snapshot_path: str | None,
    purge_scope_report: str | None,
) -> dict:
    if not destructive:
        return {"destructive": False, "write_allowed": False}
    if not str(backup_path or "").strip():
        raise SystemExit("FATAL: destructive import requires a named backup_path from `bench --site frontend backup --with-files`.")
    snapshot = _guard_path_exists("snapshot_path", snapshot_path)
    purge_report = _guard_path_exists("purge_scope_report", purge_scope_report)
    return {
        "destructive": True,
        "write_allowed": True,
        "backup_path": str(backup_path),
        "snapshot_path": snapshot,
        "purge_scope_report": purge_report,
    }


def _seed_variants(template_code: str, prod: dict, normalize_map: dict, log) -> int:
    """Generate Item Variants for every valid combination Odoo encoded.

    Each variant gets its own Item Price on Standard Selling from the scraped
    variant row. Odoo's JSON-LD page price is only the base page price; dynamic
    variant prices come from /website_sale/get_combination_info.

    Returns: number of variants created (excluding existing).
    """
    base_price = prod.get("base_price")
    valid = dedupe_required_variant_rows(prod.get("valid_variants", []))
    if not valid:
        return 0

    from erpnext.controllers.item_variant import create_variant, get_variant, ItemVariantExistsError

    created = 0
    for v in valid:
        # Map combo {attr_name: raw_value} → normalized canonical values
        args = {
            attr_name: _normalize_value(attr_name, raw, normalize_map)
            for attr_name, raw in v["combo"].items()
        }
        try:
            existing = get_variant(template_code, args=args)
        except Exception:
            existing = None
        variant_price = v.get("erpnext_variant_price", v.get("price", base_price))
        if existing:
            _upsert_item_price(existing, variant_price)
            continue

        try:
            new_variant = create_variant(template_code, args=args)
            new_variant.insert(ignore_permissions=True)
            created += 1
        except ItemVariantExistsError:
            # Race or stale flag; treat as already-created
            existing = get_variant(template_code, args=args)
            if existing:
                _upsert_item_price(existing, variant_price)
            continue

        _upsert_item_price(new_variant.name, variant_price)

        # Per-variant image: leave Item.image inherited from template (auto-copied
        # from template by create_variant).

    return created


def _rebuild_variant_cache(template_code: str):
    """Rebuild the Redis variant cache for a template so webshop selectors render."""
    try:
        from webshop.webshop.variant_selector.utils import ItemVariantsCacheManager
        ItemVariantsCacheManager(template_code).rebuild_cache()
    except Exception as e:
        # Cache rebuild failure is not fatal — selector will lazy-build on first hit
        frappe.log_error(f"variant cache rebuild failed for {template_code}: {e}",
                         title="LT seed_catalog: cache rebuild")


# ── Public entrypoint ────────────────────────────────────────────────

def execute(
    max_products: int | None = None,
    slug_filter: str | None = None,
    dry_run: bool = True,
    destructive: bool = False,
    backup_path: str | None = None,
    snapshot_path: str | None = None,
    purge_scope_report: str | None = None,
    v1_subset_only: bool = True,
) -> str:
    """Plan or seed the Odoo catalog into ERPNext webshop.

    Args:
        max_products: optional cap for smoke testing. None = process all.
        slug_filter: optional single-slug filter for surgical re-run on one product.
        dry_run: defaults to True and performs no ERPNext writes.
        destructive: required before any ERPNext write/import path can run.
        backup_path: required in destructive mode; name/path from bench backup.
        snapshot_path: required existing snapshot folder in destructive mode.
        purge_scope_report: required existing purge dry-run report in destructive mode.
        v1_subset_only: excludes owner-named unsupported structures and proven backend/schema blockers.

    Returns: a summary string.
    """
    catalog, slug_to_group, normalize_map, images_dir = _load_inputs()
    guard = _validate_destructive_guards(
        destructive=destructive,
        backup_path=backup_path,
        snapshot_path=snapshot_path,
        purge_scope_report=purge_scope_report,
    )
    plan = _build_import_plan(
        catalog=catalog,
        slug_to_group=slug_to_group,
        images_dir=images_dir,
        max_products=max_products,
        slug_filter=slug_filter,
        v1_subset_only=v1_subset_only,
    )

    if dry_run or not destructive:
        plan["mode"] = "dry_run"
        plan["guard"] = guard
        plan["next_command_sequence"] = [
            "python scripts/setup/stage_seed_data.py",
            "bench --site frontend backup --with-files",
            "python scripts/verify/catalog_state_snapshot_contract.py",
            "python scripts/verify/catalog_purge_scope_dry_run.py",
            "bench --site frontend execute locally_twisted.seed.seed_catalog.execute --kwargs \"{'dry_run': True}\"",
            "bench --site frontend execute locally_twisted.seed.seed_catalog.execute --kwargs \"{'dry_run': False, 'destructive': True, 'backup_path': '<backup>', 'snapshot_path': '<snapshot>', 'purge_scope_report': '<purge-report>'}\"",
        ]
        rendered = json.dumps(plan, indent=2, sort_keys=True)
        print(rendered)
        return rendered

    if plan["missing_groups"]:
        raise SystemExit(f"FATAL: missing group mappings: {plan['missing_groups']}")

    # in_import skips email triggers and some validate paths — speeds bulk insert.
    frappe.flags.in_import = True
    frappe.flags.ignore_permissions = True

    selected_slugs = {row["slug"] for row in plan["rows"] if row.get("selected_for_v1_import")}
    products = [p for p in catalog["products"] if p["slug"] in selected_slugs]

    print(f"=== Seeding {len(products)} products ===")
    print(f"  catalog: {len(catalog['products'])} total, {len(products)} processing")
    print(f"  images_dir: {images_dir}")
    print()

    started = time.time()
    summary = {
        "products_seeded": 0,
        "variants_created": 0,
        "items_already_present": 0,
        "missing_images": [],
        "missing_groups": [],
        "errors": [],
    }

    for i, prod in enumerate(products, 1):
        slug = prod["slug"]
        group = slug_to_group.get(slug)
        if not group:
            summary["missing_groups"].append(slug)
            print(f"[{i:3}/{len(products)}] {slug}: FATAL no group mapping")
            raise SystemExit(f"slug_to_group.json missing entry for {slug!r}")

        try:
            contract = build_product_page_contract(prod, category_hint=group)
            file_url = _ensure_file_attached(slug, slug, images_dir)
            if not file_url:
                summary["missing_images"].append(slug)
                print(f"[{i:3}/{len(products)}] {slug}: missing image (continuing without)")

            already_present = frappe.db.exists("Item", slug)
            template = _upsert_template_item(prod, group, file_url)

            # If template has variants, do NOT create Item Price on it (validate_item_template throws)
            has_attrs = bool(prod.get("attributes"))
            if not has_attrs:
                _upsert_item_price(template, prod.get("base_price"))

            web_item = _upsert_website_item(template, prod, group, file_url, contract)

            variants_created = 0
            if has_attrs:
                variants_created = _seed_variants(template, prod, normalize_map, print)
                _rebuild_variant_cache(template)

            summary["products_seeded"] += 1
            summary["variants_created"] += variants_created
            if already_present:
                summary["items_already_present"] += 1

            elapsed = time.time() - started
            print(f"[{i:3}/{len(products)}] {slug:<48} grp={group:<20} "
                  f"variants:+{variants_created:<4} "
                  f"({elapsed:.1f}s elapsed)")

            # Commit per product so a crash mid-run preserves what landed
            frappe.db.commit()

        except SystemExit:
            raise
        except Exception as e:
            summary["errors"].append({"slug": slug, "error": f"{type(e).__name__}: {e}"})
            print(f"[{i:3}/{len(products)}] {slug}: FAIL — {type(e).__name__}: {e}")
            raise

    elapsed = time.time() - started
    print()
    print(f"=== DONE in {elapsed:.1f}s ===")
    print(f"  products seeded: {summary['products_seeded']}")
    print(f"  variants created: {summary['variants_created']}")
    print(f"  items pre-existing: {summary['items_already_present']}")
    print(f"  missing images: {len(summary['missing_images'])} ({summary['missing_images']})")
    print(f"  errors: {len(summary['errors'])}")

    return json.dumps(summary, indent=2)
