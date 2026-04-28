from src.graph import build_graph
from src.logging_utils import get_logger
from src.state import AgentState
from src.utils import save_report, validate_topic

logger = get_logger(__name__)


def main():
    raw_topic = input("请输入研究主题: ")
    topic = validate_topic(raw_topic)

    initial_state: AgentState = {
        "topic": topic,
        "need_tool": False,
        "tool_result": "",
        "summary": "",
        "report": "",
        "decision_reason": "",
        "errors": [],
    }

    logger.info("开始执行主题分析: topic=%r", topic)
    graph = build_graph()
    final_state = graph.invoke(initial_state)

    file_path = save_report(topic, final_state.get("report", ""))

    print("\n是否调用工具：\n")
    print(final_state.get("need_tool", "未记录"))

    print("\n决策说明：\n")
    print(final_state.get("decision_reason", "未记录"))

    print("\n工具结果如下：\n")
    print(final_state.get("tool_result", "无"))

    print("\n生成报告如下：\n")
    print(final_state.get("report", "报告生成失败"))
    if final_state.get("errors"):
        print("\n流程中的异常信息：\n")
        for item in final_state["errors"]:
            print(f"- {item}")
    print(f"\n报告已保存到: {file_path}")


if __name__ == "__main__":
    main()
