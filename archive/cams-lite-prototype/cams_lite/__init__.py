"""CAMS-Lite: a small, model-agnostic audit layer for agent evidence."""

from .gating import GateConfig, coverage_gate, covariance_marker
from .provenance import ProvenanceTree
from .types import Claim, Evidence, Span, Verdict

__all__ = [
    "Claim",
    "Evidence",
    "GateConfig",
    "ProvenanceTree",
    "Span",
    "Verdict",
    "coverage_gate",
    "covariance_marker",
]
