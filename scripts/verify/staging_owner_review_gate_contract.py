#!/usr/bin/env python3
"""Offline contract for the Frappe Cloud staging owner-review gate.

This contract proves the gate logic with fake Frappe Cloud/staging fixtures.
It must not read credentials, call provider APIs, or touch a real staging site.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

import staging_owner_review_gate as gate


EXPECTED_HASH = "a" * 40
WRONG_HASH = "b" * 40
STALE_BOOTSTRAP_HASH = "c" * 40


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable contract results.")
    args = parser.parse_args()

    result = run_contract()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[STAGING OWNER REVIEW GATE CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for case in result["cases"]:
            print(f"  - {case['name']}: {case['status']}")
        for failure in result["failures"]:
            print(f"    - {failure}")
    return 0 if result["ok"] else 1


def run_contract() -> dict[str, Any]:
    cases = [
        ContractCase("valid_fixture", expect_ok=True),
        ContractCase(
            "zero_catalog_rows",
            expect_ok=False,
            mutate=zero_catalog_rows,
            expected_failures=["Website Item count 0 is below required minimum"],
        ),
        ContractCase(
            "missing_owner_and_marketing_users",
            expect_ok=False,
            mutate=missing_required_users,
            expected_failures=[
                "required staging user missing: locallytwisted@gmail.com",
                "required staging user missing: marketing@exploringnotboring.com",
            ],
        ),
        ContractCase(
            "wrong_app_order",
            expect_ok=False,
            mutate=wrong_app_order,
            expected_failures=["installed app order drifted:"],
        ),
        ContractCase(
            "wrong_installed_app_hash",
            expect_ok=False,
            mutate=wrong_installed_app_hash,
            expected_failures=[f"locally_twisted hash {WRONG_HASH} != expected {EXPECTED_HASH}"],
        ),
        ContractCase(
            "stale_bootstrap_hash",
            expect_ok=False,
            mutate=stale_bootstrap_hash,
            expected_failures=[
                "bootstrap status is not bound to the deployed app hash: "
                f"{STALE_BOOTSTRAP_HASH} != {EXPECTED_HASH}"
            ],
        ),
        ContractCase(
            "ecommerce_indexing_exposure_mismatch",
            expect_ok=False,
            mutate=ecommerce_indexing_exposure_mismatch,
            expected_failures=[
                "lt_ecommerce_paused is not enabled on staging",
                "lt_public_indexing_enabled is not disabled on staging",
                "/shop still resolves to paused page for authenticated owner/admin proof",
            ],
        ),
    ]

    failures: list[str] = []
    case_results = []
    for case in cases:
        case_result = run_case(case)
        case_results.append(case_result)
        failures.extend(case_result["contract_failures"])

    return {
        "ok": not failures,
        "failures": failures,
        "cases": case_results,
    }


class ContractCase:
    def __init__(
        self,
        name: str,
        *,
        expect_ok: bool,
        mutate: Callable[[dict[str, Any]], None] | None = None,
        expected_failures: list[str] | None = None,
    ) -> None:
        self.name = name
        self.expect_ok = expect_ok
        self.mutate = mutate
        self.expected_failures = expected_failures or []


def run_case(case: ContractCase) -> dict[str, Any]:
    fixture = valid_fixture()
    if case.mutate:
        case.mutate(fixture)

    try:
        with patched_gate(fixture):
            gate_result = gate.run_gate(fake_args())
    except Exception as exc:
        return {
            "name": case.name,
            "status": "FAIL",
            "gate_ok": False,
            "gate_failures": [],
            "contract_failures": [f"{case.name}: gate crashed with {type(exc).__name__}: {exc}"],
        }

    gate_ok = bool(gate_result["ok"])
    gate_failures = list(gate_result["failures"])
    contract_failures: list[str] = []
    if gate_ok != case.expect_ok:
        contract_failures.append(
            f"{case.name}: expected gate ok={case.expect_ok}, found ok={gate_ok}; "
            f"failures={gate_failures}"
        )
    for expected in case.expected_failures:
        if not any(expected in failure for failure in gate_failures):
            contract_failures.append(
                f"{case.name}: expected failure containing {expected!r}; found {gate_failures}"
            )

    return {
        "name": case.name,
        "status": "PASS" if not contract_failures else "FAIL",
        "gate_ok": gate_ok,
        "gate_failures": gate_failures,
        "contract_failures": contract_failures,
    }


def fake_args() -> argparse.Namespace:
    return argparse.Namespace(
        site="fake-staging.local",
        team="fake-team",
        credentials=Path("missing-credentials-must-not-be-read.txt"),
        expected_hash=EXPECTED_HASH,
        expected_hash_from_mirror=False,
        mirror_url="https://example.invalid/fake.git",
        json=False,
    )


class patched_gate:
    def __init__(self, fixture: dict[str, Any]) -> None:
        self.fixture = fixture
        self.originals: dict[str, Any] = {}

    def __enter__(self) -> None:
        replacements = {
            "PressClient": self.fake_press_client_class(),
            "staging_session": lambda _press, _site: {"session": "fake"},
            "stage_get_count": self.fake_stage_get_count,
            "stage_get_user": self.fake_stage_get_user,
            "fetch_route": self.fake_fetch_route,
            "stage_method": self.fake_stage_method,
            "request_json": self.fail_if_network_reached,
        }
        for name, replacement in replacements.items():
            self.originals[name] = getattr(gate, name)
            setattr(gate, name, replacement)

    def __exit__(self, _exc_type: Any, _exc: Any, _tb: Any) -> None:
        for name, original in self.originals.items():
            setattr(gate, name, original)

    def fake_press_client_class(self) -> type:
        fixture = self.fixture

        class FakePressClient:
            def __init__(self, _credentials: Path, team: str) -> None:
                self.team = team

            def get(self, method: str, _params: dict[str, Any]) -> dict[str, Any]:
                if method == "press.api.site.get":
                    return {"message": copy.deepcopy(fixture["site"])}
                if method == "press.api.site.installed_apps":
                    return {"message": copy.deepcopy(fixture["apps"])}
                if method == "press.api.site.site_config":
                    return {
                        "message": [
                            {"key": key, "value": value}
                            for key, value in fixture["config"].items()
                        ]
                    }
                raise AssertionError(f"unexpected fake PressClient.get method: {method}")

            def post_json(self, method: str, _payload: dict[str, Any]) -> dict[str, Any]:
                raise AssertionError(f"unexpected fake PressClient.post_json method: {method}")

        return FakePressClient

    def fake_stage_get_count(
        self,
        _site: str,
        _session: object,
        doctype: str,
    ) -> int:
        return self.fixture["counts"][doctype]

    def fake_stage_get_user(
        self,
        _site: str,
        _session: object,
        email: str,
    ) -> dict[str, Any]:
        return copy.deepcopy(self.fixture["accounts"][email])

    def fake_fetch_route(
        self,
        _site: str,
        _session: object,
        path: str,
    ) -> dict[str, Any]:
        return copy.deepcopy(self.fixture["routes"][path])

    def fake_stage_method(
        self,
        _site: str,
        _session: object,
        method: str,
        _params: dict[str, Any],
    ) -> dict[str, Any]:
        expected_method = (
            "locally_twisted.staging_owner_review_bootstrap."
            "get_staging_owner_review_bootstrap_status"
        )
        if method != expected_method:
            raise AssertionError(f"unexpected fake stage_method method: {method}")
        return {"message": copy.deepcopy(self.fixture["bootstrap_status"])}

    def fail_if_network_reached(self, url: str, **_kwargs: Any) -> dict[str, Any]:
        raise AssertionError(f"network helper should not be reached by contract fixture: {url}")


def valid_fixture() -> dict[str, Any]:
    routes = {path: base_route(path) for path in gate.OWNER_VISIBLE_ROUTES}
    routes["/shop-items/bouquets/mickey-mouse-bouquet"].update(
        {
            "has_gallery_shell": True,
            "thumbnail_count": 3,
            "thumbnail_paths": [
                "/files/mickey-mouse-bouquet.png",
                "/files/mickey-mouse-bouquet-large.webp",
                "/files/mickey-mouse-bouquet-review.webp",
            ],
        }
    )
    routes["/shop-items/arches/classic-arch"].update(
        {
            "has_gallery_shell": True,
            "thumbnail_count": 12,
            "thumbnail_paths": ["/files/classic-arch.png"]
            + [f"/files/classic-arch-{index:02d}.webp" for index in range(1, 12)],
        }
    )
    routes["/shop-items/garlands/large-garland"].update(
        {
            "has_gallery_shell": True,
            "thumbnail_count": 2,
            "thumbnail_paths": [
                "/files/large-garland.png",
                "/files/large-garland-side.webp",
            ],
        }
    )
    routes["/shop-items/columns"]["looks_like_category"] = True

    return {
        "site": {"name": "fake-staging.local", "status": "Active", "group": "fake-bench"},
        "apps": [
            {"app": "frappe", "hash": "f" * 40},
            {"app": "erpnext", "hash": "e" * 40},
            {"app": "payments", "hash": "d" * 40},
            {"app": "webshop", "hash": "c" * 40},
            {
                "app": "locally_twisted",
                "hash": EXPECTED_HASH,
                "commit_message": "fake owner-review fixture",
                "branch": "main",
                "repository": "https://example.invalid/Locally-Twisted-Frappe-App.git",
            },
        ],
        "config": {
            "lt_ecommerce_paused": "1",
            "lt_public_indexing_enabled": "0",
        },
        "counts": {doctype: minimum for doctype, minimum in gate.MIN_COUNTS.items()},
        "accounts": {
            email: {
                "exists": True,
                "enabled": 1,
                "user_type": "System User",
                "roles": sorted(required_roles),
            }
            for email, required_roles in gate.REQUIRED_USERS.items()
        },
        "routes": routes,
        "bootstrap_status": {
            "status": {
                "state": "success",
                "expected_app_hash": EXPECTED_HASH,
            }
        },
    }


def base_route(path: str) -> dict[str, Any]:
    return {
        "path": path,
        "status": 200,
        "final_url": f"https://fake-staging.local{path}",
        "title": "Fake owner review route",
        "login_page": False,
        "has_gallery_shell": False,
        "thumbnail_count": 0,
        "thumbnail_paths": [],
        "looks_like_category": False,
    }


def zero_catalog_rows(fixture: dict[str, Any]) -> None:
    for doctype in gate.MIN_COUNTS:
        fixture["counts"][doctype] = 0


def missing_required_users(fixture: dict[str, Any]) -> None:
    for email in gate.REQUIRED_USERS:
        fixture["accounts"][email] = {
            "exists": False,
            "enabled": 0,
            "user_type": None,
            "roles": [],
        }


def wrong_app_order(fixture: dict[str, Any]) -> None:
    fixture["apps"] = [
        fixture["apps"][0],
        fixture["apps"][1],
        fixture["apps"][2],
        fixture["apps"][4],
        fixture["apps"][3],
    ]


def wrong_installed_app_hash(fixture: dict[str, Any]) -> None:
    for app in fixture["apps"]:
        if app["app"] == "locally_twisted":
            app["hash"] = WRONG_HASH
            return


def stale_bootstrap_hash(fixture: dict[str, Any]) -> None:
    fixture["bootstrap_status"]["status"]["expected_app_hash"] = STALE_BOOTSTRAP_HASH


def ecommerce_indexing_exposure_mismatch(fixture: dict[str, Any]) -> None:
    fixture["config"]["lt_ecommerce_paused"] = "0"
    fixture["config"]["lt_public_indexing_enabled"] = "1"
    fixture["routes"]["/shop"]["final_url"] = "https://fake-staging.local/paused"


if __name__ == "__main__":
    sys.exit(main())
