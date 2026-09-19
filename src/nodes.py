import re

from src.config import get_chat_llm
from src.logging_utils import get_logger
from src.prompts import COLLECT_INFO_PROMPT, DECIDE_SEARCH_PROMPT, GENERATE_REPORT_PROMPT
from src.state import AgentState, Source
from src.tools import search_topic
from src.utils import validate_topic

logger = get_logger(__name__)
_KEYWORD_FALLBACK = ["本周", "最新", "动态", "近期", "新闻", "今年", "今天", "当前", "目前", "价格"]


def _content(response) -> str:
    content = response.content
    if not isinstance(content, str) or not content.strip():
        raise ValueError("EMPTY_MODEL_RESPONSE")
    return content.strip()


def _llm_decide_need_search(topic: str) -> bool:
    answer = _content((DECIDE_SEARCH_PROMPT | get_chat_llm()).invoke({"topic": topic}))
    if answer not in {"是", "否"}:
        raise ValueError("INVALID_DECISION")
    return answer == "是"


def decide_search(state: AgentState) -> dict:
    topic = validate_topic(state["topic"])
    errors = list(state.get("errors", []))
    try:
        need_tool = _llm_decide_need_search(topic)
        reason = "LLM 判断需要外部搜索。" if need_tool else "LLM 判断可先进行概念分析。"
    except Exception:
        logger.warning("决策不可用，使用关键词规则: code=DECISION_UNAVAILABLE")
        need_tool = any(keyword in topic for keyword in _KEYWORD_FALLBACK)
        reason = "模型决策不可用，已使用关键词规则；该规则不能覆盖所有时效性问题。"
        errors.append("DECISION_UNAVAILABLE")
    return {"topic": topic, "need_tool": need_tool, "decision_reason": reason, "errors": errors}


def _source_text(sources: list[Source]) -> str:
    return "\n\n".join(f"[{source['id']}] {source['title']}\n{source['content']}" for source in sources)


def collect_info(state: AgentState) -> dict:
    errors = list(state.get("errors", []))
    try:
        result = search_topic(state["topic"])
    except Exception:
        logger.warning("搜索不可用: code=SEARCH_UNAVAILABLE")
        result = {"status": "error", "sources": [], "error_code": "SEARCH_UNAVAILABLE"}
    sources = result["sources"]
    update = {
        "sources": sources, "search_status": result["status"],
        "tool_result": _source_text(sources), "summary": "", "errors": errors,
    }
    if result["status"] != "ok":
        errors.append(result["error_code"])
        return {**update, "status": "unavailable"}
    try:
        summary = _content((COLLECT_INFO_PROMPT | get_chat_llm()).invoke({
            "topic": state["topic"], "tool_result": update["tool_result"],
        }))
        return {**update, "summary": summary, "status": "ok"}
    except Exception:
        logger.warning("摘要生成不可用: code=SUMMARY_UNAVAILABLE")
        errors.append("SUMMARY_UNAVAILABLE")
        return {**update, "summary": update["tool_result"], "status": "degraded"}


def _append_sources(report: str, sources: list[Source]) -> str:
    if not sources:
        return report
    lines = ["", "## 检索来源", "", "以下为检索返回的来源；编号匹配不代表已验证每条结论的语义支持。"]
    for source in sources:
        date = source["published_at"] or "未提供"
        lines.append(f"- [{source['id']}] {source['title']} — {source['url']}（发布时间：{date}）")
    return report + "\n" + "\n".join(lines)


def _evidence_fallback(state: AgentState, note: str) -> str:
    return _append_sources(
        f"# {state['topic']}\n\n> {note}\n\n## 原始检索摘要\n\n"
        f"{_source_text(state.get('sources', [])) or '未获得可用外部证据。'}\n\n"
        "## 后续建议\n请补充可靠来源或检查服务配置后重试；当前结果不构成已核验的研究结论。",
        state.get("sources", []),
    )


def generate_report(state: AgentState) -> dict:
    sources = state.get("sources", [])
    errors = list(state.get("errors", []))
    if state["need_tool"] and state.get("search_status") != "ok":
        return {"status": "unavailable", "report": _evidence_fallback(state, "外部证据不可用；未生成研究结论。")}
    if "SUMMARY_UNAVAILABLE" in errors:
        return {"status": "degraded", "report": _evidence_fallback(state, "摘要整理失败；以下保留原始检索摘要。")}
    try:
        report = _content((GENERATE_REPORT_PROMPT | get_chat_llm()).invoke({
            "topic": state["topic"], "summary": state["summary"], "sources": _source_text(sources),
        }))
    except Exception:
        logger.warning("报告生成不可用: code=REPORT_UNAVAILABLE")
        errors.append("REPORT_UNAVAILABLE")
        return {
            "status": "degraded" if sources else "unavailable", "errors": errors,
            "report": _evidence_fallback(state, "报告生成失败；已保留可用检索证据。"),
        }
    if not sources:
        return {"status": "unverified", "report": "> 未检索外部来源；以下是未经外部证据核验的模型分析。\n\n" + report}

    # The model may emit bare IDs only; links are rendered from the source registry.
    # Reject inline links, reference links and reference definitions, which can
    # otherwise bind a valid ID to an unrelated model-invented URL.
    has_link = re.search(r"\]\s*\(|<a\b", report, re.IGNORECASE)
    has_link_definition = re.search(r"(?m)^\s*\[[^\]\n]+\]:", report)
    if has_link or has_link_definition:
        errors.append("CITATION_CHECK_FAILED")
        return {
            "status": "degraded", "errors": errors,
            "report": _evidence_fallback(state, "引用检查未通过：生成正文包含链接定义；已舍弃生成正文，仅保留检索资料。"),
        }
    cited = set(re.findall(r"\[(S\d+)\]", report))
    known = {source["id"] for source in sources}
    if not cited or not cited <= known:
        status = "degraded"
        errors.append("CITATION_CHECK_FAILED")
        notice = "引用检查未通过：正文缺少引用或存在未知编号；以下内容需人工核验。"
    else:
        status = "degraded" if errors else "ok"
        notice = "引用编号已匹配检索来源；未逐句核验结论与来源的语义支持，也未验证时效性。"
    return {"status": status, "errors": errors, "report": _append_sources(f"> {notice}\n\n{report}", sources)}


def skip_tool(state: AgentState) -> dict:
    return {
        "sources": [], "search_status": "not_requested", "status": "unverified",
        "tool_result": "该主题未触发工具调用。",
        "summary": f"主题：{state['topic']}。未检索外部证据，仅可进行概念分析。",
        "decision_reason": state.get("decision_reason", "当前路径未调用外部工具。"),
    }
