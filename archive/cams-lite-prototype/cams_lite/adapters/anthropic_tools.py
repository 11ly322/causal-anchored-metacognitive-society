"""Minimal parser for Anthropic-style tool_use logs (no network calls)."""

from __future__ import annotations

import json
from typing import Any

from ..types import Evidence, content_checksum


def _as_content(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def parse_anthropic_tool_uses(payload: Any) -> list[Evidence]:
    if isinstance(payload, dict):
        blocks = payload.get("content", [])
    elif isinstance(payload, list):
        blocks = payload
    else:
        raise TypeError("payload must be a dict or a list")

    evidence: list[Evidence] = []
    for index, block in enumerate(blocks):
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            continue
        tool_id = str(block.get("id") or f"tool:{index}")
        name = str(block.get("name") or "unknown")
        content = _as_content(block.get("input", {}))
        valid = not bool(block.get("is_error", False))
        evidence.append(
            Evidence(
                evidence_id=tool_id,
                source=name,
                content=content,
                checksum=content_checksum(content),
                valid=valid,
                non_text=name in {"browser", "sensor", "file", "shell"},
                metadata={"format": "anthropic", "error": bool(block.get("is_error", False))},
            )
        )
    return evidence
