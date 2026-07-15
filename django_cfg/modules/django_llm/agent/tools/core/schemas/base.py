"""Common base types for tool results.

Two shapes a tool function can return:

- a tool-specific ``BaseModel`` subclass on success;
- a ``ToolError`` instance on validated failure.

Anything else is a programming error — the ``@llm_tool`` decorator
catches it and reports a generic error to the agent. Tools must NOT
return raw dicts after the plan10 migration.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class ToolError(BaseModel):
    """Validated error reply.

    ``error`` is the short, agent-facing message (kept stable so prompts
    can pattern-match on it). ``detail`` is a longer machine-readable
    body that may help the agent recover (e.g. "field X must be in
    {...}").
    """

    error: str
    detail: str = ""


class ToolErrorException(Exception):
    """Wrapper so ``ToolError`` can be raised in hooks.

    ``_call`` catches this, unwraps the inner ``ToolError``, and
    serialises it for the LLM.
    """

    def __init__(self, tool_error: ToolError) -> None:
        self.tool_error = tool_error
        super().__init__(tool_error.error)


class ToolResult(BaseModel, Generic[T]):
    """Generic envelope for tools that don't have a richer typed shape.

    Most tools will define their own concrete result class for clarity;
    use ``ToolResult[X]`` only when a thin wrapper is genuinely simpler
    than naming a one-off class.
    """

    ok: bool = True
    data: T
    warnings: list[str] = Field(default_factory=list)
