#!/usr/bin/env python3
"""Verify ERPNext variant prices match catalog source option price modifiers.

Run:
  python scripts/verify/catalog_price_modifier_contract.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.seed.repair_variant_price_modifiers_from_catalog_source.execute"
ROOT = Path(__file__).resolve().parents[2]
HOST_SOURCE_ROOT = ROOT / "_resources" / "catalog-source"
REQUIRED_SOURCE_FILES = ("catalog.json", "value_normalize_map.json")
CONTAINER_SOURCE_ROOTS = (
    "/home/frappe/frappe-bench/apps/locally_twisted/locally_twisted/seed/_data",
    "/workspace/_resources/catalog-source",
    "/home/frappe/frappe-bench/_resources/catalog-source",
    "/home/frappe/frappe-bench/sites/_resources/catalog-source",
)


class ContractFail(Exception):
    pass


class SourceDataUnavailable(ContractFail):
    pass


def _missing_source_hint(text: str) -> bool:
    lowered = text.lower()
    return "_resources/catalog-source not found" in lowered or "bind-mount the project _resources" in lowered


def _check_host_source_packet() -> None:
    missing = [
        str((HOST_SOURCE_ROOT / filename).relative_to(ROOT))
        for filename in REQUIRED_SOURCE_FILES
        if not (HOST_SOURCE_ROOT / filename).exists()
    ]
    if missing:
        raise SourceDataUnavailable(
            "Host catalog source packet is missing required file(s): "
            f"{', '.join(missing)}. This is a source-data blocker, not a catalog price logic failure."
        )


def _container_has_required_files(source_root: str) -> bool:
    for filename in REQUIRED_SOURCE_FILES:
        proc = subprocess.run(
            ["docker", "exec", CONTAINER, "test", "-f", f"{source_root}/{filename}"],
            text=True,
            capture_output=True,
            timeout=30,
        )
        if proc.returncode != 0:
            return False
    return True


def _check_container_source_packet() -> None:
    docker_errors: list[str] = []
    for source_root in CONTAINER_SOURCE_ROOTS:
        try:
            if _container_has_required_files(source_root):
                return
        except (subprocess.SubprocessError, OSError) as exc:
            docker_errors.append(str(exc))

    detail = f"Checked container paths: {', '.join(CONTAINER_SOURCE_ROOTS)}."
    if docker_errors:
        detail += f" Docker check errors: {'; '.join(docker_errors)}."
    raise SourceDataUnavailable(
        "Container-visible catalog source packet is missing or not mounted. "
        "This is a source-data/mount blocker, not a catalog price logic failure. "
        f"{detail} Run `python scripts/setup/stage_seed_data.py` or mount `_resources/catalog-source` into the backend container, then rerun."
    )


def bench_execute(method: str, *, kwargs: dict[str, Any] | None = None, timeout: int = 900) -> Any:
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
        combined = f"{proc.stdout}\n{proc.stderr}"
        if _missing_source_hint(combined):
            raise SourceDataUnavailable(
                "ERPNext price modifier method could not see `_resources/catalog-source` inside the container. "
                "This is a source-data/mount blocker, not a catalog price logic failure.\n"
                f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
            )
        raise ContractFail(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        return parsed
    except json.JSONDecodeError as exc:
        raise ContractFail(f"{method} returned non-JSON output: {text}") from exc


def check_no_catalog_source_price_modifier_drift() -> None:
    _check_host_source_packet()
    _check_container_source_packet()
    data = bench_execute(METHOD, kwargs={"dry_run": True, "strict": False})
    errors = data.get("errors") or []
    if errors:
        details = "; ".join(f"{row.get('template')}: {row.get('error')}" for row in errors)
        if _missing_source_hint(details):
            raise SourceDataUnavailable(
                "ERPNext price modifier method reported missing source data while checking products. "
                "This is a source-data/mount blocker, not a catalog price logic failure: "
                f"{details}"
            )
        raise ContractFail(f"catalog source price modifier probe had errors: {details}")

    products_checked = int(data.get("products_checked") or 0)
    variants_checked = int(data.get("variants_checked") or 0)
    variants_that_would_change = int(data.get("variants_that_would_change") or 0)

    if products_checked < 45:
        raise ContractFail(f"expected broad variant catalog coverage, checked only {products_checked} products")
    if variants_checked < 10000:
        raise ContractFail(f"expected 10k+ active variants checked, got {variants_checked}")
    if variants_that_would_change:
        raise ContractFail(f"{variants_that_would_change} variant prices still differ from catalog source modifiers")

    print(
        "[PASS] catalog source price modifiers match ERPNext Item Prices "
        f"for {products_checked} products / {variants_checked} active variants"
    )


def main() -> int:
    parse_noop_args(__doc__)
    try:
        check_no_catalog_source_price_modifier_drift()
    except SourceDataUnavailable as exc:
        print(f"[FAIL] source_price_modifier_source_data: {exc}")
        print("\n[PRODUCT PRICE MODIFIER CONTRACT] SOURCE DATA BLOCKED")
        return 1
    except Exception as exc:
        print(f"[FAIL] check_no_catalog_source_price_modifier_drift: {exc}")
        print("\n[PRODUCT PRICE MODIFIER CONTRACT] FAIL")
        return 1

    print("\n[PRODUCT PRICE MODIFIER CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
