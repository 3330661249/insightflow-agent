from unittest.mock import MagicMock

from src.nodes import collect_info, decide_search, generate_report, skip_tool


def test_skip_tool():
    state = {"topic": "机器学习基础", "need_tool": False, "tool_result": "", "summary": "", "report": ""}
    result = skip_tool(state)
    assert "未触发工具调用" in result["tool_result"]
    assert "机器学习基础" in result["summary"]


def test_decide_search_with_news_keyword():
    state = {"topic": "本周AI新闻", "need_tool": False, "tool_result": "", "summary": "", "report": ""}
    result = decide_search(state)
    assert result["need_tool"] is True


def test_decide_search_with_static_topic():
    state = {"topic": "机器学习基础概念", "need_tool": False, "tool_result": "", "summary": "", "report": ""}
    result = decide_search(state)
    assert result["need_tool"] is False


def test_collect_info_with_mock(monkeypatch):
    mock_response = MagicMock()
    mock_response.content = "这是摘要内容"

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_response

    import src.nodes as nodes_module

    original_prompt = nodes_module.COLLECT_INFO_PROMPT
    monkeypatch.setattr(type(original_prompt), "__or__", lambda self, other: mock_chain)

    monkeypatch.setattr(
        nodes_module, "search_topic", lambda topic: "搜索结果文本"
    )

    state = {"topic": "测试主题", "need_tool": True, "tool_result": "", "summary": "", "report": ""}
    result = collect_info(state)
    assert result["tool_result"] == "搜索结果文本"
    assert result["summary"] == "这是摘要内容"


def test_generate_report_with_mock(monkeypatch):
    mock_response = MagicMock()
    mock_response.content = "# 研究报告\n这是报告内容"

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_response

    import src.nodes as nodes_module

    original_prompt = nodes_module.GENERATE_REPORT_PROMPT
    monkeypatch.setattr(type(original_prompt), "__or__", lambda self, other: mock_chain)

    state = {"topic": "测试", "need_tool": False, "tool_result": "", "summary": "已有摘要", "report": ""}
    result = generate_report(state)
    assert "# 研究报告" in result["report"]
