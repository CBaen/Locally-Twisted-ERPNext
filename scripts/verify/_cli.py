"""Shared CLI helpers for LT verifier scripts."""
from __future__ import annotations

import argparse
from typing import Sequence


def parse_noop_args(description: str | None = None, argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Give no-argument verifiers safe --help behavior before live checks run."""
    parser = argparse.ArgumentParser(
        description=(description or "").strip() or None,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    return parser.parse_args(argv)
