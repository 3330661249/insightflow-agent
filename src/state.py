from typing import Literal, TypedDict


class Source(TypedDict):
    id: str
    title: str
    url: str
    content: str
    published_at: str


class SearchResult(TypedDict):
    status: Literal["ok", "empty", "unavailable", "error"]
    sources: list[Source]
    error_code: str


class AgentState(TypedDict):
    topic: str
    tool_result: str
    summary: str
    report: str
    need_tool: bool
    decision_reason: str
    errors: list[str]
    sources: list[Source]
    search_status: str
    status: str
