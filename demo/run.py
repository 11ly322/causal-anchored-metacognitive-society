#!/usr/bin/env python3
"""Offline demo for the agent-audit-kernel receipt/gate contract.

Standard library only. No network, no model calls, no third-party packages.

Exit codes:
  0  accept
  2  MEASUREMENT_FAILURE
  3  INSUFFICIENT_EVIDENCE
  4  malformed trace (also reported as MEASUREMENT_FAILURE)
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED = [
    "receipt_id",
    "tool_id",
    "exit_code",
    "stdout_hash",
    "nonce",
    "timestamp",
    "signature",
    "input_digest",
]
ALLOWED_RECEIPT_KEYS = set(REQUIRED) | {"stderr_hash", "metadata"}

HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
RECEIPT_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
NONCE_RE = re.compile(r"^[A-Za-z0-9_-]{16,64}$")
SIG_RE = re.compile(r"^hmac-sha256:[0-9a-f]{64}$")

DEFAULT_KEY = "demo-key-not-secret"


class TraceError(Exception):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_tag(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sign_receipt(receipt: dict[str, Any], key: bytes) -> str:
    payload = {k: v for k, v in receipt.items() if k != "signature"}
    message = b"agent-audit-receipt-v1\n" + canonical(payload)
    return "hmac-sha256:" + hmac.new(key, message, hashlib.sha256).hexdigest()


def parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise TraceError("timestamp is not a string")
    text = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise TraceError("timestamp has no timezone")
    return parsed.astimezone(timezone.utc)


def load_trace(path: str) -> dict[str, Any]:
    raw = Path(path).read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise TraceError("trace root is not an object")
    return data


def validate_shape(receipt: dict[str, Any]) -> None:
    if not isinstance(receipt, dict):
        raise TraceError("receipt is not an object")
    extra = set(receipt) - ALLOWED_RECEIPT_KEYS
    if extra:
        raise TraceError(f"unknown receipt fields: {sorted(extra)}")
    for field in REQUIRED:
        if field not in receipt or receipt[field] in ("", None):
            raise TraceError(f"missing or empty field: {field}")
    if not isinstance(receipt["receipt_id"], str) or not RECEIPT_ID_RE.match(receipt["receipt_id"]):
        raise TraceError("bad receipt_id")
    if not isinstance(receipt["tool_id"], str) or not receipt["tool_id"]:
        raise TraceError("bad tool_id")
    if isinstance(receipt["exit_code"], bool) or not isinstance(receipt["exit_code"], int):
        raise TraceError("exit_code must be an integer")
    if not 0 <= receipt["exit_code"] <= 255:
        raise TraceError("exit_code out of range")
    if not isinstance(receipt["stdout_hash"], str) or not HASH_RE.match(receipt["stdout_hash"]):
        raise TraceError("bad stdout_hash")
    if not isinstance(receipt["nonce"], str) or not NONCE_RE.match(receipt["nonce"]):
        raise TraceError("bad nonce")
    parse_timestamp(receipt["timestamp"])
    if not isinstance(receipt["signature"], str) or not SIG_RE.match(receipt["signature"]):
        raise TraceError("bad signature")
    if not isinstance(receipt["input_digest"], str) or not HASH_RE.match(receipt["input_digest"]):
        raise TraceError("bad input_digest")
    if "stderr_hash" in receipt and not HASH_RE.match(receipt["stderr_hash"]):
        raise TraceError("bad stderr_hash")
    if "metadata" in receipt and not isinstance(receipt["metadata"], dict):
        raise TraceError("metadata must be an object")


def verify_receipt(
    receipt: dict[str, Any],
    tool: dict[str, Any],
    now: datetime,
    key: bytes,
    policy: dict[str, Any],
    seen_nonces: set[str],
    seen_ids: set[str],
) -> tuple[bool, str | None, str]:
    try:
        validate_shape(receipt)
    except TraceError as exc:
        return False, "SCHEMA", str(exc)

    if receipt["tool_id"] != tool.get("tool_id"):
        return False, "INTEGRITY", "receipt tool_id does not match tool call"
    if receipt["exit_code"] != tool.get("exit_code"):
        return False, "INTEGRITY", "receipt exit_code does not match tool call"

    stdout = tool.get("stdout", "")
    if not isinstance(stdout, str):
        return False, "SCHEMA", "tool stdout must be a string"
    expected_stdout = sha256_tag(stdout.encode("utf-8"))
    if not hmac.compare_digest(receipt["stdout_hash"], expected_stdout):
        return False, "INTEGRITY", "stdout_hash does not match captured stdout"

    input_payload = {
        "tool_id": tool.get("tool_id"),
        "args": tool.get("args", []),
        "stdin": tool.get("stdin"),
    }
    expected_input = sha256_tag(canonical(input_payload))
    if not hmac.compare_digest(receipt["input_digest"], expected_input):
        return False, "INTEGRITY", "input_digest does not match tool input"

    expected_sig = sign_receipt(receipt, key)
    if not hmac.compare_digest(receipt["signature"], expected_sig):
        return False, "SIGNATURE", "signature mismatch"

    try:
        stamp = parse_timestamp(receipt["timestamp"])
    except TraceError as exc:
        return False, "SCHEMA", str(exc)

    age = (now - stamp).total_seconds()
    max_age = int(policy.get("max_age_seconds", 300))
    future_skew = int(policy.get("future_skew_seconds", 60))
    if age > max_age:
        return False, "STALE", f"receipt is {age:.0f}s old"
    if -age > future_skew:
        return False, "STALE", f"receipt is {-age:.0f}s in the future"

    if receipt["nonce"] in seen_nonces:
        return False, "REPLAY", "nonce already used"
    if receipt["receipt_id"] in seen_ids:
        return False, "REPLAY", "receipt_id already used"
    seen_nonces.add(receipt["nonce"])
    seen_ids.add(receipt["receipt_id"])
    return True, None, "ok"


def make_contract(
    decision: str,
    reason_code: str,
    detail_code: str | None,
    coverage: float,
    verified: list[dict[str, Any]],
    required_leaves: int,
    escalation_path: str,
) -> dict[str, Any]:
    return {
        "contract_version": "0.1",
        "decision": decision,
        "reason_code": reason_code,
        "detail_code": detail_code,
        "evidence_coverage": round(max(0.0, min(1.0, coverage)), 6),
        "provenance_summary": {
            "receipts": [
                {
                    "receipt_id": item["receipt_id"],
                    "tool_id": item["tool_id"],
                    "stdout_hash": item["stdout_hash"],
                }
                for item in verified
            ],
            "verified_leaves": len(verified),
            "required_leaves": required_leaves,
        },
        "escalation_path": escalation_path,
    }


def gate(trace: dict[str, Any]) -> tuple[dict[str, Any], int]:
    policy = trace.get("policy", {})
    if not isinstance(policy, dict):
        raise TraceError("policy must be an object")

    clock_mode = policy.get("clock_mode", "real")
    if clock_mode == "fixture":
        now = parse_timestamp(trace.get("fixture_now"))
    elif clock_mode == "real":
        now = datetime.now(timezone.utc)
    else:
        raise TraceError("clock_mode must be real or fixture")

    tool = trace.get("tool", {})
    if not isinstance(tool, dict):
        raise TraceError("tool must be an object")
    receipt = trace.get("receipt")
    claims = trace.get("claims")
    if not isinstance(claims, list) or not claims:
        raise TraceError("claims must be a non-empty list")

    key = os.environ.get("CAMS_DEMO_HMAC_KEY", DEFAULT_KEY).encode("utf-8")
    seen_nonces: set[str] = set()
    seen_ids: set[str] = set()
    verified: dict[str, dict[str, Any]] = {}
    verified_list: list[dict[str, Any]] = []

    if receipt is None:
        decision = "MEASUREMENT_FAILURE"
        contract = make_contract(
            decision, decision, "NO_RECEIPT", 0.0, [], 0, "retry_tool"
        )
        return contract, 2

    if not isinstance(receipt, dict):
        raise TraceError("receipt must be an object")

    ok, detail, message = verify_receipt(
        receipt, tool, now, key, policy, seen_nonces, seen_ids
    )
    if not ok:
        decision = "MEASUREMENT_FAILURE"
        escalation = "human_review" if detail in {"SIGNATURE", "REPLAY"} else "retry_tool"
        contract = make_contract(
            decision, decision, detail, 0.0, [], 0, escalation
        )
        contract["message"] = message
        return contract, 2

    verified[receipt["receipt_id"]] = receipt
    verified_list.append(receipt)

    allowed_tools = policy.get("allowed_tools", [])
    if allowed_tools and receipt["tool_id"] not in allowed_tools:
        contract = make_contract(
            "MEASUREMENT_FAILURE",
            "MEASUREMENT_FAILURE",
            "TOOL_NOT_ALLOWED",
            0.0,
            [],
            0,
            "human_review",
        )
        return contract, 2

    allowed_scopes = set(policy.get("allowed_scopes", []))
    required_claims = [c for c in claims if isinstance(c, dict) and c.get("required", True)]
    if not required_claims:
        contract = make_contract(
            "INSUFFICIENT_EVIDENCE",
            "INSUFFICIENT_EVIDENCE",
            "MISSING_EVIDENCE",
            0.0,
            verified_list,
            0,
            "human_review",
        )
        return contract, 3

    total_leaves = 0
    verified_leaves = 0
    for claim in required_claims:
        evidence = claim.get("evidence", [])
        scope = claim.get("scope", "")
        if allowed_scopes and scope not in allowed_scopes:
            contract = make_contract(
                "INSUFFICIENT_EVIDENCE",
                "INSUFFICIENT_EVIDENCE",
                "OUT_OF_SCOPE",
                0.0,
                verified_list,
                0,
                "human_review",
            )
            return contract, 3
        if not isinstance(evidence, list) or not evidence:
            contract = make_contract(
                "INSUFFICIENT_EVIDENCE",
                "INSUFFICIENT_EVIDENCE",
                "MISSING_EVIDENCE",
                0.0,
                verified_list,
                0,
                "human_review",
            )
            return contract, 3
        for receipt_id in evidence:
            total_leaves += 1
            if receipt_id in verified:
                verified_leaves += 1

    coverage = (verified_leaves / total_leaves) if total_leaves else 0.0
    min_coverage = float(policy.get("min_coverage", 0.80))
    if coverage < min_coverage:
        contract = make_contract(
            "INSUFFICIENT_EVIDENCE",
            "INSUFFICIENT_EVIDENCE",
            "LOW_COVERAGE",
            coverage,
            verified_list,
            total_leaves,
            "human_review",
        )
        return contract, 3

    contract = make_contract(
        "accept",
        "NO_RISK",
        None,
        coverage,
        verified_list,
        total_leaves,
        "none",
    )
    return contract, 0


def main() -> int:
    parser = argparse.ArgumentParser(description="agent-audit-kernel offline demo")
    parser.add_argument("--trace", required=True, help="path to a trace JSON")
    args = parser.parse_args()
    try:
        trace = load_trace(args.trace)
        contract, code = gate(trace)
    except (OSError, json.JSONDecodeError, TraceError, TypeError, ValueError) as exc:
        contract = make_contract(
            "MEASUREMENT_FAILURE",
            "MEASUREMENT_FAILURE",
            "SCHEMA",
            0.0,
            [],
            0,
            "human_review",
        )
        contract["message"] = str(exc)
        print(json.dumps(contract, indent=2, ensure_ascii=False))
        return 4
    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
