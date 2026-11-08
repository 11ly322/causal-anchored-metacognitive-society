"""Minimal parser for OpenAI-style tool-call logs (no network calls)."""

from __future__ import annotations

import json
from typing import Any

from ..types import Evidence, content_checksum


def _as_content(arguments: Any) -> str:
    if isinstance(arguments, str):
        try:
            parsed = json.loads(arguments)
        except json.JSONDecodeError:
            return arguments
        return json.dumps(parsed, ensure_ascii=False, sort_keys=True)
    return json.dumps(arguments, ensure_ascii=False, sort_keys=True)


def parse_openai_tool_calls(payload: Any) -> list[Evidence]:
    """Parse a dict with ``tool_calls`` or a bare list of calls.

    Unknown/error calls become invalid Evidence rather than being dropped;
    dropping them would hide measurement failure from the audit layer.
    """

    if isinstance(payload, dict):
        calls = payload.get("tool_calls", [])
    elif isinstance(payload, list):
        calls = payload
    else:
        raise TypeError("payload must be a dict or a list")

    evidence: list[Evidence] = []
    for index, call in enumerate(calls):
        if not isinstance(call, dict):
            evidence.append(
                Evidence(
                    evidence_id=f"call:{index}",
                    source="unknown",
                    content=str(call),
                    valid=False,
                    metadata={"error": "UNSUPPORTED_LOG_FORMAT"},
                )
            )
            continue
        call_id = str(call.get("id") or f"call:{index}")
        function = call.get("function") or {}
        name = str(function.get("name") or call.get("name") or "unknown")
        content = _as_content(function.get("arguments", call.get("arguments", "")))
        status = str(call.get("status") or "ok").lower()
        valid = status not in {"error", "failed", "invalid"}
        evidence.append(
            Evidence(
                evidence_id=call_id,
                source=name,
                content=content,
                checksum=content_checksum(content),
                valid=valid,
                non_text=name in {"browser", "sensor", "file", "shell"},
                metadata={"status": status, "format": "openai"},
            )
        )
    return evidence
