#!/usr/bin/env python3
"""Read-only Meta targeting search probe for LT ad planning.

This answers a narrow planning question: what detailed targeting terms does the
current Meta token return for the missionary balloon ad idea?

The script performs only Graph API GET requests. It does not create or edit
campaigns, ad sets, ads, audiences, budgets, creatives, pixels, datasets,
messages, leads, customer lists, billing, Page settings, or partner access.

Usage:
    python scripts/verify/meta_targeting_probe.py --env-file /path/to/.env
    META_ACCESS_TOKEN="..." python scripts/verify/meta_targeting_probe.py --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


GRAPH_HOST = "https://graph.facebook.com"
DEFAULT_VERSION = "v25.0"
DEFAULT_ENV_FILE = ".env"
DEFAULT_TOKEN_ENV = "META_ACCESS_TOKEN"

RELIGION_CONTEXT_TERMS = (
    "Mormon",
    "Mormons",
    "Mormonism",
    "LDS",
    "LDS Church",
    "Latter-day Saint",
    "Latter-day Saints",
    "Latter Day Saint movement",
    "Church of Jesus Christ of Latter-day Saints",
    "Missionary",
    "Missionary work",
    "Missionaries",
    "Mission call",
    "Return missionary",
    "missionary homecoming",
    "SLC airport",
    "Salt Lake City International Airport",
)

PRODUCT_CONTEXT_TERMS = (
    "Utah",
    "Salt Lake City",
    "Homecoming",
    "Personalized gifts",
    "Gift",
    "Party supply stores",
    "Event management",
)

SUGGESTION_SEEDS = (
    "Utah",
    "Salt Lake City",
    "Gift",
    "Personalised Gifts",
    "Party Supplies",
    "Event management",
)

IRRELEVANT_RELIGION_RESULTS = {
    "The Book of Mormon (musical)",
    "The Book of Mormon on Broadway",
    "Musical theatre",
    "Ryan Reynolds",
}


class MetaReadError(RuntimeError):
    def __init__(self, status: int | None, payload: dict[str, Any] | str):
        self.status = status
        self.payload = payload
        super().__init__(self._format())

    def _format(self) -> str:
        if isinstance(self.payload, dict):
            error = self.payload.get("error") if isinstance(self.payload.get("error"), dict) else {}
            message = error.get("message") or self.payload
            code = error.get("code")
            error_type = error.get("type")
            parts = []
            if self.status:
                parts.append(f"HTTP {self.status}")
            if error_type:
                parts.append(str(error_type))
            if code:
                parts.append(f"code={code}")
            parts.append(str(message))
            return ": ".join(parts)
        prefix = f"HTTP {self.status}: " if self.status else ""
        return prefix + str(self.payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE)
    parser.add_argument("--token-env", default=DEFAULT_TOKEN_ENV)
    parser.add_argument("--api-version", default=DEFAULT_VERSION)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args(argv)

    token = os.environ.get(args.token_env, "").strip() or read_env_value(Path(args.env_file), args.token_env)
    if not token:
        print("[META TARGETING PROBE] BLOCKED")
        print(f"  - {args.token_env} was not found in the shell or {args.env_file}.")
        print("  - No Meta request was made.")
        return 2

    report = run_probe(token=token, version=args.api_version, timeout=args.timeout)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    return 1 if report["failures"] else 0


def run_probe(*, token: str, version: str, timeout: float) -> dict[str, Any]:
    failures: list[str] = []
    religion_results: dict[str, list[dict[str, Any]]] = {}
    product_results: dict[str, list[dict[str, Any]]] = {}
    suggestion_results: dict[str, list[dict[str, Any]]] = {}

    for term in RELIGION_CONTEXT_TERMS:
        try:
            religion_results[term] = search_adinterest(token, version, term, timeout)
        except MetaReadError as exc:
            failures.append(f"{term}: {exc}")
            religion_results[term] = []

    for term in PRODUCT_CONTEXT_TERMS:
        try:
            product_results[term] = search_adinterest(token, version, term, timeout)
        except MetaReadError as exc:
            failures.append(f"{term}: {exc}")
            product_results[term] = []

    for seed in SUGGESTION_SEEDS:
        try:
            suggestion_results[seed] = search_suggestions(token, version, seed, timeout)
        except MetaReadError as exc:
            failures.append(f"{seed} suggestions: {exc}")
            suggestion_results[seed] = []

    usable_religion_hits = [
        {"term": term, **compact_hit(hit)}
        for term, hits in religion_results.items()
        for hit in hits
        if str(hit.get("name") or "") not in IRRELEVANT_RELIGION_RESULTS
    ]

    return {
        "status": "fail" if failures else "pass",
        "method": "GET only",
        "mutation": "none",
        "token_printed": False,
        "api_version": version,
        "religion_context_terms": summarize_results(religion_results),
        "usable_religion_context_hits": usable_religion_hits,
        "product_context_terms": summarize_results(product_results),
        "suggestion_seeds": summarize_results(suggestion_results),
        "recommendation": (
            "Do not use direct Mormon/LDS/Missionary detailed targeting for the first missionary ad."
            if not usable_religion_hits
            else "Review any returned religion-context hits against Meta policy before use."
        ),
        "failures": failures,
    }


def search_adinterest(token: str, version: str, term: str, timeout: float) -> list[dict[str, Any]]:
    payload = graph_get(
        token=token,
        version=version,
        path="search",
        params={"type": "adinterest", "q": term, "limit": "12", "locale": "en_US"},
        timeout=timeout,
    )
    return payload.get("data", []) if isinstance(payload.get("data"), list) else []


def search_suggestions(token: str, version: str, seed: str, timeout: float) -> list[dict[str, Any]]:
    payload = graph_get(
        token=token,
        version=version,
        path="search",
        params={
            "type": "adinterestsuggestion",
            "interest_list": json.dumps([seed]),
            "limit": "12",
            "locale": "en_US",
        },
        timeout=timeout,
    )
    return payload.get("data", []) if isinstance(payload.get("data"), list) else []


def summarize_results(results: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    return {
        term: {
            "count": len(hits),
            "top": [compact_hit(hit) for hit in hits[:5]],
        }
        for term, hits in results.items()
    }


def compact_hit(hit: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": hit.get("name"),
        "id": hit.get("id"),
        "audience": hit.get("audience_size") or hit.get("audience_size_lower_bound"),
        "topic": hit.get("topic"),
        "path": hit.get("path") or [],
    }


def graph_get(
    *,
    token: str,
    version: str,
    path: str,
    params: dict[str, str],
    timeout: float,
) -> dict[str, Any]:
    encoded = dict(params)
    encoded["access_token"] = token
    url = f"{GRAPH_HOST}/{version.strip('/')}/{path.lstrip('/')}?{urllib.parse.urlencode(encoded)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "lt-meta-targeting-probe/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise MetaReadError(exc.code, parse_json_or_text(body)) from None
    except urllib.error.URLError as exc:
        raise MetaReadError(None, str(exc.reason)) from None
    except json.JSONDecodeError as exc:
        raise MetaReadError(None, f"non-JSON response: {exc}") from None

    if not isinstance(payload, dict):
        raise MetaReadError(None, f"expected JSON object, got {type(payload).__name__}")
    if "error" in payload:
        raise MetaReadError(None, payload)
    return payload


def read_env_value(path: Path, key: str) -> str:
    if not path.exists():
        return ""
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        if not line.startswith(key + "="):
            continue
        value = line.split("=", 1)[1].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        return value
    return ""


def parse_json_or_text(value: str) -> dict[str, Any] | str:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return value[:500]
    return parsed if isinstance(parsed, dict) else value[:500]


def print_text(report: dict[str, Any]) -> None:
    print("[META TARGETING PROBE] " + report["status"].upper())
    print(f"  method: {report['method']}")
    print(f"  mutation: {report['mutation']}")
    print(f"  token_printed: {report['token_printed']}")
    print(f"  usable religion-context hits: {len(report['usable_religion_context_hits'])}")
    print(f"  recommendation: {report['recommendation']}")
    print("  religion/context search counts:")
    for term, data in report["religion_context_terms"].items():
        names = ", ".join(str(hit["name"]) for hit in data["top"] if hit.get("name")) or "none"
        print(f"    - {term}: {data['count']} ({names})")
    print("  product/context search counts:")
    for term, data in report["product_context_terms"].items():
        names = ", ".join(str(hit["name"]) for hit in data["top"] if hit.get("name")) or "none"
        print(f"    - {term}: {data['count']} ({names})")
    if report["failures"]:
        print("  failures:")
        for failure in report["failures"]:
            print(f"    - {failure}")


if __name__ == "__main__":
    sys.exit(main())
