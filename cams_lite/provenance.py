"""Checksum and support-graph verification for claims."""

from __future__ import annotations

from typing import Any

from .types import Claim, Evidence, Span, canonical_json, sha256_text


class ProvenanceTree:
    """A small append-only evidence/support graph.

    It intentionally does **not** perform semantic entailment.  It verifies
    the declared support links, checksums, scopes, and non-sequitur markers.
    That limit is part of the contract: a valid hash can still support a
    false conclusion, and the benchmark treats that as a leakage path.
    """

    def __init__(self) -> None:
        self._evidence: dict[str, Evidence] = {}
        self._spans: dict[str, Span] = {}
        self._checks: dict[str, bool] = {}

    def add_evidence(self, evidence: Evidence) -> Span:
        ok = evidence.valid and evidence.checksum_ok()
        self._checks[evidence.evidence_id] = ok
        self._evidence[evidence.evidence_id] = evidence
        span = Span(
            span_id=f"span:{evidence.evidence_id}",
            source=evidence.source,
            text=evidence.content,
            receipt_id=evidence.evidence_id,
            non_text=evidence.non_text,
            metadata={"checksum": evidence.checksum, "scope": evidence.scope},
        )
        self._spans[span.span_id] = span
        return span

    def add_many(self, evidence: list[Evidence]) -> list[Span]:
        return [self.add_evidence(item) for item in evidence]

    def has_evidence(self, evidence_id: str) -> bool:
        return evidence_id in self._evidence

    def evidence_ids(self) -> list[str]:
        return list(self._evidence)

    def root_hash(self) -> str:
        payload = [self._evidence[key].to_dict() for key in sorted(self._evidence)]
        return sha256_text(canonical_json(payload))

    def verify_claim(self, claim: Claim) -> dict[str, Any]:
        if not claim.supports:
            return self._result(False, 0.0, "NO_SUPPORT", [], False)

        if claim.relation != "supports":
            return self._result(False, 0.0, "NON_SEQUITUR", [], False)

        valid = 0
        span_ids: list[str] = []
        non_text = False
        reasons: list[str] = []

        for evidence_id in claim.supports:
            evidence = self._evidence.get(evidence_id)
            if evidence is None:
                reasons.append("MISSING_SUPPORT")
                continue
            if not self._checks.get(evidence_id, False):
                reasons.append("INVALID_EVIDENCE")
                continue
            if evidence.scope not in ("in", "any") and claim.scope != evidence.scope:
                reasons.append("OUT_OF_SCOPE")
                continue
            valid += 1
            non_text = non_text or evidence.non_text
            span_ids.append(f"span:{evidence_id}")

        coverage = valid / len(claim.supports)
        if reasons:
            reason = reasons[0]
        elif coverage < 1.0:
            reason = "EVIDENCE_INSUFFICIENT"
        else:
            reason = "OK"
        return self._result(
            verified=coverage == 1.0,
            coverage=coverage,
            reason=reason,
            span_ids=span_ids,
            non_text=non_text,
        )

    def verify_claims(self, claims: list[Claim]) -> list[dict[str, Any]]:
        return [self.verify_claim(claim) for claim in claims]

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_hash": self.root_hash(),
            "evidence": [
                self._evidence[key].to_dict() for key in sorted(self._evidence)
            ],
            "spans": [self._spans[key].to_dict() for key in sorted(self._spans)],
        }

    @staticmethod
    def _result(
        verified: bool,
        coverage: float,
        reason: str,
        span_ids: list[str],
        non_text: bool,
    ) -> dict[str, Any]:
        return {
            "verified": verified,
            "coverage": coverage,
            "reason": reason,
            "span_ids": span_ids,
            "non_text": non_text,
        }
