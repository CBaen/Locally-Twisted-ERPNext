"""Fail if forbidden platform labels return to repo paths or text."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def label(*codes: int) -> str:
    return "".join(chr(code) for code in codes)


FORBIDDEN_LABELS = tuple(
    label(*codes)
    for codes in (
        (111, 100, 111, 111),
        (108, 101, 103, 97, 99, 121, 95, 115, 111, 117, 114, 99, 101),
        (108, 101, 103, 97, 99, 121, 45, 115, 111, 117, 114, 99, 101),
        (108, 101, 103, 97, 99, 121, 32, 115, 111, 117, 114, 99, 101),
        (99, 97, 116, 97, 108, 111, 103, 95, 114, 101, 102, 101, 114, 101, 110, 99, 101),
        (99, 97, 116, 97, 108, 111, 103, 45, 114, 101, 102, 101, 114, 101, 110, 99, 101),
        (99, 97, 116, 97, 108, 111, 103, 32, 114, 101, 102, 101, 114, 101, 110, 99, 101),
        (104, 101, 116, 122, 110, 101, 114),
        (53, 46, 55, 56, 46, 49, 51, 54, 46, 49, 51, 51),
        (114, 101, 116, 105, 114, 101, 100, 45, 115, 111, 117, 114, 99, 101),
        (114, 101, 116, 105, 114, 101, 100, 32, 115, 111, 117, 114, 99, 101),
        (114, 101, 116, 105, 114, 101, 100, 95, 115, 111, 117, 114, 99, 101),
    )
)
SKIP_PARTS = {
    ".git",
    "node_modules",
    "__pycache__",
}
TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".sh",
    ".svg",
    ".toml",
    ".txt",
    ".yml",
}


def repo_files() -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths = []
    for raw in proc.stdout.split(b"\0"):
        if not raw:
            continue
        rel = Path(raw.decode("utf-8", errors="ignore"))
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        full = ROOT / rel
        if full.is_file():
            paths.append(rel)
    return paths


def text_contains_forbidden(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    data = (ROOT / path).read_bytes()
    lowered = data.lower()
    if not any(forbidden.encode("ascii") in lowered for forbidden in FORBIDDEN_LABELS):
        return False
    text = data.decode("utf-8", errors="ignore").lower()
    return any(forbidden in text for forbidden in FORBIDDEN_LABELS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    bad_paths: list[str] = []
    bad_text: list[str] = []

    for rel in repo_files():
        rel_text = rel.as_posix().lower()
        if any(forbidden in rel_text for forbidden in FORBIDDEN_LABELS):
            bad_paths.append(rel.as_posix())
        if text_contains_forbidden(rel):
            bad_text.append(rel.as_posix())

    if bad_paths or bad_text:
        print("FAIL: forbidden platform label found.")
        if bad_paths:
            print("Paths:")
            for path in bad_paths[:50]:
                print(f"  - {path}")
        if bad_text:
            print("Text:")
            for path in bad_text[:50]:
                print(f"  - {path}")
        return 1

    print("PASS: forbidden platform labels absent from repo paths and text.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
