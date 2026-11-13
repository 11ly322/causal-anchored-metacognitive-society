#!/usr/bin/env python3
"""Mock-first 10k experiment harness for the audit layer.

`--mock` samples the synthetic benchmark and produces a reproducible
`[设计/假设]` artifact. It is not the preregistered live H1 result.
`--live` is intentionally gated: wire a provider before using it.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bench.run import (  # noqa: E402
    cams_lite,
    calibrate_logprob,
    evaluate,
    load_tasks,
    logprob_gate,
    no_audit,
)
from bench.score import compute_metrics  # noqa: E402

DEFAULT_CONFIG = ROOT / "experiments" / "configs" / "pilot.yaml"
DEFAULT_OUT = ROOT / "experiments" / "results.mock.json"


def load_config(path: Path) -> dict[str, str]:
    config: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        config[key.strip()] = value.strip()
    return config


def mock_run(samples: int, seed: int) -> dict[str, Any]:
    tasks = load_tasks("test")
    if not tasks:
        raise SystemExit("no test tasks")
    rng = random.Random(seed)
    sampled = [rng.choice(tasks) for _ in range(samples)]
    threshold = calibrate_logprob(load_tasks("dev"), 0.80)
    methods = {
        "no_audit": lambda task: no_audit(task),
        "logprob_gate": lambda task: logprob_gate(task, threshold),
        "cams_lite": cams_lite,
    }
    methods_out: dict[str, Any] = {}
    for name, fn in methods.items():
        records = [evaluate(task, fn(task), name) for task in sampled]
        methods_out[name] = compute_metrics(records)
    return {
        "mode": "mock",
        "evidence": "[设计/假设]",
        "note": "Resampled synthetic benchmark; NOT the preregistered live H1.",
        "samples": samples,
        "seed": seed,
        "logprob_threshold": threshold,
        "methods": methods_out,
        "h1_status": "[TBD] live receipts and provider budget required",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--samples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--mock", action="store_true", default=True)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    if args.live:
        print(
            "Live mode is intentionally disabled in v0: no provider key is stored.\n"
            "Set CAMS_API_URL/CAMS_API_KEY and wire run_live() before using this mode.\n"
            "No result was produced; do not report a live number.",
            file=sys.stderr,
        )
        return 2

    payload = mock_run(args.samples, args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
