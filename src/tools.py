from urllib.parse import urlsplit

import requests

from src.config import SEARCH_RESULT_COUNT, SEARCH_TIMEOUT_SECONDS, get_search_api_key, is_offline
from src.logging_utils import get_logger
from src.state import SearchResult, Source

logger = get_logger(__name__)
BOCHA_API_URL = "https://api.bochaai.com/v1/web-search"


def _failure(status: str, code: str) -> SearchResult:
    logger.warning("搜索未返回证据: code=%s", code)
    return {"status": status, "sources": [], "error_code": code}


def search_topic(topic: str) -> SearchResult:
    if is_offline():
        return _failure("unavailable", "SEARCH_OFFLINE")
    api_key = get_search_api_key()
    if not api_key:
        return _failure("unavailable", "SEARCH_NOT_CONFIGURED")
    try:
        response = requests.post(
            BOCHA_API_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"query": topic, "freshness": "oneYear", "summary": True, "count": SEARCH_RESULT_COUNT},
            timeout=SEARCH_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return _parse_search_response(response.json(), topic)
    except requests.Timeout:
        return _failure("error", "SEARCH_TIMEOUT")
    except requests.RequestException:
        return _failure("error", "SEARCH_REQUEST_FAILED")
    except (ValueError, TypeError):
        return _failure("error", "SEARCH_INVALID_RESPONSE")


def _parse_search_response(data: object, topic: str) -> SearchResult:
    # HTTP success does not imply a valid provider envelope or usable evidence.
    if not isinstance(data, dict):
        return _failure("error", "SEARCH_INVALID_RESPONSE")
    if data.get("code") not in (None, 200, "200"):
        return _failure("error", "SEARCH_PROVIDER_ERROR")
    envelope = data.get("data")
    if not isinstance(envelope, dict) or not isinstance(envelope.get("webPages"), dict):
        return _failure("error", "SEARCH_INVALID_RESPONSE")
    pages = envelope["webPages"].get("value")
    if not isinstance(pages, list):
        return _failure("error", "SEARCH_INVALID_RESPONSE")
    if not pages:
        return _failure("empty", "SEARCH_EMPTY")

    sources: list[Source] = []
    for item in pages[:SEARCH_RESULT_COUNT]:
        if not isinstance(item, dict):
            continue
        url = item.get("url", "")
        content = item.get("summary") or item.get("snippet") or ""
        if not isinstance(url, str) or not isinstance(content, str) or not content.strip():
            continue
        try:
            parsed_url = urlsplit(url)
            if parsed_url.scheme not in {"https", "http"} or not parsed_url.hostname or parsed_url.username:
                continue
        except ValueError:
            continue
        title = item.get("name") or item.get("title") or "无标题"
        published_at = item.get("datePublished") or ""
        sources.append({
            "id": f"S{len(sources) + 1}", "title": title if isinstance(title, str) else "无标题",
            "url": url, "content": content.strip(),
            "published_at": published_at if isinstance(published_at, str) else "",
        })
    if not sources:
        return _failure("error", "SEARCH_INVALID_RESPONSE")
    return {"status": "ok", "sources": sources, "error_code": ""}
