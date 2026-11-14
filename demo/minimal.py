#!/usr/bin/env python3
"""Tiny offline example of tool output flowing into a gate contract.

It checks only one fixed stdout claim; this is not a receipt verifier or a
security proof. Use run.py for the fuller fixture gate, including its
demo-only HMAC, freshness, and replay checks.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys


def main() -> int:
    completed = subprocess.run(
        [sys.executable, "-c", "print('local demo result')"],
        check=False,
        capture_output=True,
        text=False,
    )
    if completed.returncode != 0:
        print("fixed local demo command failed", file=sys.stderr)
        return 2

    claim_id = "demo.local-output"
    expected_stdout = b"local demo result" + os.linesep.encode("ascii")
    if completed.stdout != expected_stdout:
        print("fixed local demo output did not match the claim", file=sys.stderr)
        return 3

    stdout_hash = "sha256:" + hashlib.sha256(completed.stdout).hexdigest()
    receipt_id = "demo-" + hashlib.sha256(
        claim_id.encode("utf-8") + bytes((0,)) + completed.stdout
    ).hexdigest()[:16]

    warning = (
        "[DEMO ONLY: checked fixed stdout equality; signature, freshness, "
        "and replay are not verified]"
    )
    contract = {
        "contract_version": "0.1",
        "decision": "accept",
        "reason_code": "NO_RISK",
        "detail_code": None,
        "evidence_coverage": 1.0,
        "provenance_summary": {
            "receipts": [
                {
                    "receipt_id": receipt_id,
                    "tool_id": "python.local-demo",
                    "stdout_hash": stdout_hash,
                }
            ],
            "verified_leaves": 1,
            "required_leaves": 1,
        },
        "escalation_path": "none",
    }
    receipt = {
        "receipt_id": receipt_id,
        "claim_id": claim_id,
        "tool_id": "python.local-demo",
        "exit_code": completed.returncode,
        "stdout_hash": stdout_hash,
        "verification_scope": "fixed stdout equality only",
        "verification": "partial",
    }
    result = json.dumps(
        {"receipt": receipt, "contract": contract},
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.buffer.write(
        completed.stdout
        + warning.encode("utf-8")
        + os.linesep.encode("ascii")
        + result.encode("utf-8")
        + os.linesep.encode("ascii")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
