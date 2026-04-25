from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes import decide_search, collect_info, skip_tool, generate_report

def route_after_decision(state: AgentState) -> str:
    if state["need_tool"]:
        return "collect_info"
    return "skip_tool"

def build_graph():
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("decide_search", decide_search)
    graph_builder.add_node("collect_info", collect_info)
    graph_builder.add_node("skip_tool", skip_tool)
    graph_builder.add_node("generate_report", generate_report)

    graph_builder.add_edge(START, "decide_search")

    graph_builder.add_conditional_edges(
        "decide_search",
        route_after_decision,
        {
            "collect_info": "collect_info",
            "skip_tool": "skip_tool"
        }
    )

    graph_builder.add_edge("collect_info", "generate_report")
    graph_builder.add_edge("skip_tool", "generate_report")
    graph_builder.add_edge("generate_report", END)

    graph = graph_builder.compile()
    return graph