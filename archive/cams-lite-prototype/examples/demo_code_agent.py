#!/usr/bin/env python3
"""Offline demo: three claims, one invalid receipt, one accepted, one refused.

Run:
    python examples/demo_code_agent.py --offline
No network, no API key, no model.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cams_lite import Claim, Evidence, ProvenanceTree, coverage_gate
from cams_lite.types import content_checksum


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="use synthetic receipts")
    args = parser.parse_args()
    if not args.offline:
        print("This demo is offline-only by design.", file=sys.stderr)
        return 2

    tree = ProvenanceTree()
    tree.add_many(
        [
            Evidence(
                "receipt:sha",
                "shell",
                json.dumps({"exit": 0, "stdout": "42"}),
                checksum=content_checksum(json.dumps({"exit": 0, "stdout": "42"})),
                non_text=True,
            ),
            Evidence(
                "receipt:forged",
                "sensor",
                "42",
                checksum="sha256:forged",
            ),
        ]
    )

    claims = [
        Claim("c:ok", "The command exited 0 and printed 42.", supports=("receipt:sha",), confidence=0.9),
        Claim("c:forged", "The sensor confirms 42.", supports=("receipt:forged",), confidence=0.8),
        Claim("c:unsupported", "The deploy is safe.", supports=(), confidence=0.7),
    ]

    output = []
    for claim in claims:
        verdict = coverage_gate([claim], tree, answer=claim.text)
        output.append(
            {
                "claim": claim.claim_id,
                "status": verdict.status,
                "reason_code": verdict.reason_code,
                "coverage": verdict.coverage,
                "contract": verdict.contract,
            }
        )

    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
