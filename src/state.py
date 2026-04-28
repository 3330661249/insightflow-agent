from typing import TypedDict


class AgentState(TypedDict):
    topic: str
    tool_result: str
    summary: str
    report: str
    need_tool: bool
    decision_reason: str
    errors: list[str]
