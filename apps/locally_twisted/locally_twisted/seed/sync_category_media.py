"""Assign approved Item Group category images from a staged selection file.

Run in-process:
    bench --site frontend execute locally_twisted.seed.sync_category_media.execute \
        --kwargs '{"data_dir":"/tmp/lt-category-media","dry_run":true}'

The host wrapper at scripts/setup/sync_category_media.py stages selected source
files into the container before calling this module.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import frappe


SITE_FILES_DIR = Path("/home/frappe/frappe-bench/sites/frontend/public/files")
DEFAULT_DATA_DIR = Path("/tmp/lt-category-media")
DEFAULT_SELECTION_FILE = "category-media-selection.json"


def _find_selection(data_dir: str | None, selection_file: str | None) -> Path:
    base = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
    selection = base / (selection_file or DEFAULT_SELECTION_FILE)
    if not selection.exists():
        raise FileNotFoundError(f"Missing category media selection file: {selection}")
    return selection


def _ensure_file_attached(source: Path, category: str) -> str:
    file_url = f"/files/{source.name}"
    target = SITE_FILES_DIR / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.stat().st_size != source.stat().st_size:
        shutil.copy2(source, target)

    existing = frappe.db.exists(
        "File",
        {
            "file_url": file_url,
            "attached_to_doctype": "Item Group",
            "attached_to_name": category,
        },
    )
    if not existing:
        file_doc = frappe.get_doc(
            {
                "doctype": "File",
                "file_name": source.name,
                "file_url": file_url,
                "is_private": 0,
                "attached_to_doctype": "Item Group",
                "attached_to_name": category,
            }
        )
        file_doc.insert(ignore_permissions=True)
    return file_url


def _source_for_selection(selection_path: Path, source_path: str) -> Path:
    staged = selection_path.parent / "images" / Path(source_path).name
    if not staged.exists():
        raise FileNotFoundError(f"Staged image not found for {source_path}: {staged}")
    return staged


def _item_group_state(category: str) -> dict[str, object]:
    row = frappe.db.get_value("Item Group", category, ["name", "parent_item_group", "image"], as_dict=True)
    if not row:
        raise ValueError(f"Item Group does not exist: {category}")
    if row.parent_item_group != "Shop Items":
        raise ValueError(f"Item Group is not a direct Shop Items child: {category}")
    return {"name": row.name, "parent_item_group": row.parent_item_group, "image": row.image}


def execute(
    data_dir: str | None = None,
    selection_file: str | None = None,
    dry_run: bool = True,
) -> dict[str, object]:
    selection_path = _find_selection(data_dir, selection_file)
    payload = json.loads(selection_path.read_text(encoding="utf-8"))
    selections = payload.get("selections") or {}

    results = []
    updated = 0
    unchanged = 0
    would_update = 0
    not_approved = 0
    errors = []

    for category, selection in selections.items():
        result: dict[str, object] = {
            "category": category,
            "approved": bool(selection.get("approved")),
            "source_path": selection.get("source_path"),
        }
        try:
            state = _item_group_state(category)
            if not dry_run and not selection.get("approved"):
                not_approved += 1
                result.update(
                    {
                        "current_image": state["image"],
                        "action": "not_approved",
                    }
                )
                results.append(result)
                continue

            source = _source_for_selection(selection_path, str(selection.get("source_path") or ""))
            file_url = f"/files/{source.name}"
            result.update(
                {
                    "current_image": state["image"],
                    "file_url": file_url,
                    "source_bytes": source.stat().st_size,
                }
            )

            if state["image"] == file_url:
                unchanged += 1
                result["action"] = "unchanged"
            elif dry_run:
                would_update += 1
                result["action"] = "would_update"
            else:
                attached_url = _ensure_file_attached(source, category)
                frappe.db.set_value("Item Group", category, "image", attached_url, update_modified=False)
                updated += 1
                result["action"] = "updated"
        except Exception as exc:
            result["action"] = "error"
            result["error"] = str(exc)
            errors.append({"category": category, "error": str(exc)})
        results.append(result)

    if not dry_run and updated:
        frappe.db.commit()

    ok = not errors and (dry_run or not not_approved)
    return {
        "data_dir": str(selection_path.parent),
        "selection_file": selection_path.name,
        "dry_run": bool(dry_run),
        "ok": ok,
        "selected": len(selections),
        "would_update": would_update,
        "updated": updated,
        "unchanged": unchanged,
        "not_approved": not_approved,
        "errors": errors,
        "results": results,
    }
