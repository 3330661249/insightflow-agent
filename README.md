# InsightFlow-Agent

## 项目简介

InsightFlow-Agent 是一个面向主题分析场景的轻量 Agent 工作流项目。用户输入研究主题后，系统会先判断是否需要外部搜索，再根据搜索结果整理摘要并生成结构化 Markdown 报告；若主题不依赖实时信息，则直接跳过工具调用进入报告生成。

这一版重点补了工程化骨架：集中配置、输入校验、日志记录、失败降级和报告落盘，方便在本地稳定演示，也更接近可讲述的项目形态。

## 项目功能

- 支持输入研究主题并进行长度与空值校验
- 支持使用决策节点判断是否需要调用实时搜索工具
- 支持通过 Bocha Search API 获取主题相关网页摘要
- 支持在无 API Key、搜索失败或 LLM 调用异常时自动降级
- 支持基于工具结果生成摘要，并进一步生成结构化 Markdown 报告
- 支持记录决策说明与流程中的异常信息
- 支持使用 LangGraph 管理节点执行顺序与条件路由
- 支持将报告保存到本地 `reports/` 目录

## 技术栈

- Python

- LangGraph

- LangChain / langchain-openai

- TypedDict

- requests

- python-dotenv

- logging

- 智谱 GLM 系列模型

- Bocha Search API

## 项目结构

```text
insightflow-agent/
├── main.py
├── README.md
├── reports/
├── src/
│   ├── config.py
│   ├── graph.py
│   ├── logging_utils.py
│   ├── nodes.py
│   ├── prompts.py
│   ├── state.py
│   ├── tools.py
│   └── utils.py
└── tests/
```

## 当前流程

1. `main.py` 读取用户输入并校验主题长度。
2. `decide_search` 用 LLM 判断是否需要搜索，失败时降级到关键词匹配。
3. 若需要搜索，`collect_info` 调用 Bocha Search API 并整理摘要。
4. `generate_report` 基于摘要生成 Markdown 报告。
5. `save_report` 将结果保存到本地，并输出流程中的决策说明与异常信息。

## 已知限制

- 目前还是单主题单轮流程，暂不支持多轮追问或记忆。
- 搜索工具返回仍以文本摘要为主，尚未完全结构化。
- 真实端到端效果依赖外部模型与搜索接口可用性。
