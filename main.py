import argparse
import os
import sys

from src.config import get_chat_llm, get_settings
from src.graph import build_graph
from src.state import AgentState
from src.utils import save_report, validate_topic


def main(argv=None):
    parser = argparse.ArgumentParser(description="单主题研究工作流原型")
    parser.add_argument("--topic", help="研究主题；省略时交互输入")
    parser.add_argument("--offline", action="store_true", help="不加载 .env、不调用外部服务，仅演示降级路径")
    args = parser.parse_args(argv)
    try:
        topic = validate_topic(args.topic if args.topic is not None else input("请输入研究主题: "))
    except (ValueError, EOFError) as exc:
        print(f"输入错误：{exc}", file=sys.stderr)
        return 2

    previous_offline = os.environ.get("INSIGHTFLOW_OFFLINE")
    if args.offline:
        os.environ["INSIGHTFLOW_OFFLINE"] = "1"
    else:
        from dotenv import load_dotenv
        load_dotenv()
    get_settings.cache_clear()
    get_chat_llm.cache_clear()
    try:
        state: AgentState = {
            "topic": topic, "need_tool": False, "tool_result": "", "summary": "",
            "report": "", "decision_reason": "", "errors": [], "sources": [],
            "search_status": "not_requested", "status": "pending",
        }
        result = build_graph().invoke(state)
        try:
            path = save_report(topic, result["report"])
        except OSError:
            print("报告保存失败：REPORT_SAVE_FAILED，请检查输出目录权限。", file=sys.stderr)
            return 1
        print(f"运行状态：{result['status']}")
        print(f"搜索决策：{result['decision_reason']}")
        if result["errors"]:
            print(f"诊断代码：{', '.join(result['errors'])}")
        print(f"\n{result['report']}\n\n报告已保存到：{path}")
        return 0
    finally:
        if previous_offline is None:
            os.environ.pop("INSIGHTFLOW_OFFLINE", None)
        else:
            os.environ["INSIGHTFLOW_OFFLINE"] = previous_offline
        get_settings.cache_clear()
        get_chat_llm.cache_clear()


if __name__ == "__main__":
    raise SystemExit(main())
