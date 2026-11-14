#!/usr/bin/env python3
"""Check the standalone consumer against actual offline gate outputs."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ("accept", "accept", "NO_RISK", None, 0),
    ("measurement", "measurement", "MEASUREMENT_FAILURE", "STALE", 2),
    ("insufficient", "insufficient", "INSUFFICIENT_EVIDENCE", "LOW_COVERAGE", 3),
    ("fail-tampered-stdout-hash", "measurement", "MEASUREMENT_FAILURE", "INTEGRITY", 2),
    ("fail-replay-nonce", "measurement", "MEASUREMENT_FAILURE", "REPLAY", 2),
    ("fail-empty-checksum", "measurement", "MEASUREMENT_FAILURE", "SCHEMA", 2),
    ("fail-no-tool", "measurement", "MEASUREMENT_FAILURE", "NO_RECEIPT", 2),
)


def main() -> None:
    env = os.environ.copy()
    env.pop("CAMS_DEMO_HMAC_KEY", None)
    env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    with tempfile.TemporaryDirectory(prefix="contract-consumer-") as folder:
        isolated = Path(folder)
        consumer = isolated / "consume_contract.py"
        shutil.copyfile(ROOT / "demo/consume_contract.py", consumer)

        def consume(data: bytes, *, file_input: bool = False) -> subprocess.CompletedProcess:
            command = [sys.executable, "-I", str(consumer)]
            if file_input:
                path = isolated / "contract.json"
                path.write_bytes(data)
                command += ["--contract", str(path)]
            return subprocess.run(command, input=None if file_input else data,
                                  cwd=isolated, env=env, capture_output=True, timeout=10)

        def check(data: bytes, expected: dict, *, file_input: bool = False) -> None:
            result = consume(data, file_input=file_input)
            assert result.returncode == 0, result.stderr.decode("utf-8")
            assert not result.stderr, result.stderr
            assert json.loads(result.stdout) == expected, result.stdout

        contracts = []
        for name, state, reason, detail, code in CASES:
            direct = subprocess.run(
                [sys.executable, "-I", str(ROOT / "demo/run.py"),
                 "--trace", str(ROOT / f"traces/{name}.json")],
                cwd=ROOT, env=env, capture_output=True, timeout=10,
            )
            assert direct.returncode == code and not direct.stderr, (name, direct.stderr)
            contract = json.loads(direct.stdout)
            expected = {"state": state, "reason_code": reason, "detail_code": detail,
                        "verified_leaves": contract["provenance_summary"]["verified_leaves"]}
            check(direct.stdout, expected)
            check(direct.stdout, expected, file_input=True)
            projection = {key: contract[key] for key in ("decision", "reason_code", "detail_code")}
            projection["provenance_summary"] = {"verified_leaves": expected["verified_leaves"]}
            check(json.dumps(projection).encode(), expected)
            # Irrelevant model fields do not participate in classification.
            noisy = dict(projection, covariance="not read", logprob={"not": "read"},
                         claims="not read", evidence_coverage="not read")
            check(json.dumps(noisy).encode(), expected)
            contracts.append(projection)
        print("PASS: 7 actual gate contracts, stdin/file parity, four-field projection and ignored model fields")
        print("PASS: standalone copy runs with isolated Python; no verifier, traces or repository imports available")

        # Public codes absent from the seven fixtures are projection-only cases.
        for base, state, details in (
            (contracts[1], "measurement", ("SIGNATURE", "TOOL_NOT_ALLOWED")),
            (contracts[2], "insufficient", ("MISSING_EVIDENCE", "OUT_OF_SCOPE")),
        ):
            for detail in details:
                projection = dict(base, detail_code=detail)
                expected = {"state": state, "reason_code": base["reason_code"],
                            "detail_code": detail,
                            "verified_leaves": base["provenance_summary"]["verified_leaves"]}
                check(json.dumps(projection).encode(), expected)
        arguments = subprocess.run(
            [sys.executable, "-I", str(consumer), "--unknown-option"],
            cwd=isolated, env=env, input=b"", capture_output=True, timeout=10,
        )
        assert arguments.returncode == 2 and not arguments.stdout
        assert b"unrecognized arguments" in arguments.stderr and b"Traceback" not in arguments.stderr
        print("PASS: four remaining public detail codes and argument-error exit 2")

        valid = contracts[0]
        invalid = [b"", b"{", b"null", b"[]", b"{}", b"\xff"]
        for key in valid:
            item = dict(valid)
            del item[key]
            invalid.append(json.dumps(item).encode())
        changes = (
            {"decision": "UNKNOWN"}, {"decision": []},
            {"reason_code": "MEASUREMENT_FAILURE"}, {"reason_code": None},
            {"detail_code": "STALE"}, {"detail_code": []},
            {"provenance_summary": []}, {"provenance_summary": {}},
            *({"provenance_summary": {"verified_leaves": count}}
              for count in (-1, True, 0.5, "1", None)),
        )
        for change in changes:
            invalid.append(json.dumps(dict(valid, **change)).encode())
        invalid += [
            json.dumps(dict(contracts[1], detail_code="LOW_COVERAGE")).encode(),
            json.dumps(dict(contracts[2], detail_code="INTEGRITY")).encode(),
            json.dumps(valid).replace('"decision": "accept"',
                                     '"decision": "MEASUREMENT_FAILURE", "decision": "accept"').encode(),
            json.dumps(valid).replace('"verified_leaves": 1',
                                     '"verified_leaves": 0, "verified_leaves": 1').encode(),
            json.dumps(dict(valid, covariance=float("nan"))).encode(),
            b" " * 1_048_577,
            b"[" * 2000 + b"]" * 2000,
        ]
        for number, data in enumerate(invalid, 1):
            result = consume(data)
            assert result.returncode == 1 and not result.stdout, (number, result)
            assert result.stderr.startswith(b"contract consumer: "), (number, result.stderr)
            assert b"Traceback" not in result.stderr, (number, result.stderr)
        missing = subprocess.run(
            [sys.executable, "-I", str(consumer), "--contract", str(isolated / "missing.json")],
            cwd=isolated, env=env, capture_output=True, timeout=10,
        )
        assert missing.returncode == 1 and not missing.stdout and b"Traceback" not in missing.stderr
        print(f"PASS: {len(invalid) + 1} malformed, missing, conflicting or oversized inputs fail without a classification")

        expected = {"state": "accept", "reason_code": "NO_RISK", "detail_code": None, "verified_leaves": 1}
        check(b"\xef\xbb\xbf" + json.dumps(valid).encode(), expected, file_input=True)
        print("PASS: UTF-8 BOM file support for Windows shell output")


if __name__ == "__main__":
    main()
