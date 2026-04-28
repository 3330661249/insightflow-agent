import requests

from src.config import SEARCH_RESULT_COUNT, SEARCH_TIMEOUT_SECONDS, get_settings
from src.logging_utils import get_logger

logger = get_logger(__name__)

BOCHA_API_URL = "https://api.bochaai.com/v1/web-search"


def search_topic(topic: str) -> str:
    settings = get_settings()
    bocha_api_key = settings.bocha_api_key

    if not bocha_api_key:
        raise ValueError("未检测到 BOCHA_API_KEY，请检查 .env 文件配置。")

    try:
        headers = {
            "Authorization": f"Bearer {bocha_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "query": topic,
            "freshness": "oneYear",
            "summary": True,
            "count": SEARCH_RESULT_COUNT,
        }

        response = requests.post(
            BOCHA_API_URL, headers=headers, json=payload, timeout=SEARCH_TIMEOUT_SECONDS
        )
        response.raise_for_status()

        return _parse_search_response(response.json(), topic)

    except requests.Timeout:
        logger.warning("搜索请求超时: topic=%r", topic)
        return f"搜索超时，未能获取到关于「{topic}」的实时信息。"
    except requests.RequestException as exc:
        logger.error("搜索请求失败: %s", exc)
        return f"搜索请求失败：{exc}"


def _parse_search_response(data: dict, topic: str) -> str:
    web_pages = data.get("data", {}).get("webPages", {}).get("value", [])

    if not web_pages:
        logger.info("搜索无结果: topic=%r", topic)
        return f"未搜索到关于「{topic}」的相关结果。"

    parts = []
    for i, item in enumerate(web_pages, start=1):
        title = item.get("title", "无标题")
        snippet = item.get("snippet", "")
        summary = item.get("summary", "")
        url = item.get("url", "")

        content = summary if summary else snippet
        entry = f"【{i}】{title}\n{content}"
        if url:
            entry += f"\n来源：{url}"
        parts.append(entry)

    logger.info("搜索完成: topic=%r, 结果数=%d", topic, len(web_pages))
    return "\n\n".join(parts)
