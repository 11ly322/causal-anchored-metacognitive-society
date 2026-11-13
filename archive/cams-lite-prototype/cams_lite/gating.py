"""Coverage/covariance gate and the stable refusal contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .provenance import ProvenanceTree
from .types import Claim, Verdict

CONTRACT_VERSION = "1.0"
REASON_CODES = {
    "NO_RISK",
    "INSUFFICIENT_EVIDENCE",
    "MEASUREMENT_FAILURE",
    "OUT_OF_SCOPE",
}


@dataclass(frozen=True)
class GateConfig:
    min_coverage: float = 0.80
    tau_cov: float = 0.60
    contract_version: str = CONTRACT_VERSION
    adapter_cost: float = 0.0


def _contract(
    reason_code: str,
    coverage: float,
    provenance: dict[str, Any],
    escalation_path: str,
    adapter_cost: float,
) -> dict[str, Any]:
    if reason_code not in REASON_CODES:
        reason_code = "INSUFFICIENT_EVIDENCE"
    return {
        "contract_version": CONTRACT_VERSION,
        "reason_code": reason_code,
        "evidence_coverage": round(coverage, 6),
        "provenance_summary": provenance.get("root_hash", ""),
        "escalation_path": escalation_path,
        "adapter_cost": round(float(adapter_cost), 6),
    }


def coverage_gate(
    claims: list[Claim],
    tree: ProvenanceTree,
    answer: str | None = None,
    config: GateConfig | None = None,
    *,
    adapter_cost: float | None = None,
    escalation_path: str = "human_review",
) -> Verdict:
    """Return an accept/abstain verdict with a stable external contract.

    ``answer`` is only emitted when every claim is verified and the gate
    accepts.  The refusal object is still structured and usable by an
    external caller, which is the commercial-ROI claim under test.
    """

    cfg = config or GateConfig()
    if adapter_cost is not None:
        cfg = GateConfig(
            min_coverage=cfg.min_coverage,
            tau_cov=cfg.tau_cov,
            contract_version=cfg.contract_version,
            adapter_cost=adapter_cost,
        )

    provenance = tree.to_dict()
    if not claims:
        contract = _contract(
            "INSUFFICIENT_EVIDENCE", 0.0, provenance, escalation_path, cfg.adapter_cost
        )
        return Verdict(
            status="abstain",
            answer=None,
            reason_code=contract["reason_code"],
            coverage=0.0,
            covariance=0.0,
            determined=False,
            provenance=provenance,
            contract=contract,
        )

    checks = [tree.verify_claim(claim) for claim in claims]
    coverage = sum(item["coverage"] for item in checks) / len(checks)
    covariance = max(claim.covariance for claim in claims)
    reasons = [item["reason"] for item in checks if item["reason"] != "OK"]

    if any(reason == "INVALID_EVIDENCE" for reason in reasons):
        reason_code = "MEASUREMENT_FAILURE"
    elif any(reason == "OUT_OF_SCOPE" for reason in reasons):
        reason_code = "OUT_OF_SCOPE"
    elif covariance > cfg.tau_cov:
        reason_code = "INSUFFICIENT_EVIDENCE"
    elif reasons or coverage < cfg.min_coverage:
        reason_code = "INSUFFICIENT_EVIDENCE"
    else:
        reason_code = "NO_RISK"

    accepted = reason_code == "NO_RISK"
    contract = _contract(
        reason_code, coverage, provenance, escalation_path, cfg.adapter_cost
    )
    return Verdict(
        status="accept" if accepted else "abstain",
        answer=answer if accepted else None,
        reason_code=reason_code,
        coverage=coverage,
        covariance=covariance,
        determined=accepted,
        provenance=provenance,
        contract=contract,
        claims=[claim.to_dict() for claim in claims],
    )


def covariance_marker(claim: Claim, tau_cov: float = 0.60) -> dict[str, Any]:
    """Mark high covariance after the fact; this is not a discrete output port."""
    high = claim.covariance > tau_cov
    return {
        "claim_id": claim.claim_id,
        "covariance": claim.covariance,
        "tau_cov": tau_cov,
        "marker": "high_covariance" if high else "calibrated",
        "action": "short_correction" if high else "none",
    }
