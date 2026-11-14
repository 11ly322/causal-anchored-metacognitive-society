#!/usr/bin/env python3
"""Export the seven public offline fixtures for the static Pages presenter.

The existing demo/run.py subprocess owns every verdict. This exporter never
reimplements receipt checks and never executes the tool recorded in a trace.
Only the Python standard library is required.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/11ly322/causal-anchored-metacognitive-society"
ASSETS = ("index.html", "styles.css", "app.js")
CASES = (
    ("accept", "接受声明", "有效回执覆盖了这个演示声明。", "accept", None, 0),
    ("measurement", "回执过期", "固定时钟下，回执超过允许的时间窗口。", "MEASUREMENT_FAILURE", "STALE", 2),
    ("insufficient", "证据不足", "回执通过验证，但必填声明的证据覆盖不足。", "INSUFFICIENT_EVIDENCE", "LOW_COVERAGE", 3),
    ("fail-tampered-stdout-hash", "输出被改动", "记录的工具输出与回执中的摘要不一致。", "MEASUREMENT_FAILURE", "INTEGRITY", 2),
    ("fail-replay-nonce", "重复 nonce", "同一次 verifier 调用内，两份回执使用相同 nonce。", "MEASUREMENT_FAILURE", "REPLAY", 2),
    ("fail-empty-checksum", "空摘要", "回执中的空摘要未通过字段检查。", "MEASUREMENT_FAILURE", "SCHEMA", 2),
    ("fail-no-tool", "缺少回执", "策略要求工具证据，但输入没有回执。", "MEASUREMENT_FAILURE", "NO_RECEIPT", 2),
)


class BuildError(Exception):
    """A source or recorded observation does not meet the publication contract."""


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, check=True,
        encoding="utf-8", timeout=20,
    )
    return result.stdout.strip()


def source_file(relative: str, directory: str) -> Path:
    """Admit regular checkout files without following links or junctions."""
    root = ROOT.resolve(strict=True)
    path = root / relative
    expected = root / directory
    if not path.is_relative_to(expected):
        raise BuildError(f"{relative}: source is outside {directory}/")
    for item in (path, *path.parents):
        if item == root:
            break
        if item.is_symlink() or item.is_junction():
            raise BuildError(f"{relative}: linked source paths are not allowed")
    if not path.resolve(strict=True).is_relative_to(expected) or not path.is_file():
        raise BuildError(f"{relative}: expected a regular file in {directory}/")
    return path


def observe(case: tuple) -> dict:
    case_id, label, explanation, decision, detail, exit_code = case
    source_path = f"traces/{case_id}.json"
    source = source_file(source_path, "traces").read_bytes()
    verifier = source_file("demo/run.py", "demo")
    trace_raw = source.decode("utf-8")
    trace = json.loads(trace_raw)
    if trace.get("expected") != {"decision": decision, "detail_code": detail}:
        raise BuildError(f"{source_path}: expected fields disagree with approved cases")
    if trace.get("policy", {}).get("clock_mode") != "fixture" or not trace.get("fixture_now"):
        raise BuildError(f"{source_path}: a fixed fixture clock is required")

    environment = os.environ.copy()
    environment.pop("CAMS_DEMO_HMAC_KEY", None)
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    process = subprocess.run(
        [sys.executable, str(verifier), "--trace", source_path],
        cwd=ROOT, env=environment, capture_output=True, timeout=20,
    )
    stdout = process.stdout.decode("utf-8")
    stderr = process.stderr.decode("utf-8")
    try:
        contract = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise BuildError(f"{source_path}: verifier did not return a JSON contract") from error
    if not isinstance(contract, dict):
        raise BuildError(f"{source_path}: verifier contract must be an object")
    actual = (contract.get("decision"), contract.get("detail_code"), process.returncode)
    if actual != (decision, detail, exit_code) or stderr:
        raise BuildError(
            f"{source_path}: expected {(decision, detail, exit_code)!r}, "
            f"observed {actual!r}; stderr={stderr!r}"
        )
    return {
        "id": case_id,
        "label": label,
        "explanation": explanation,
        "source_path": source_path,
        "source_sha256": sha256(source),
        "command": f"python demo/run.py --trace {source_path}",
        "exit_code": process.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "contract": contract,
        "trace": trace,
        "trace_raw": trace_raw,
    }


def build() -> dict:
    assets = {name: source_file(f"site/{name}", "site").read_bytes() for name in ASSETS}
    verifier_source = source_file("demo/run.py", "demo").read_bytes()
    commit = git("rev-parse", "HEAD")
    records = [observe(case) for case in CASES]
    for record in records:
        record["source_url"] = f"{REPOSITORY}/blob/{commit}/{record['source_path']}"
    data = {
        "schema_version": 1,
        "build": {
            "commit": commit,
            "dirty": bool(git("status", "--porcelain", "--untracked-files=normal")),
            "verifier_path": "demo/run.py",
            "verifier_url": f"{REPOSITORY}/blob/{commit}/demo/run.py",
            "verifier_sha256": sha256(verifier_source),
            "python_version": sys.version.split()[0],
        },
        "evidence": {"kind": "offline-fixture", "clock_mode": "fixture", "live": False},
        "fixtures": records,
    }
    output = ROOT / "_site"
    permitted = {"index.html", "styles.css", "app.js", ".nojekyll", "data/fixtures.json"}
    if output.is_symlink() or output.is_junction():
        raise BuildError("_site must not be a link or junction")
    if output.exists():
        unexpected = []
        directories = [output]
        while directories:
            for path in directories.pop().iterdir():
                relative = path.relative_to(output).as_posix()
                if path.is_symlink() or path.is_junction():
                    unexpected.append(relative)
                elif path.is_dir() and relative == "data":
                    directories.append(path)
                elif not path.is_file() or relative not in permitted:
                    unexpected.append(relative)
        if unexpected:
            raise BuildError(f"_site contains unexpected public files: {unexpected!r}")
    # Nothing is published or overwritten until every fixture has matched.
    (output / "data").mkdir(parents=True, exist_ok=True)
    for name, content in assets.items():
        (output / name).write_bytes(content)
    (output / ".nojekyll").write_text("", encoding="utf-8")
    (output / "data" / "fixtures.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n",
    )
    return data


def main() -> int:
    try:
        data = build()
    except (BuildError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"site build failed: {error}", file=sys.stderr)
        return 1
    print(f"site build: {len(data['fixtures'])}/7 fixtures verified; artifact: _site/")
    print(f"source commit: {data['build']['commit']}; dirty: {data['build']['dirty']}")
    for record in data["fixtures"]:
        contract = record["contract"]
        print(f"  {record['id']}: {contract['decision']} / {contract['detail_code']} / exit {record['exit_code']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
