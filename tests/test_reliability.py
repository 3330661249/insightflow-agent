from types import SimpleNamespace

import pytest
import requests

from src import nodes, tools
from src.graph import build_graph


def initial(topic="本周 AI 新闻"):
    return {
        "topic": topic, "need_tool": False, "tool_result": "", "summary": "",
        "report": "", "decision_reason": "", "errors": [],
    }


def response_payload():
    return {"data": {"webPages": {"value": [{
        "name": "Synthetic release", "summary": "Synthetic product added export.",
        "url": "https://example.com/release", "datePublished": "2026-09-18",
    }]}}}


def fake_model(monkeypatch, answers):
    from langchain_core.runnables import RunnableLambda

    iterator = iter(answers)

    def respond(prompt):
        answer = next(iterator)
        if isinstance(answer, Exception):
            raise answer
        return SimpleNamespace(content=answer)

    monkeypatch.setattr(nodes, "get_chat_llm", lambda: RunnableLambda(respond))


def successful_search(monkeypatch):
    monkeypatch.setattr(tools.requests, "post", lambda *a, **k: SimpleNamespace(
        raise_for_status=lambda: None, json=response_payload,
    ))


def test_graph_without_any_keys_completes_unavailable(monkeypatch):
    for name in ["ZHIPU_API_KEY", "ZHIPU_BASE_URL", "BOCHA_API_KEY"]:
        monkeypatch.delenv(name, raising=False)
    result = build_graph().invoke(initial())
    assert result["status"] == "unavailable"
    assert result["sources"] == []
    assert "未获得可用外部证据" in result["report"]


def test_search_key_is_independent_of_model_configuration(monkeypatch):
    monkeypatch.delenv("ZHIPU_API_KEY")
    monkeypatch.delenv("ZHIPU_BASE_URL")
    successful_search(monkeypatch)
    result = tools.search_topic("本周 AI 新闻")
    assert result["status"] == "ok"
    assert result["sources"][0]["title"] == "Synthetic release"


def test_missing_search_key_returns_unavailable(monkeypatch):
    monkeypatch.delenv("BOCHA_API_KEY")
    result = tools.search_topic("topic")
    assert result["status"] == "unavailable"
    assert result["error_code"] == "SEARCH_NOT_CONFIGURED"


@pytest.mark.parametrize("payload", [None, {"data": None}, {"data": {"webPages": {"value": [None]}}}])
def test_malformed_search_is_an_error_instead_of_crashing(payload):
    result = tools._parse_search_response(payload, "topic")
    assert result["status"] == "error"
    assert result["sources"] == []


@pytest.mark.parametrize("failure,code", [
    (requests.Timeout("sentinel-private-value"), "SEARCH_TIMEOUT"),
    (requests.HTTPError("sentinel-private-value"), "SEARCH_REQUEST_FAILED"),
])
def test_search_errors_are_safe_and_not_evidence(monkeypatch, caplog, failure, code):
    def fail(*args, **kwargs):
        raise failure
    monkeypatch.setattr(tools.requests, "post", fail)
    fake_model(monkeypatch, ["是"])
    result = build_graph().invoke(initial())
    assert result["status"] == "unavailable"
    assert code in result["errors"]
    assert "sentinel-private-value" not in repr(result) + caplog.text
    assert result["sources"] == []


def test_empty_search_does_not_generate_research_claims(monkeypatch):
    monkeypatch.setattr(tools.requests, "post", lambda *a, **k: SimpleNamespace(
        raise_for_status=lambda: None, json=lambda: {"data": {"webPages": {"value": []}}},
    ))
    fake_model(monkeypatch, ["是"])
    result = build_graph().invoke(initial())
    assert result["status"] == "unavailable"
    assert "未获得可用外部证据" in result["report"]


def test_sources_survive_into_exported_report(monkeypatch, tmp_path):
    from src.utils import save_report

    successful_search(monkeypatch)
    fake_model(monkeypatch, ["是", "Added export. [S1]", "# Report\nAdded export. [S1]"])
    result = build_graph().invoke(initial())
    assert result["status"] == "ok"
    assert result["sources"][0]["id"] == "S1"
    assert result["sources"][0]["published_at"] == "2026-09-18"
    assert "[S1]" in result["report"]
    assert "https://example.com/release" in result["report"]
    assert "未逐句核验" in result["report"]
    monkeypatch.setattr("src.utils.REPORTS_DIR", tmp_path)
    path = save_report(result["topic"], result["report"])
    assert "https://example.com/release" in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("report", ["# Report\nUnsupported assertion.", "# Report\nAssertion. [S99]"])
def test_missing_or_unknown_citations_degrade_report(monkeypatch, report):
    successful_search(monkeypatch)
    fake_model(monkeypatch, ["是", "Added export. [S1]", report])
    result = build_graph().invoke(initial())
    assert result["status"] == "degraded"
    assert "CITATION_CHECK_FAILED" in result["errors"]
    assert "引用检查未通过" in result["report"]


@pytest.mark.parametrize("report", [
    "结论 [S1](https://fabricated.example/not-the-source)",
    "结论 [S1][fake]\n\n[fake]: https://fabricated.example/not-the-source",
    "结论 [S1]\n\n[S1]: https://fabricated.example/not-the-source",
    "[结论包含编号 [S1]](https://fabricated.example/not-the-source)",
])
def test_model_citation_links_cannot_override_source_registry(monkeypatch, report):
    successful_search(monkeypatch)
    fake_model(monkeypatch, ["是", "Added export. [S1]", report])
    result = build_graph().invoke(initial())
    assert result["status"] == "degraded"
    assert "CITATION_CHECK_FAILED" in result["errors"]
    assert "fabricated.example" not in result["report"]
    assert "https://example.com/release" in result["report"]


def test_adjacent_bare_citation_ids_remain_valid(monkeypatch):
    successful_search(monkeypatch)
    fake_model(monkeypatch, ["是", "Added export. [S1]", "Two observations. [S1] [S1]"])
    assert build_graph().invoke(initial())["status"] == "ok"


def test_summary_failure_preserves_sources_without_leaking_exception(monkeypatch, caplog):
    successful_search(monkeypatch)
    fake_model(monkeypatch, ["是", RuntimeError("sentinel-private-value")])
    result = build_graph().invoke(initial())
    assert result["status"] == "degraded"
    assert "Synthetic product added export" in result["report"]
    assert "https://example.com/release" in result["report"]
    assert "sentinel-private-value" not in repr(result) + caplog.text


def test_report_failure_is_safe_and_keeps_sources(monkeypatch, caplog):
    successful_search(monkeypatch)
    fake_model(monkeypatch, ["是", "Added export. [S1]", RuntimeError("sentinel-private-value")])
    result = build_graph().invoke(initial())
    assert result["status"] == "degraded"
    assert "REPORT_UNAVAILABLE" in result["errors"]
    assert "https://example.com/release" in result["report"]
    assert "sentinel-private-value" not in repr(result) + caplog.text


def test_static_analysis_is_labeled_unverified(monkeypatch):
    fake_model(monkeypatch, ["否", "# Model analysis\nA concept explanation."])
    result = build_graph().invoke(initial("机器学习基础概念"))
    assert result["status"] == "unverified"
    assert result["sources"] == []
    assert "未检索外部来源" in result["report"]
