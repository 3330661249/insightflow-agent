import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from src.state import AgentState
from src.prompts import COLLECT_INFO_PROMPT, GENERATE_REPORT_PROMPT
from src.tools import search_topic

load_dotenv()

def get_llm():
    api_key = os.getenv("ZHIPU_API_KEY")
    base_url = os.getenv("ZHIPU_BASE_URL")
    model_name = os.getenv("ZHIPU_CHAT_MODEL", "glm-4-flash")

    if not api_key:
        raise ValueError("未检测到 ZHIPU_API_KEY，请检查 .env 文件配置。")

    if not base_url:
        raise ValueError("未检测到 ZHIPU_BASE_URL，请检查 .env 文件配置。")

    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0.3
    )

def collect_info(state: AgentState) -> AgentState:
    llm = get_llm()
    topic = state["topic"]

    tool_result = search_topic(topic)
    state["tool_result"] = tool_result

    prompt = COLLECT_INFO_PROMPT.format(
        topic=topic,
        tool_result=tool_result
    )
    response = llm.invoke(prompt)

    state["summary"] = response.content.strip()
    return state

def generate_report(state: AgentState) -> AgentState:
    llm = get_llm()
    topic = state["topic"]
    summary = state["summary"]

    prompt = GENERATE_REPORT_PROMPT.format(topic=topic, summary=summary)
    response = llm.invoke(prompt)

    state["report"] = response.content.strip()
    return state

def decide_search(state: AgentState) -> AgentState:
    topic = state["topic"]

    keywords = ["本周", "最新", "动态", "近期", "新闻"]
    need_tool = any(keyword in topic for keyword in keywords)

    state["need_tool"] = need_tool
    return state

def skip_tool(state: AgentState) -> AgentState:
    topic = state["topic"]

    state["tool_result"] = "该主题未触发工具调用，直接进入报告生成流程。"
    state["summary"] = f"主题「{topic}」未命中实时信息关键词，当前流程未调用外部工具，后续可直接基于主题生成基础分析报告。"
    return state