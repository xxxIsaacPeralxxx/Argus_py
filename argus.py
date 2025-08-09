"""Command line entry point for the Argus analyzer.

This small script acts as a thin wrapper around
``fls_intel_analyzer.analyze_text``.  It accepts a path to an
input text file and optional parameters controlling the fuzzy logic
system.  The produced analysis is written as JSON next to the input
file.  On success the location of the generated JSON file is printed to
``stdout``; otherwise a clear error message is printed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _parse_args() -> argparse.Namespace:
    """Return CLI arguments for the Argus entry point."""
    parser = argparse.ArgumentParser(description="Run the Argus analyzer")
    parser.add_argument("input", help="Path to the text file to analyse")
    parser.add_argument(
        "--source-reliability",
        type=float,
        default=1.0,
        help="Reliability of the source in [0,1]",
    )
    parser.add_argument(
        "--tnorm",
        choices=["min", "product", "lukasiewicz"],
        default="min",
        help="T-norm used by the FLS algorithm",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point for running analysis from the command line."""
    args = _parse_args()

    try:
        from fls_intel_analyzer import analyze_text
    except Exception as exc:  # pragma: no cover - runtime dependency
        print(f"Error: {exc}")
        return 1

    input_path = Path(args.input)
    try:
        text = input_path.read_text(encoding="utf8")
    except OSError as exc:
        print(f"Error reading input file: {exc}")
        return 1

    bundle: dict[str, Any] = analyze_text(text, tnorm=args.tnorm)
    bundle["source_reliability"] = args.source_reliability

    output_path = input_path.with_suffix(".analysis.json")
    try:
        output_path.write_text(json.dumps(bundle, indent=2), encoding="utf8")
    except OSError as exc:
        print(f"Error writing output file: {exc}")
        return 1

    print(f"Analysis written to {output_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())

