import json

import pytest

from cams_lite.adapters import parse_anthropic_tool_uses, parse_openai_tool_calls
from cams_lite.types import content_checksum


def test_openai_dict_parsing_and_checksum():
    payload = {
        "tool_calls": [
            {
                "id": "call_1",
                "function": {"name": "sensor", "arguments": json.dumps({"value": 42})},
            }
        ]
    }
    evidence = parse_openai_tool_calls(payload)
    assert len(evidence) == 1
    assert evidence[0].valid is True
    assert evidence[0].checksum == content_checksum('{"value": 42}')


def test_openai_error_and_bad_shape():
    payload = [
        {"id": "call_1", "function": {"name": "sensor"}, "status": "error"},
        "not-a-dict",
    ]
    evidence = parse_openai_tool_calls(payload)
    assert evidence[0].valid is False
    assert evidence[1].valid is False


def test_openai_bare_list_and_string_arguments():
    evidence = parse_openai_tool_calls(
        [{"id": "c", "function": {"name": "shell", "arguments": "echo hi"}}]
    )
    assert evidence[0].source == "shell"
    assert evidence[0].non_text is True


def test_anthropic_parsing_skips_non_tool_blocks():
    payload = {
        "content": [
            {"type": "text", "text": "I will check."},
            {"type": "tool_use", "id": "tool_1", "name": "browser", "input": {"url": "x"}},
        ]
    }
    evidence = parse_anthropic_tool_uses(payload)
    assert len(evidence) == 1
    assert evidence[0].evidence_id == "tool_1"
    assert evidence[0].checksum == content_checksum('{"url": "x"}')


def test_anthropic_error_marker():
    payload = {"content": [{"type": "tool_use", "id": "t", "name": "db", "input": {}, "is_error": True}]}
    assert parse_anthropic_tool_uses(payload)[0].valid is False


def test_adapters_reject_non_collection():
    with pytest.raises(TypeError):
        parse_openai_tool_calls("nope")
    with pytest.raises(TypeError):
        parse_anthropic_tool_uses(42)
