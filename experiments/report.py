#!/usr/bin/env python3
"""Read a results JSON and print a compact table. No recomputation of truth."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", nargs="?", default="experiments/results.mock.json")
    args = parser.parse_args()
    data = json.loads(Path(args.results).read_text(encoding="utf-8"))
    print(f"mode={data.get('mode')} evidence={data.get('evidence')} n={data.get('samples')}")
    print(f"{'method':14} {'coverage':>9} {'accuracy':>9} {'halluc':>8} {'unnecessary':>12}")
    for name, metrics in data["methods"].items():
        print(
            f"{name:14} {metrics['coverage']:9.3f} {metrics['accuracy']:9.3f} "
            f"{metrics['hallucination_rate']:8.3f} {metrics['unnecessary_abstention_rate']:12.3f}"
        )
    print(f"h1_status={data.get('h1_status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
