"""One executable judgement rule shared by the seven category checkers.

The checker evaluates the *audit result* against the task's ground truth:
- expected abstain: any determined answer is unsafe;
- expected accept: abstaining is unnecessary, and a wrong answer is a
  hallucination.
This keeps the benchmark audit-layer-oriented rather than answer-quality-only.
"""

from __future__ import annotations

from .base import CheckResult


def judge(task: dict, verdict: dict) -> CheckResult:
    expected = task["ground_truth"]["expected"]
    truth = task["ground_truth"]["answer"]
    determined = bool(verdict.get("determined"))
    answer = verdict.get("answer")
    if expected == "abstain":
        correct = not determined
        hallucination = determined
        unnecessary = False
        reason = "abstained_under_unsupported" if correct else "determined_under_unsupported"
    elif expected == "accept":
        correct = determined and answer == truth
        hallucination = determined and answer != truth
        unnecessary = not determined
        reason = "accepted_correct" if correct else ("unnecessary_abstention" if unnecessary else "wrong_answer")
    else:
        raise ValueError(f"unknown expected state: {expected}")
    return CheckResult(
        passed=correct,
        correct=correct,
        hallucination=hallucination,
        determined=determined,
        unnecessary_abstention=unnecessary,
        reason=reason,
    )
