from src.graph import build_graph, route_after_decision


def test_route_to_collect_info():
    state = {"need_tool": True}
    assert route_after_decision(state) == "collect_info"


def test_route_to_skip_tool():
    state = {"need_tool": False}
    assert route_after_decision(state) == "skip_tool"


def test_build_graph():
    graph = build_graph()
    assert graph is not None
