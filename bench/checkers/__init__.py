"""Seven executable checkers for AgentAudit-Bench v0."""

from .bad_reasoning import check as bad_reasoning
from .minority_evidence import check as minority_evidence
from .ood import check as ood
from .overconservative import check as overconservative
from .precision_bias import check as precision_bias
from .quality_gaming import check as quality_gaming
from .sensor_lie import check as sensor_lie

CHECKS = {
    "sensor_lie": sensor_lie,
    "bad_reasoning": bad_reasoning,
    "minority_evidence": minority_evidence,
    "precision_bias": precision_bias,
    "ood": ood,
    "overconservative": overconservative,
    "quality_gaming": quality_gaming,
}

__all__ = ["CHECKS"]
