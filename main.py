from src.state import AgentState
from src.graph import build_graph
from src.utils import save_report

def main():
    topic = input("请输入研究主题: ")

    initial_state: AgentState = {
        "topic": topic,
        "need_tool": False,
        "tool_result": "",
        "summary": "",
        "report": ""
    }

    graph = build_graph()
    final_state = graph.invoke(initial_state)

    file_path = save_report(topic, final_state.get("report", ""))

    print("\n是否调用工具：\n")
    print(final_state.get("need_tool", "未记录"))

    print("\n工具结果如下：\n")
    print(final_state.get("tool_result", "无"))

    print("\n生成报告如下：\n")
    print(final_state.get("report", "报告生成失败"))
    print(f"\n报告已保存到: {file_path}")

if __name__ == "__main__":
    main()