#!/usr/bin/env python3
"""Minimum real-catalog import readiness gate for LT ecommerce.

This verifier is non-mutating. It does not import, purge, delete, upload, or
change ERPNext records. It checks whether the current repo has the source
artifacts, approval packets, fail-loud import fields, and snapshot/rollback
preconditions needed before a real product catalog import rehearsal.

Run:
  python scripts/verify/product_import_readiness_gate.py
  python scripts/verify/product_import_readiness_gate.py --json
  python scripts/verify/product_import_readiness_gate.py --report output/product-import-readiness-gate.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "_resources" / "odoo-live"
AUDIT_ROOT = ROOT / "audits" / "odoo-erpnext-migration-audit-2026-05-08"
IMPORT_RUNNER = ROOT / "apps" / "locally_twisted" / "locally_twisted" / "seed" / "seed_catalog.py"

SOURCE_CONTRACT_JSON = AUDIT_ROOT / "15-product-page-contract-source-audit.json"
PRICE_ENRICHMENT_JSON = AUDIT_ROOT / "21-product-page-price-enrichment-candidates.json"
ADD_ON_APPROVAL_JSON = AUDIT_ROOT / "22-product-add-on-approval-packet.json"
MEDIA_CLASSIFICATION_JSON = AUDIT_ROOT / "23-product-page-media-classification-packet.json"
PRICE_REVIEW_JSON = AUDIT_ROOT / "24-product-page-price-review-packet.json"
PURGE_DRY_RUN_REPORT = AUDIT_ROOT / "16-catalog-purge-scope-dry-run.md"
PURGE_DRY_RUN_JSON = AUDIT_ROOT / "16-catalog-purge-scope-dry-run.json"
V1_IMPORT_MANIFEST_JSON = AUDIT_ROOT / "25-v1-odoo-erpnext-import-manifest.json"
GUARD_PATHS_JSON = AUDIT_ROOT / "27-local-import-guard-paths.json"
FINAL_APPROVAL_JSON = AUDIT_ROOT / "28-local-destructive-import-approval.json"

EXPECTED_INCLUDED_PRODUCTS = 48
EXPECTED_EXCLUDED_PRODUCTS = 5
EXPECTED_EXCLUDED_SLUGS = {
    "classic-arch",
    "classic-column",
    "classic-organic-arch",
    "classic-organic-balloon-garland",
    "classic-organic-columns",
}
EXPECTED_PURGE_COUNTS = {
    "website_items": 48,
    "item_templates": 48,
    "item_variants": 6894,
    "item_prices": 6928,
}

REQUIRED_SOURCE_FILES = (
    SOURCE_ROOT / "catalog.json",
    SOURCE_ROOT / "slug_to_group.json",
    SOURCE_ROOT / "value_normalize_map.json",
)
REQUIRED_IMPORT_FIELD_MARKERS = (
    "lt_product_page_type",
    "lt_commerce_lane",
    "build_product_page_contract",
    "LINE_FIELDNAMES",
)
REQUIRED_GUARD_MARKERS = (
    "dry_run",
    "destructive",
    "backup_path",
    "snapshot_path",
    "purge_scope_report",
)
FRESH_SNAPSHOT_PLACEHOLDER = "<fresh current-state-snapshot-* required>"


@dataclass
class GateRow:
    id: str
    status: str
    summary: str
    blocker: str | None = None
    next_action: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {
            "id": self.id,
            "status": self.status,
            "summary": self.summary,
            "blocker": self.blocker,
            "next_action": self.next_action,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True)

    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[PRODUCT IMPORT READINESS GATE] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(report)

    return 0 if report["ok"] else 2


def build_report() -> dict[str, Any]:
    rows = [
        _source_files_row(),
        _corrected_v1_manifest_row(),
        _source_trace_preservation_row(),
        _v1_price_approval_row(),
        _v1_media_row(),
        _v1_add_on_row(),
        _purge_scope_row(),
        _snapshot_row(),
        _backup_required_row(),
        _import_runner_fields_row(),
        _import_runner_guard_row(),
        _final_destructive_approval_row(),
    ]
    blockers = [row for row in rows if row.status == "blocker"]
    warnings = [row for row in rows if row.status == "warning"]
    manifest = _optional_json(V1_IMPORT_MANIFEST_JSON) or {}
    return {
        "ok": not blockers,
        "scope": "corrected_v1_real_catalog_import_readiness",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "read_only": True,
        "current_product_records_are_fixture_evidence_only": True,
        "destructive_import_allowed": False if blockers else True,
        "corrected_v1_manifest": _manifest_summary(manifest),
        "summary": {
            "pass": sum(1 for row in rows if row.status == "pass"),
            "warning": len(warnings),
            "blocker": len(blockers),
        },
        "rows": [row.as_dict() for row in rows],
        "blockers": [row.blocker for row in blockers if row.blocker],
        "required_snapshot_and_rollback_plan": _rollback_plan(),
        "required_verifier_commands": _verifier_commands(),
        "local_only_command_packet": _local_only_command_packet(),
    }


def _source_files_row() -> GateRow:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_SOURCE_FILES if not path.exists()]
    if not (SOURCE_ROOT / "images").is_dir():
        missing.append(str((SOURCE_ROOT / "images").relative_to(ROOT)))
    if missing:
        return GateRow(
            "source_files_present",
            "blocker",
            "Real import source packet must exist in the repo before import rehearsal.",
            blocker=f"Missing source files or image directory: {', '.join(missing)}",
            next_action="Refresh the approved source packet before any import rehearsal.",
        )
    source = _read_json(REQUIRED_SOURCE_FILES[0])
    products = source.get("products") if isinstance(source, dict) else source
    count = len(products or [])
    if count <= 0:
        return GateRow(
            "source_files_present",
            "blocker",
            "Source catalog exists but has no product rows.",
            blocker="_resources/odoo-live/catalog.json has zero product rows.",
            next_action="Rebuild the source catalog packet from the approved source before import.",
        )
    return GateRow(
        "source_files_present",
        "pass",
        f"Source catalog packet is present with {count} product rows and an image directory.",
    )


def _corrected_v1_manifest_row() -> GateRow:
    manifest = _optional_json(V1_IMPORT_MANIFEST_JSON)
    if manifest is None:
        return GateRow(
            "corrected_v1_manifest",
            "blocker",
            "Corrected V1 manifest is required before purge/import.",
            blocker=f"Missing {V1_IMPORT_MANIFEST_JSON.relative_to(ROOT)}.",
            next_action="Run: python scripts/verify/v1_odoo_erpnext_import_manifest.py",
        )

    validation = manifest.get("validation") or {}
    summary = manifest.get("summary") or {}
    excluded_products = manifest.get("excluded_products") or []
    excluded_slugs = {str(row.get("slug") or "") for row in excluded_products}
    errors = validation.get("errors") or []
    included = int(summary.get("included_products") or 0)
    excluded = int(summary.get("excluded_products") or 0)
    if (
        not validation.get("ok")
        or included != EXPECTED_INCLUDED_PRODUCTS
        or excluded != EXPECTED_EXCLUDED_PRODUCTS
        or excluded_slugs != EXPECTED_EXCLUDED_SLUGS
    ):
        return GateRow(
            "corrected_v1_manifest",
            "blocker",
            "Corrected V1 manifest does not match the owner-approved import subset.",
            blocker=(
                f"included={included}, expected={EXPECTED_INCLUDED_PRODUCTS}; "
                f"excluded={excluded}, expected={EXPECTED_EXCLUDED_PRODUCTS}; "
                f"excluded_slugs={sorted(excluded_slugs)}, expected={sorted(EXPECTED_EXCLUDED_SLUGS)}; "
                f"validation_errors={errors}"
            ),
            next_action="Regenerate the corrected manifest and fix any validation errors before destructive import.",
        )

    return GateRow(
        "corrected_v1_manifest",
        "pass",
        f"Corrected manifest validates {included} included products and {excluded} owner-explicit exclusions.",
    )


def _source_trace_preservation_row() -> GateRow:
    manifest = _optional_json(V1_IMPORT_MANIFEST_JSON)
    if manifest is None:
        return GateRow(
            "source_trace_preservation",
            "blocker",
            "Corrected V1 manifest is missing, so source trace preservation cannot be evaluated.",
            blocker=f"Missing {V1_IMPORT_MANIFEST_JSON.relative_to(ROOT)}.",
            next_action="Run: python scripts/verify/v1_odoo_erpnext_import_manifest.py",
        )

    missing_identity = []
    missing_pattern = []
    missing_axis_hash = []
    variant_mismatches = []
    for row in manifest.get("products") or []:
        slug = str(row.get("slug") or "")
        trace = row.get("source_trace") or {}
        if not trace.get("odoo_product_id") or not trace.get("source_url") or not trace.get("source_integrity"):
            missing_identity.append(slug)
        if not trace.get("source_pattern_class"):
            missing_pattern.append(slug)
        axis_hashes = trace.get("source_axis_hashes") or []
        if not isinstance(axis_hashes, list) or any(not axis.get("source_value_hash") for axis in axis_hashes):
            missing_axis_hash.append(slug)
        expected = int((row.get("product_contract") or {}).get("source_variant_rows") or 0)
        variant_pointers = trace.get("source_variant_pointers") or {}
        actual = int(variant_pointers.get("source_variant_count") or 0)
        if expected != actual or (expected and not variant_pointers.get("source_variant_pointer_hash")):
            variant_mismatches.append(f"{slug} expected {expected}, got {actual}")

    blockers = []
    if missing_identity:
        blockers.append("missing source IDs/integrity: " + ", ".join(missing_identity))
    if missing_pattern:
        blockers.append("missing pattern class: " + ", ".join(missing_pattern))
    if missing_axis_hash:
        blockers.append("missing axis hashes: " + ", ".join(missing_axis_hash))
    if variant_mismatches:
        blockers.append("variant pointer mismatches: " + "; ".join(variant_mismatches))
    if blockers:
        return GateRow(
            "source_trace_preservation",
            "blocker",
            "Import manifest must preserve source IDs, axis hashes, variant pointers, and pattern class.",
            blocker=" | ".join(blockers),
            next_action="Regenerate the V1 manifest from the source mapper and do not run destructive import until trace fields validate.",
        )

    return GateRow(
        "source_trace_preservation",
        "pass",
        "Corrected V1 manifest preserves source IDs, source integrity, axis hashes, source variant pointers, and pattern class for included products.",
    )


def _v1_price_approval_row() -> GateRow:
    manifest = _optional_json(V1_IMPORT_MANIFEST_JSON)
    if manifest is None:
        return GateRow(
            "v1_price_approval",
            "blocker",
            "Corrected V1 manifest is missing, so included price readiness cannot be evaluated.",
            blocker=f"Missing {V1_IMPORT_MANIFEST_JSON.relative_to(ROOT)}.",
            next_action="Run: python scripts/verify/v1_odoo_erpnext_import_manifest.py",
        )
    summary = manifest.get("summary") or {}
    sale_units = int(summary.get("v1_sale_units") or 0)
    needs_hold_or_fix = int(summary.get("v1_price_review_units") or 0)
    resolution = summary.get("v1_price_units_by_source") or {}
    conflicts = int(resolution.get("conflict_needs_fix") or 0)
    holds = int(resolution.get("source_price_missing_checkout_hold") or 0)
    ready = int(resolution.get("source_price_ready") or 0)
    if sale_units <= 0:
        return GateRow(
            "v1_price_approval",
            "blocker",
            "Corrected V1 manifest has no sale units.",
            blocker="v1_sale_units is zero.",
            next_action="Regenerate price enrichment and the corrected V1 manifest.",
        )
    if conflicts:
        return GateRow(
            "v1_price_approval",
            "blocker",
            "Included product prices have source conflicts that must be fixed before destructive import.",
            blocker=f"{conflicts} of {sale_units} included sale units have conflicting source prices. Resolution: {resolution}.",
            next_action="Fix conflicting source prices, or explicitly mark affected sale units/products as checkout-hold before destructive import.",
        )
    if holds:
        return GateRow(
            "v1_price_approval",
            "warning",
            f"{ready} sale units have source prices; {holds} sale units are recorded as checkout-hold/quote-first because source price is missing.",
            next_action="Do not enable direct checkout for held sale units until prices are provided.",
        )

    return GateRow(
        "v1_price_approval",
        "pass",
        f"All {sale_units} included sale units have deterministic source prices. Resolution: {resolution}.",
    )


def _v1_media_row() -> GateRow:
    manifest = _optional_json(V1_IMPORT_MANIFEST_JSON)
    if manifest is None:
        return GateRow(
            "v1_media",
            "blocker",
            "Corrected V1 manifest is missing, so included media readiness cannot be evaluated.",
            blocker=f"Missing {V1_IMPORT_MANIFEST_JSON.relative_to(ROOT)}.",
            next_action="Run: python scripts/verify/v1_odoo_erpnext_import_manifest.py",
        )
    products = manifest.get("products") or []
    missing_primary = [
        f"{row.get('source_name')} ({row.get('slug')})"
        for row in products
        if not ((row.get("media_manifest") or {}).get("primary_image_url"))
    ]
    if missing_primary:
        return GateRow(
            "v1_media",
            "blocker",
            "Included products need primary media before import.",
            blocker="Missing primary media for: " + "; ".join(missing_primary),
            next_action="Provide/choose primary media or hold the affected product out of import.",
        )
    held = int((manifest.get("summary") or {}).get("v1_extra_images_held") or 0)
    return GateRow(
        "v1_media",
        "pass",
        f"Included products have primary media. {held} optional extra media rows are held and do not block import.",
    )


def _v1_add_on_row() -> GateRow:
    manifest = _optional_json(V1_IMPORT_MANIFEST_JSON)
    if manifest is None:
        return GateRow(
            "v1_add_on_fallbacks",
            "blocker",
            "Corrected V1 manifest is missing, so included add-on behavior cannot be evaluated.",
            blocker=f"Missing {V1_IMPORT_MANIFEST_JSON.relative_to(ROOT)}.",
            next_action="Run: python scripts/verify/v1_odoo_erpnext_import_manifest.py",
        )
    bad = []
    review_only = []
    for row in manifest.get("products") or []:
        axes = (row.get("add_on_manifest") or {}).get("review_only_axes_from_global_packet") or []
        if not axes:
            continue
        label = f"{row.get('source_name')} ({row.get('slug')}): {', '.join(axes)}"
        review_only.append(label)
        lane = (row.get("product_contract") or {}).get("commerce_lane")
        if lane != "quote_first":
            bad.append(label)
    if bad:
        return GateRow(
            "v1_add_on_fallbacks",
            "blocker",
            "Review-only add-on axes exist on non-quote-first included products.",
            blocker="Needs checkout mapping or quote-first fallback for: " + "; ".join(bad),
            next_action="Map the add-on axes into checkout or set those products to quote-first before destructive import.",
        )
    if review_only:
        return GateRow(
            "v1_add_on_fallbacks",
            "pass",
            f"{len(review_only)} included product(s) keep review-only add-on axes protected behind quote-first fallback.",
            next_action="Map these add-ons before allowing direct checkout for those products.",
        )
    return GateRow(
        "v1_add_on_fallbacks",
        "pass",
        "Included products have no unmapped add-on axes requiring fallback.",
    )


def _purge_scope_row() -> GateRow:
    if not PURGE_DRY_RUN_REPORT.exists() or not PURGE_DRY_RUN_JSON.exists():
        return GateRow(
            "purge_scope_dry_run",
            "blocker",
            "A destructive import needs a precomputed catalog-owned purge scope.",
            blocker="Missing purge scope report or JSON artifact.",
            next_action="Run: python scripts/verify/catalog_purge_scope_dry_run.py",
        )
    artifact = _read_json(PURGE_DRY_RUN_JSON)
    subset = artifact.get("v1_subset") or {}
    counts = artifact.get("purge_scope_counts") or {}
    included = int(subset.get("included_count") or 0)
    excluded = int(subset.get("excluded_count") or 0)
    excluded_slugs = {str(row.get("slug") or "") for row in subset.get("excluded_products") or []}
    count_mismatches = {
        key: {"actual": int(counts.get(key) or 0), "expected": expected}
        for key, expected in EXPECTED_PURGE_COUNTS.items()
        if int(counts.get(key) or 0) != expected
    }
    if (
        included != EXPECTED_INCLUDED_PRODUCTS
        or excluded != EXPECTED_EXCLUDED_PRODUCTS
        or excluded_slugs != EXPECTED_EXCLUDED_SLUGS
        or count_mismatches
    ):
        return GateRow(
            "purge_scope_dry_run",
            "blocker",
            "Catalog purge scope does not match the corrected V1 manifest.",
            blocker=(
                f"purge included={included}, excluded={excluded}; expected "
                f"{EXPECTED_INCLUDED_PRODUCTS}/{EXPECTED_EXCLUDED_PRODUCTS}; "
                f"excluded_slugs={sorted(excluded_slugs)}, expected={sorted(EXPECTED_EXCLUDED_SLUGS)}; "
                f"count_mismatches={count_mismatches}"
            ),
            next_action="Rerun: python scripts/verify/catalog_purge_scope_dry_run.py",
        )
    return GateRow(
        "purge_scope_dry_run",
        "pass",
        (
            f"Catalog purge scope dry-run exists for {included} included products, "
            f"{excluded} owner-explicit exclusions, "
            f"{counts.get('item_templates')} templates, {counts.get('item_variants')} variants, "
            f"and {counts.get('item_prices')} prices."
        ),
    )


def _snapshot_row() -> GateRow:
    snapshots = sorted(AUDIT_ROOT.glob("current-state-snapshot-*"))
    if not snapshots:
        return GateRow(
            "fresh_catalog_snapshot",
            "blocker",
            "No current-state catalog snapshot exists for rollback comparison.",
            blocker="Missing current-state-snapshot-* folder under the catalog audit.",
            next_action="Create a fresh pre-import ERPNext catalog snapshot after source freeze.",
        )
    newest = max(snapshots, key=lambda path: path.stat().st_mtime)
    modified = datetime.fromtimestamp(newest.stat().st_mtime, UTC).date()
    if modified != date.today():
        return GateRow(
            "fresh_catalog_snapshot",
            "blocker",
            "Snapshot exists, but it is not fresh enough for destructive import.",
            blocker=f"Newest snapshot is {newest.relative_to(ROOT)} with modified date {modified.isoformat()}; today is {date.today().isoformat()}.",
            next_action="Create a fresh source-freeze/pre-import snapshot and rerun this gate.",
        )
    return GateRow(
        "fresh_catalog_snapshot",
        "pass",
        f"Fresh catalog snapshot exists: {newest.relative_to(ROOT)}.",
    )


def _backup_required_row() -> GateRow:
    artifact = _optional_json(GUARD_PATHS_JSON)
    if artifact and artifact.get("guard_verification", {}).get("ok"):
        backup = artifact.get("backup_path")
        return GateRow(
            "fresh_backup_required",
            "pass",
            f"Fresh local backup path and container-visible guard paths are recorded: {backup}.",
        )
    return GateRow(
        "fresh_backup_required",
        "blocker",
        "Final destructive purge/import requires a fresh `bench --site frontend backup --with-files` backup path.",
        blocker="No backup path is recorded in this non-destructive readiness gate.",
        next_action="Run local backup and guard-path verification, then write audits/odoo-erpnext-migration-audit-2026-05-08/27-local-import-guard-paths.json.",
    )


def _import_runner_fields_row() -> GateRow:
    if not IMPORT_RUNNER.exists():
        return GateRow(
            "import_runner_required_fields",
            "blocker",
            "Import runner is missing.",
            blocker=f"Missing {IMPORT_RUNNER.relative_to(ROOT)}.",
            next_action="Create or restore the ERPNext catalog import runner before import rehearsal.",
        )
    text = IMPORT_RUNNER.read_text(encoding="utf-8", errors="replace")
    missing = [marker for marker in REQUIRED_IMPORT_FIELD_MARKERS if marker not in text]
    if missing:
        return GateRow(
            "import_runner_required_fields",
            "blocker",
            "Import runner does not write the current ecommerce authority fields.",
            blocker=f"{IMPORT_RUNNER.relative_to(ROOT)} is missing markers: {', '.join(missing)}.",
            next_action="Update the import runner to derive and write Website Item page template/buying path fields from the source contract.",
        )
    return GateRow(
        "import_runner_required_fields",
        "pass",
        "Import runner contains the required product-page authority field markers.",
    )


def _import_runner_guard_row() -> GateRow:
    text = IMPORT_RUNNER.read_text(encoding="utf-8", errors="replace") if IMPORT_RUNNER.exists() else ""
    missing = [marker for marker in REQUIRED_GUARD_MARKERS if marker not in text.lower()]
    if missing:
        return GateRow(
            "import_runner_destructive_guard",
            "blocker",
            "Import runner lacks minimum dry-run/destructive/backup guard markers.",
            blocker=f"{IMPORT_RUNNER.relative_to(ROOT)} is missing guard markers: {', '.join(missing)}.",
            next_action="Add dry-run as the default, require an explicit destructive flag, and require a named backup/snapshot before writes.",
        )
    return GateRow(
        "import_runner_destructive_guard",
        "pass",
        "Import runner includes dry-run/destructive/backup guard markers.",
    )


def _final_destructive_approval_row() -> GateRow:
    approval = _optional_json(FINAL_APPROVAL_JSON) or {}
    if approval.get("approved") is True and approval.get("scope") == "local_erpnext_container_site_frontend":
        return GateRow(
            "final_destructive_approval",
            "pass",
            f"Final explicit destructive approval is recorded for local-only site frontend at {approval.get('approved_at')}.",
        )
    return GateRow(
        "final_destructive_approval",
        "blocker",
        "Destructive purge/import is prepared for a local-only command packet but still requires final explicit approval.",
        blocker=(
            f"No final destructive approval is recorded in {FINAL_APPROVAL_JSON.relative_to(ROOT)}; "
            "command must remain local-only and must not target Frappe Cloud/live."
        ),
        next_action="After price decisions, backup path, container-visible snapshot/purge guard paths, and dry-run proof are accepted, request final approval for the exact local-only destructive command.",
    )


def _rollback_plan() -> list[str]:
    return [
        "Freeze source and commit/review the exact import code before staging.",
        "Run `bench --site frontend backup --with-files` on the target site and record the backup path outside chat.",
        "Create a fresh catalog state snapshot of Website Item, Item, Item Price, Item Variant Attribute, Item Attribute, Item Group, and File rows.",
        "Run `python scripts/verify/catalog_purge_scope_dry_run.py` and review the exact protected/excluded item codes.",
        "Run the import runner in dry-run mode and archive the report.",
        "Only after approval, run the destructive/import mode on staging first.",
        "After import, rerun catalog shape, price, media, cart/checkout, and product-import readiness gates.",
        "Rollback path is restore DB/files backup or restore from the fresh snapshot plus rerun the previous known-good fixture/import seed.",
    ]


def _verifier_commands() -> list[str]:
    return [
        "python scripts/verify/v1_odoo_erpnext_import_manifest.py",
        "python scripts/verify/product_import_readiness_gate.py --report output/product-import-readiness-gate.json",
        "python scripts/verify/catalog_state_snapshot_contract.py",
        "python scripts/verify/catalog_purge_scope_dry_run.py",
        "python scripts/setup/stage_seed_data.py",
        "bench --site frontend backup --with-files",
        "bench --site frontend execute locally_twisted.seed.seed_catalog.execute --kwargs \"{'dry_run': True}\"",
        "python scripts/verify/product_page_architecture_readiness.py --json",
        "python scripts/verify/catalog_variant_contract.py",
        "python scripts/verify/cart_checkout_contract.py",
        "python scripts/verify/checkout_product_family_contract.py",
    ]


def _local_only_command_packet() -> list[str]:
    snapshots_by_modified_time = sorted(
        AUDIT_ROOT.glob("current-state-snapshot-*"),
        key=lambda path: path.stat().st_mtime,
    )
    snapshot_path = _snapshot_display_path(snapshots_by_modified_time)
    purge_report = str(PURGE_DRY_RUN_JSON.relative_to(ROOT))
    guard = _optional_json(GUARD_PATHS_JSON) or {}
    backup_path = guard.get("backup_path") or "<backup-from-bench-backup>"
    guard_paths = guard.get("container_visible_paths") or {}
    container_snapshot = guard_paths.get("snapshot_path") or f"<container-visible copy of {snapshot_path}>"
    container_purge = guard_paths.get("purge_scope_report") or f"<container-visible copy of {purge_report}>"
    approved = (_optional_json(FINAL_APPROVAL_JSON) or {}).get("approved") is True
    destructive_prefix = "" if approved else "BLOCKED UNTIL FINAL EXPLICIT APPROVAL: "
    return [
        "python scripts/setup/stage_seed_data.py",
        "docker exec locally-twisted-erpnext-v15-backend-1 bash -lc \"cd /home/frappe/frappe-bench && bench --site frontend backup --with-files\"",
        "docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.seed_catalog.execute --kwargs \"{'dry_run': True, 'v1_subset_only': True}\"",
        (
            f"{destructive_prefix}docker exec locally-twisted-erpnext-v15-backend-1 "
            "bench --site frontend execute locally_twisted.seed.seed_catalog.execute --kwargs "
            "\"{'dry_run': False, 'destructive': True, 'v1_subset_only': True, "
            f"'backup_path': '{backup_path}', "
            f"'snapshot_path': '{container_snapshot}', "
            f"'purge_scope_report': '{container_purge}'}}\""
        ),
    ]


def _snapshot_display_path(snapshot_paths: Iterable[Path]) -> str:
    snapshots = list(snapshot_paths)
    if not snapshots:
        return FRESH_SNAPSHOT_PLACEHOLDER
    newest = snapshots[-1]
    try:
        return str(newest.relative_to(ROOT))
    except ValueError:
        return str(newest)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _optional_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return _read_json(path)


def _manifest_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    if not manifest:
        return {"present": False}
    summary = manifest.get("summary") or {}
    products = manifest.get("products") or []
    return {
        "present": True,
        "validation": manifest.get("validation") or {},
        "summary": summary,
        "included_products": [
            {
                "name": row.get("source_name"),
                "slug": row.get("slug"),
                "status": row.get("ecommerce_import_status"),
                "lane": (row.get("product_contract") or {}).get("commerce_lane"),
                "reasons": row.get("status_reasons") or [],
            }
            for row in products
        ],
        "excluded_products": [
            {
                "name": row.get("name"),
                "slug": row.get("slug"),
                "reason": row.get("primary_exclusion_reason"),
                "details": row.get("excluded_reason_details") or [],
            }
            for row in manifest.get("excluded_products") or []
        ],
    }


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


def _print_summary(report: dict[str, Any]) -> None:
    print("[PRODUCT IMPORT READINESS GATE] " + ("PASS" if report["ok"] else "BLOCKED"))
    print(f"  scope: {report['scope']}")
    print(f"  read_only: {report['read_only']}")
    print(f"  destructive_import_allowed: {report['destructive_import_allowed']}")
    print(
        "  summary: "
        f"{report['summary']['pass']} pass, "
        f"{report['summary']['warning']} warning, "
        f"{report['summary']['blocker']} blocker"
    )
    for row in report["rows"]:
        marker = row["status"].upper()
        print(f"  [{marker}] {row['id']}: {row['summary']}")
        if row.get("blocker"):
            print(f"    blocker: {row['blocker']}")
        if row.get("next_action"):
            print(f"    next: {row['next_action']}")


if __name__ == "__main__":
    sys.exit(main())
