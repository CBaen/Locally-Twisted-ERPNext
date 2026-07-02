#!/usr/bin/env python3
"""Run local browser proof for the multi-color purchasable product tranche.

This is local-only proof. It temporarily opens local ecommerce and applies
`simple_product|checkout` to the six multi-color repair-lane Website Items,
runs the shared Playwright cart/checkout proof with only those products, then
restores the original Website Item contracts and pause state.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTAINER = os.environ.get("LT_FRAPPE_BACKEND_CONTAINER", "locally-twisted-erpnext-v15-backend-1")
SITE = os.environ.get("LT_FRAPPE_SITE", "frontend")
NODE = os.environ.get("LT_NODE_EXE", r"node")
REPORT = "workstreams/ecommerce-audit/multi-color-purchasable-browser-proof-2026-05-17.json"
APPLY_METHOD = "locally_twisted.verify.multi_color_purchasable_browser_support.apply_open_contracts"
RESTORE_METHOD = "locally_twisted.verify.multi_color_purchasable_browser_support.restore_contracts"
PAUSE_METHOD = "locally_twisted.ecommerce_pause.is_ecommerce_paused"
EXPECTED_PRODUCTS = 6
EXPECTED_VIEWPORTS = 2
EXPECTED_COLOR_DRAWERS = 14


class ContractFail(Exception):
    pass


def bench_execute(method: str, *, kwargs: dict[str, Any] | None = None, timeout: int = 90) -> Any:
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "execute",
        method,
    ]
    if kwargs is not None:
        cmd.extend(["--kwargs", repr(kwargs)])
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    if proc.returncode != 0:
        raise ContractFail(f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    text = proc.stdout.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractFail(f"{method} returned non-JSON output: {text}") from exc


def set_pause(paused: bool) -> None:
    value = "1" if paused else "0"
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "set-config", "lt_ecommerce_paused", value],
        text=True,
        capture_output=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise ContractFail(f"set-config lt_ecommerce_paused {value} failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")


def clear_cache() -> None:
    proc = subprocess.run(
        ["python", "scripts/dev/clear_website_cache.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise ContractFail(f"clear website cache failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")


def product_payload(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    products = []
    for row in snapshot.get("products") or []:
        products.append(
            {
                "label": str(row.get("web_item_name") or row.get("item_code")),
                "route": str(row.get("route")),
                "expectedTemplate": str(row.get("item_code")),
            }
        )
    if len(products) != EXPECTED_PRODUCTS:
        raise ContractFail(f"expected {EXPECTED_PRODUCTS} multi-color browser products, found {len(products)}")
    return products


def run_browser_proof(products: list[dict[str, str]], report: str) -> dict[str, Any]:
    env = os.environ.copy()
    env["LT_CHECKOUT_PROOF_PRODUCTS_JSON"] = json.dumps(products, sort_keys=True)
    env["LT_EXPECTED_DIRECT_CHECKOUT_PRODUCT_COUNT"] = str(len(products))
    env["LT_CHECKOUT_PROOF_REPORT"] = report
    proc = subprocess.run(
        [NODE, "scripts/verify/post_import_checkout_proof.js"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=360,
        env=env,
    )
    if proc.returncode != 0:
        raise ContractFail(f"multi-color browser proof failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    print(proc.stdout.strip())
    return validate_report(report)


def validate_report(report: str) -> dict[str, Any]:
    report_path = _rooted(report)
    data = json.loads(report_path.read_text(encoding="utf-8"))
    if data.get("ok") is not True:
        raise ContractFail(f"browser proof report did not return ok: {report_path.relative_to(ROOT)}")
    product_rows = data.get("products") or []
    expected_rows = EXPECTED_PRODUCTS * EXPECTED_VIEWPORTS
    if len(product_rows) != expected_rows:
        raise ContractFail(f"expected {expected_rows} product proof rows, found {len(product_rows)}")

    total_color_drawers = 0
    for row in product_rows:
        color_drawers = row.get("colorDrawers") or []
        if not color_drawers:
            raise ContractFail(f"{row.get('route')} did not prove a visible color drawer")
        total_color_drawers += len(color_drawers)
        configuration = ((row.get("cartLine") or {}).get("configuration") or {})
        recipes = configuration.get("color_recipes") or []
        selected_options = configuration.get("selected_options") or {}
        if not recipes:
            raise ContractFail(f"{row.get('route')} cart line did not preserve color_recipes")
        for drawer in color_drawers:
            axis = drawer.get("axis")
            if axis in selected_options:
                raise ContractFail(f"{row.get('route')} leaked {axis} into selected_options")
            values = [value for recipe in recipes for value in recipe.get("values", [])]
            if drawer.get("value") not in values:
                raise ContractFail(f"{row.get('route')} missing {axis}={drawer.get('value')} in color_recipes")

    if total_color_drawers != EXPECTED_COLOR_DRAWERS:
        raise ContractFail(f"expected {EXPECTED_COLOR_DRAWERS} color drawer proofs, found {total_color_drawers}")
    return {
        "ok": True,
        "product_rows": len(product_rows),
        "color_drawer_proofs": total_color_drawers,
        "viewports": [row.get("viewport", {}).get("name") for row in data.get("viewports") or []],
        "report": str(report_path.relative_to(ROOT)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default=REPORT, help="Write browser proof JSON to this path")
    args = parser.parse_args()

    snapshot: dict[str, Any] | None = None
    original_paused = True
    failures: list[str] = []
    validation: dict[str, Any] | None = None
    try:
        original_paused = bool(bench_execute(PAUSE_METHOD))
        snapshot = bench_execute(APPLY_METHOD)
        if not snapshot or not snapshot.get("ok"):
            raise ContractFail(f"{APPLY_METHOD} did not return ok: {snapshot}")
        set_pause(False)
        clear_cache()
        validation = run_browser_proof(product_payload(snapshot), args.report)
    except ContractFail as exc:
        failures.append(str(exc))
    finally:
        restore_failures = []
        try:
            if snapshot:
                bench_execute(RESTORE_METHOD, kwargs={"snapshot": snapshot})
        except Exception as exc:  # noqa: BLE001 - restore failures must be printed, not hidden.
            restore_failures.append(f"restore Website Item contracts failed: {exc}")
        try:
            set_pause(original_paused)
        except Exception as exc:  # noqa: BLE001
            restore_failures.append(f"restore lt_ecommerce_paused failed: {exc}")
        try:
            clear_cache()
        except Exception as exc:  # noqa: BLE001
            restore_failures.append(f"final cache clear failed: {exc}")
        failures.extend(restore_failures)

    if failures:
        print("[MULTI-COLOR PURCHASABLE BROWSER PROOF] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    report_path = _rooted(args.report)
    print(f"[MULTI-COLOR PURCHASABLE BROWSER PROOF] PASS report={report_path.relative_to(ROOT)}")
    if validation:
        print(f"  product_rows: {validation['product_rows']}")
        print(f"  color_drawer_proofs: {validation['color_drawer_proofs']}")
    print("  restored: Website Item contracts and lt_ecommerce_paused")
    return 0


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
