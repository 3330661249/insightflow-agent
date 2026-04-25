# InsightFlow-Agent

## 项目简介

InsightFlow-Agent 是一个面向主题分析场景的 Agent 工作流项目。用户输入一个研究主题后，系统会根据主题内容判断是否需要调用外部搜索工具；若需要，则先获取外部信息，再由大模型整理摘要并生成结构化报告；若不需要，则直接进入报告生成流程。

项目目标是通过状态管理、节点拆分、工具调用与图式编排，搭建一个具备基础 Agent 特征的工作流系统。

---

## 项目功能

- 支持输入研究主题

- 支持通过决策节点判断是否需要调用工具

- 支持通过真实搜索工具获取外部信息

- 支持在无 API Key 或搜索失败时自动 fallback

- 支持基于工具结果和大模型生成摘要

- 支持生成结构化 markdown 报告

- 支持使用 LangGraph 管理节点执行顺序与条件路由

- 支持将报告保存到本地 `reports/` 目录

---

## 技术栈

- Python

- LangGraph

- LangChain / langchain-openai

- TypedDict

- requests

- python-dotenv

- 智谱 GLM 系列模型

- Bocha Search API

---

## 项目结构

insightflow-agent/

├── main.py

├── requirements.txt

├── .env.example

├── README.md

├── reports/

└── src/

    ├── state.py

    ├── nodes.py

    ├── tools.py

    ├── prompts.py

    ├── graph.py

    └── utils.py