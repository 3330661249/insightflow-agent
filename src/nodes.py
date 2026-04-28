
from src.config import get_chat_llm
from src.logging_utils import get_logger
from src.prompts import (
    COLLECT_INFO_PROMPT,
    DECIDE_SEARCH_PROMPT,
    GENERATE_REPORT_PROMPT,
)
from src.state import AgentState
from src.tools import search_topic

logger = get_logger(__name__)

_KEYWORD_FALLBACK = ["本周", "最新", "动态", "近期", "新闻"]


def _llm_decide_need_search(topic: str) -> bool:
    llm = get_chat_llm()
    chain = DECIDE_SEARCH_PROMPT | llm
    response = chain.invoke({"topic": topic})
    answer = response.content.strip()

    if "是" in answer and "否" not in answer:
        return True
    if "否" in answer:
        return False

    logger.warning("LLM 决策响应不明确: %r, 使用关键词 fallback", answer)
    return any(kw in topic for kw in _KEYWORD_FALLBACK)


def decide_search(state: AgentState) -> dict:
    topic = state["topic"]

    try:
        need_tool = _llm_decide_need_search(topic)
    except Exception as exc:
        logger.warning("LLM 决策失败: %s, 降级为关键词匹配", exc)
        need_tool = any(kw in topic for kw in _KEYWORD_FALLBACK)

    logger.info("决策结果: topic=%r, need_tool=%s", topic, need_tool)
    return {"need_tool": need_tool}


def collect_info(state: AgentState) -> dict:
    llm = get_chat_llm()
    topic = state["topic"]

    tool_result = search_topic(topic)
    logger.info("搜索完成: topic=%r, 结果长度=%d", topic, len(tool_result))

    chain = COLLECT_INFO_PROMPT | llm
    response = chain.invoke({"topic": topic, "tool_result": tool_result})

    return {"tool_result": tool_result, "summary": response.content.strip()}


def generate_report(state: AgentState) -> dict:
    llm = get_chat_llm()
    topic = state["topic"]
    summary = state["summary"]

    chain = GENERATE_REPORT_PROMPT | llm
    response = chain.invoke({"topic": topic, "summary": summary})

    logger.info("报告生成完成: topic=%r", topic)
    return {"report": response.content.strip()}


def skip_tool(state: AgentState) -> dict:
    topic = state["topic"]
    return {
        "tool_result": "该主题未触发工具调用，直接进入报告生成流程。",
        "summary": f"主题「{topic}」未命中实时信息关键词，当前流程未调用外部工具，后续可直接基于主题生成基础分析报告。",
    }
