"""Shared checker result type."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckResult:
    passed: bool
    correct: bool
    hallucination: bool
    determined: bool
    unnecessary_abstention: bool
    reason: str

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "correct": self.correct,
            "hallucination": self.hallucination,
            "determined": self.determined,
            "unnecessary_abstention": self.unnecessary_abstention,
            "reason": self.reason,
        }
