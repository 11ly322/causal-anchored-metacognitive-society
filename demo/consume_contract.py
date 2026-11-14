#!/usr/bin/env python3
"""Classify the public v0 contract fields without importing or rerunning the gate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

MAX_INPUT_BYTES = 1_048_576
STATES = {
    "accept": ("accept", "NO_RISK", {None}),
    "MEASUREMENT_FAILURE": (
        "measurement", "MEASUREMENT_FAILURE",
        {"NO_RECEIPT", "SCHEMA", "INTEGRITY", "SIGNATURE", "STALE", "REPLAY", "TOOL_NOT_ALLOWED"},
    ),
    "INSUFFICIENT_EVIDENCE": (
        "insufficient", "INSUFFICIENT_EVIDENCE",
        {"MISSING_EVIDENCE", "OUT_OF_SCOPE", "LOW_COVERAGE"},
    ),
}


class ContractError(ValueError):
    """The selected public fields cannot be classified unambiguously."""


def classify_contract(contract: object) -> dict:
    """Read decision, reason_code, detail_code and verified_leaves only.

    This validates the consumer's projection, not the full contract schema,
    evidence authenticity, or correctness of the producer's decision.
    """
    if not isinstance(contract, dict):
        raise ContractError("contract must be a JSON object")
    required = {"decision", "reason_code", "detail_code", "provenance_summary"}
    if not required.issubset(contract):
        raise ContractError("missing required contract fields")
    decision = contract["decision"]
    if not isinstance(decision, str) or decision not in STATES:
        raise ContractError("unknown decision")
    state, reason, details = STATES[decision]
    if contract["reason_code"] != reason:
        raise ContractError("reason_code conflicts with decision")
    detail = contract["detail_code"]
    if (detail is not None and not isinstance(detail, str)) or detail not in details:
        raise ContractError("detail_code conflicts with decision")
    provenance = contract["provenance_summary"]
    if not isinstance(provenance, dict):
        raise ContractError("provenance_summary must be an object")
    count = provenance.get("verified_leaves")
    if type(count) is not int or count < 0:
        raise ContractError("verified_leaves must be a nonnegative integer")
    return {"state": state, "reason_code": reason, "detail_code": detail,
            "verified_leaves": count}


def unique_fields(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("duplicate JSON member")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ContractError("NaN and Infinity are not JSON values")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default="-", help="UTF-8 contract file, or - for stdin (default)")
    args = parser.parse_args()
    try:
        if args.contract == "-":
            raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        else:
            with Path(args.contract).open("rb") as source:
                raw = source.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise ContractError("contract exceeds 1048576 bytes")
        contract = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_fields,
                              parse_constant=reject_constant)
        result = classify_contract(contract)
    except (OSError, ValueError, RecursionError) as error:
        print(f"contract consumer: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
