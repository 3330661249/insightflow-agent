
from src.config import get_chat_llm
from src.logging_utils import get_logger
from src.prompts import (
    COLLECT_INFO_PROMPT,
    DECIDE_SEARCH_PROMPT,
    GENERATE_REPORT_PROMPT,
)
from src.state import AgentState
from src.tools import search_topic
from src.utils import validate_topic

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
    topic = validate_topic(state["topic"])

    try:
        need_tool = _llm_decide_need_search(topic)
        decision_reason = "LLM 决策完成。"
    except Exception as exc:
        logger.warning("LLM 决策失败: %s, 降级为关键词匹配", exc)
        need_tool = any(kw in topic for kw in _KEYWORD_FALLBACK)
        decision_reason = f"LLM 决策失败，已降级为关键词匹配：{exc}"

    logger.info("决策结果: topic=%r, need_tool=%s", topic, need_tool)
    return {"topic": topic, "need_tool": need_tool, "decision_reason": decision_reason}


def collect_info(state: AgentState) -> dict:
    llm = get_chat_llm()
    topic = state["topic"]

    tool_result = search_topic(topic)
    logger.info("搜索完成: topic=%r, 结果长度=%d", topic, len(tool_result))

    try:
        chain = COLLECT_INFO_PROMPT | llm
        response = chain.invoke({"topic": topic, "tool_result": tool_result})
        summary = response.content.strip()
        return {"tool_result": tool_result, "summary": summary}
    except Exception as exc:
        logger.error("摘要生成失败: topic=%r, error=%s", topic, exc)
        errors = list(state.get("errors", [])) + [f"摘要生成失败：{exc}"]
        return {
            "tool_result": tool_result,
            "summary": f"工具已返回关于「{topic}」的原始结果，但摘要整理失败，可直接参考原始工具输出。",
            "errors": errors,
        }


def generate_report(state: AgentState) -> dict:
    llm = get_chat_llm()
    topic = state["topic"]
    summary = state["summary"]

    try:
        chain = GENERATE_REPORT_PROMPT | llm
        response = chain.invoke({"topic": topic, "summary": summary})
        report = response.content.strip()
    except Exception as exc:
        logger.error("报告生成失败: topic=%r, error=%s", topic, exc)
        errors = list(state.get("errors", [])) + [f"报告生成失败：{exc}"]
        report = (
            f"# 研究主题\n{topic}\n\n"
            f"## 信息摘要\n{summary or '暂无可用摘要'}\n\n"
            "## 初步结论\n当前流程在报告生成阶段失败，已保留已有摘要供后续继续整理。\n\n"
            "## 后续建议\n请检查模型配置、网络状态或稍后重试。"
        )
        return {"report": report, "errors": errors}

    logger.info("报告生成完成: topic=%r", topic)
    return {"report": report}


def skip_tool(state: AgentState) -> dict:
    topic = state["topic"]
    return {
        "tool_result": "该主题未触发工具调用，直接进入报告生成流程。",
        "summary": f"主题「{topic}」未命中实时信息关键词，当前流程未调用外部工具，后续可直接基于主题生成基础分析报告。",
        "decision_reason": state.get("decision_reason", "该主题无需调用外部工具。"),
    }
