#!/usr/bin/env python3
"""Run AgentAudit-Bench v0 baselines offline.

Methods:
- no-audit: trust every proposed answer;
- logprob-gate: abstain below a confidence threshold calibrated on dev;
- cams-lite: provenance/coverage/covariance gate.

No network and no model call.  The benchmark is synthetic; its numbers are
`[实测-合成]` and cannot be used as the preregistered H1 result.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bench.checkers import CHECKS  # noqa: E402
from bench.score import compute_metrics, h1_like_signal  # noqa: E402
from cams_lite import Claim, Evidence, ProvenanceTree, coverage_gate  # noqa: E402

TASKS = ROOT / "bench" / "tasks"


def load_tasks(split: str = "test") -> list[dict[str, Any]]:
    tasks = []
    for path in sorted(TASKS.glob("T*.json")):
        task = json.loads(path.read_text(encoding="utf-8"))
        if split == "all" or task["split"] == split:
            tasks.append(task)
    return tasks


def build_tree(task: dict[str, Any]) -> ProvenanceTree:
    tree = ProvenanceTree()
    for receipt in task["tool_receipts"]:
        tree.add_evidence(
            Evidence(
                evidence_id=receipt["id"],
                source=receipt["tool"],
                content=receipt["payload"],
                checksum=receipt["checksum"],
                valid=bool(receipt["valid"]),
                scope=receipt["scope"],
                non_text=bool(receipt["non_text"]),
            )
        )
    return tree


def build_claims(task: dict[str, Any]) -> list[Claim]:
    claims = []
    for raw in task["candidate"]["claims"]:
        claims.append(
            Claim(
                claim_id=raw["id"],
                text=raw["text"],
                supports=tuple(raw["supports"]),
                confidence=float(raw.get("confidence", 0.0)),
                covariance=float(raw.get("covariance", 0.1)),
                relation=raw.get("relation", "supports"),
                scope=raw.get("scope", "in"),
            )
        )
    return claims


def no_audit(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "determined": True,
        "answer": task["candidate"]["answer"],
        "coverage": 1.0,
        "reason_code": "NO_RISK",
        "confidence": float(task["candidate"]["confidence"]),
    }


def logprob_gate(task: dict[str, Any], threshold: float) -> dict[str, Any]:
    confidence = float(task["candidate"]["confidence"])
    determined = confidence >= threshold
    return {
        "determined": determined,
        "answer": task["candidate"]["answer"] if determined else None,
        "coverage": 1.0 if determined else 0.0,
        "reason_code": "NO_RISK" if determined else "INSUFFICIENT_EVIDENCE",
        "confidence": confidence,
    }


def cams_lite(task: dict[str, Any]) -> dict[str, Any]:
    verdict = coverage_gate(
        build_claims(task),
        build_tree(task),
        answer=task["candidate"]["answer"],
        escalation_path="human_review",
    )
    return {
        "determined": verdict.determined,
        "answer": verdict.answer,
        "coverage": verdict.coverage,
        "reason_code": verdict.reason_code,
        "confidence": float(task["candidate"]["confidence"]),
        "contract": verdict.contract,
    }


def evaluate(task: dict[str, Any], verdict: dict[str, Any], method: str) -> dict[str, Any]:
    check = CHECKS[task["checker"]](task, verdict)
    return {
        "task_id": task["id"],
        "category": task["category"],
        "split": task["split"],
        "method": method,
        "expected": task["ground_truth"]["expected"],
        "determined": verdict["determined"],
        "answer": verdict["answer"],
        "coverage": verdict["coverage"],
        "reason_code": verdict["reason_code"],
        "confidence": verdict["confidence"],
        **check.to_dict(),
    }


def calibrate_logprob(dev_tasks: list[dict[str, Any]], target_coverage: float = 0.80) -> float:
    confidences = sorted({float(task["candidate"]["confidence"]) for task in dev_tasks})
    if not confidences:
        return 0.75
    best = confidences[0]
    best_gap = 2.0
    for threshold in confidences:
        coverage = sum(
            1 for task in dev_tasks if float(task["candidate"]["confidence"]) >= threshold
        ) / len(dev_tasks)
        gap = abs(coverage - target_coverage)
        if gap < best_gap:
            best, best_gap = threshold, gap
    return best


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="test", choices=["dev", "test", "all"])
    parser.add_argument("--subset", type=int, default=0)
    parser.add_argument("--out", default=str(ROOT / "bench" / "results" / "benchmark.json"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    dev_tasks = load_tasks("dev")
    threshold = calibrate_logprob(dev_tasks, 0.80)
    tasks = load_tasks(args.split)
    if args.subset:
        tasks = tasks[: args.subset]
    if not tasks:
        raise SystemExit("no tasks selected")

    methods = {
        "no_audit": lambda task: no_audit(task),
        "logprob_gate": lambda task: logprob_gate(task, threshold),
        "cams_lite": cams_lite,
    }
    all_records: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}
    for name, fn in methods.items():
        records = [evaluate(task, fn(task), name) for task in tasks]
        all_records.extend(records)
        summary[name] = compute_metrics(records)

    payload = {
        "mode": "synthetic-bench",
        "evidence": "[实测-合成]",
        "note": "Synthetic tasks; not the preregistered live H1 result.",
        "split": args.split,
        "n": len(tasks),
        "logprob_threshold": threshold,
        "methods": summary,
        "descriptive_only": {
            **h1_like_signal(summary["logprob_gate"], summary["cams_lite"]),
            "coverage_matched": False,
            "note": "Synthetic bench; not the preregistered H1.",
        },
        "records": all_records,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"split={args.split} n={len(tasks)} logprob_threshold={threshold}")
        print(f"{'method':14} {'coverage':>9} {'accuracy':>9} {'halluc':>8} {'unnecessary':>12}")
        for name, metrics in summary.items():
            print(
                f"{name:14} {metrics['coverage']:9.3f} {metrics['accuracy']:9.3f} "
                f"{metrics['hallucination_rate']:8.3f} {metrics['unnecessary_abstention_rate']:12.3f}"
            )
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
