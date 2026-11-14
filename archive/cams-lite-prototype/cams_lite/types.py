"""Typed records shared by the audit layer.

The important design choice is that evidence carries its own provenance:
a receipt id, a checksum, a scope, and a non-text marker.  The audit layer
never asks a model whether a claim is true; it checks whether the claim's
declared support can be verified.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


def canonical_json(value: Any) -> str:
    """Stable JSON used for hashes and contract objects."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def content_checksum(content: Any) -> str:
    if isinstance(content, str):
        return sha256_text(content)
    return sha256_text(canonical_json(content))


@dataclass(frozen=True)
class Span:
    """A pointer to a source fragment."""

    span_id: str
    source: str
    text: str
    receipt_id: str | None = None
    non_text: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "span_id": self.span_id,
            "source": self.source,
            "text": self.text,
            "receipt_id": self.receipt_id,
            "non_text": self.non_text,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class Evidence:
    """A tool receipt or other source, with a verifiable checksum."""

    evidence_id: str
    source: str
    content: str
    checksum: str = ""
    valid: bool = True
    scope: str = "in"
    non_text: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def computed_checksum(self) -> str:
        return content_checksum(self.content)

    def checksum_ok(self) -> bool:
        if not self.checksum:
            return False
        return self.checksum == self.computed_checksum()

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "source": self.source,
            "content": self.content,
            "checksum": self.checksum,
            "valid": self.valid,
            "scope": self.scope,
            "non_text": self.non_text,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class Claim:
    """An answer claim and the evidence ids it explicitly relies on."""

    claim_id: str
    text: str
    supports: tuple[str, ...] = ()
    confidence: float = 0.0
    covariance: float = 0.0
    relation: str = "supports"
    scope: str = "in"

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "text": self.text,
            "supports": list(self.supports),
            "confidence": self.confidence,
            "covariance": self.covariance,
            "relation": self.relation,
            "scope": self.scope,
        }


@dataclass
class Verdict:
    """The audit layer's externally consumable result."""

    status: str
    answer: str | None
    reason_code: str
    coverage: float
    covariance: float
    determined: bool
    provenance: dict[str, Any]
    contract: dict[str, Any]
    claims: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "answer": self.answer,
            "reason_code": self.reason_code,
            "coverage": self.coverage,
            "covariance": self.covariance,
            "determined": self.determined,
            "provenance": self.provenance,
            "contract": self.contract,
            "claims": list(self.claims),
        }
