from src.tools import _parse_search_response


def test_parse_search_response_with_results():
    data = {
        "data": {
            "webPages": {
                "value": [
                    {
                        "title": "LangGraph 入门",
                        "snippet": "LangGraph 是一个框架",
                        "summary": "LangGraph 是用于构建 Agent 的框架",
                        "url": "https://example.com/1",
                    },
                    {
                        "title": "LangGraph 进阶",
                        "snippet": "进阶用法介绍",
                        "url": "https://example.com/2",
                    },
                ]
            }
        }
    }
    result = _parse_search_response(data, "LangGraph")
    assert result["status"] == "ok"
    assert result["sources"][0]["title"] == "LangGraph 入门"
    assert result["sources"][0]["content"] == "LangGraph 是用于构建 Agent 的框架"
    assert result["sources"][0]["url"] == "https://example.com/1"
    assert result["sources"][1]["content"] == "进阶用法介绍"


def test_parse_search_response_empty():
    data = {"data": {"webPages": {"value": []}}}
    result = _parse_search_response(data, "测试主题")
    assert result["status"] == "empty"
    assert result["sources"] == []


def test_parse_search_response_no_data():
    result = _parse_search_response({}, "测试")
    assert result["status"] == "error"
    assert result["error_code"] == "SEARCH_INVALID_RESPONSE"


def test_parse_search_response_missing_fields():
    data = {
        "data": {
            "webPages": {
                "value": [{"title": "测试"}]
            }
        }
    }
    result = _parse_search_response(data, "测试")
    assert result["status"] == "error"
    assert result["sources"] == []
