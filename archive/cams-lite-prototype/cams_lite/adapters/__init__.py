"""Adapters that turn vendor tool-call logs into Evidence records."""

from .anthropic_tools import parse_anthropic_tool_uses
from .openai_tools import parse_openai_tool_calls

__all__ = ["parse_anthropic_tool_uses", "parse_openai_tool_calls"]
