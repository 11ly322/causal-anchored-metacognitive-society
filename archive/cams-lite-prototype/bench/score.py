#!/usr/bin/env python3
"""Metrics for AgentAudit-Bench v0.

The primary pair is coverage and hallucination among determined outputs.
This is a synthetic benchmark: it is `[实测-合成]`, not evidence for the
preregistered H1, which requires live model/tool receipts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def compute_metrics(records: list[dict[str, Any]]) -> dict[str, float]:
    n = len(records)
    if n == 0:
        return {
            "n": 0,
            "coverage": 0.0,
            "accuracy": 0.0,
            "hallucination_rate": 0.0,
            "determined_error_rate": 0.0,
            "unnecessary_abstention_rate": 0.0,
        }
    determined = [row for row in records if row["determined"]]
    wrong_determined = [row for row in determined if not row["correct"]]
    unnecessary = [row for row in records if row["unnecessary_abstention"]]
    return {
        "n": float(n),
        "coverage": len(determined) / n,
        "accuracy": sum(1 for row in records if row["correct"]) / n,
        "hallucination_rate": (len(wrong_determined) / len(determined)) if determined else 0.0,
        "determined_error_rate": len(wrong_determined) / n,
        "unnecessary_abstention_rate": len(unnecessary) / n,
    }


def h1_like_signal(logprob: dict[str, float], cams: dict[str, float]) -> dict[str, float]:
    """Descriptive only; do not call this the preregistered H1 result."""
    base = logprob.get("hallucination_rate", 0.0)
    if base <= 0:
        return {"relative_hallucination_reduction": 0.0, "coverage_delta_pp": 0.0}
    return {
        "relative_hallucination_reduction": (base - cams.get("hallucination_rate", 0.0)) / base,
        "coverage_delta_pp": (cams.get("coverage", 0.0) - logprob.get("coverage", 0.0)) * 100.0,
    }


def load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", help="path to a results JSON")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    data = load(args.results)
    if "methods" in data:
        print(json.dumps(data["methods"], indent=2))
    else:
        print(json.dumps(compute_metrics(data.get("records", [])), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
