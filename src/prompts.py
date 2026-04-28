from langchain_core.prompts import ChatPromptTemplate

DECIDE_SEARCH_SYSTEM = """你是一个判断助手。你的任务是判断用户输入的研究主题是否需要搜索实时信息。

以下情况需要搜索：
- 涉及最新动态、新闻、近期变化
- 需要获取最新的数据、统计、事件
- 时间敏感的信息（如"本周"、"今年"、"近期"等）

以下情况不需要搜索：
- 纯理论、概念解释、知识性问答
- 历史事件、已有定论的话题
- 通用技术知识、方法论

请只回答"是"或"否"，不要输出其他内容。"""

DECIDE_SEARCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", DECIDE_SEARCH_SYSTEM),
    ("human", "研究主题：{topic}"),
])

COLLECT_INFO_SYSTEM = """你是一个信息分析助手。
用户会给你一个研究主题，同时系统会提供一段通过工具获取到的初步信息。

请基于研究主题和工具结果，输出一段简洁的信息摘要。

要求：
1. 使用中文
2. 内容清晰、结构简单
3. 控制在 3-5 条要点
4. 尽量基于工具结果进行整理，不要脱离给定内容随意扩展"""

COLLECT_INFO_PROMPT = ChatPromptTemplate.from_messages([
    ("system", COLLECT_INFO_SYSTEM),
    ("human", "研究主题：\n{topic}\n\n工具结果：\n{tool_result}"),
])

GENERATE_REPORT_SYSTEM = """你是一个研究报告生成助手。
请根据给定主题和信息摘要，生成一份结构化 markdown 报告。

要求：
1. 使用中文
2. 包含以下部分：
   - 研究主题
   - 信息摘要
   - 初步结论
   - 后续建议
3. 表达简洁清晰，适合阅读"""

GENERATE_REPORT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", GENERATE_REPORT_SYSTEM),
    ("human", "研究主题：\n{topic}\n\n信息摘要：\n{summary}"),
])
