import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"
MAX_TOPIC_LENGTH = 500
DEFAULT_CHAT_MODEL = "glm-4-flash"
SEARCH_TIMEOUT_SECONDS = 20
SEARCH_RESULT_COUNT = 3
LLM_TIMEOUT_SECONDS = 30


def is_offline() -> bool:
    return os.getenv("INSIGHTFLOW_OFFLINE", "").lower() in {"1", "true", "yes"}


def get_search_api_key() -> str:
    return os.getenv("BOCHA_API_KEY", "").strip()


@dataclass(frozen=True)
class Settings:
    zhipu_api_key: str
    zhipu_base_url: str
    zhipu_chat_model: str
    bocha_api_key: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    api_key = os.getenv("ZHIPU_API_KEY", "").strip()
    base_url = os.getenv("ZHIPU_BASE_URL", "").strip()
    chat_model = os.getenv("ZHIPU_CHAT_MODEL", DEFAULT_CHAT_MODEL).strip() or DEFAULT_CHAT_MODEL
    bocha_key = os.getenv("BOCHA_API_KEY", "").strip()

    if not api_key:
        raise ValueError("未检测到 ZHIPU_API_KEY，请检查 .env 文件配置。")
    if not base_url:
        raise ValueError("未检测到 ZHIPU_BASE_URL，请检查 .env 文件配置。")

    return Settings(
        zhipu_api_key=api_key,
        zhipu_base_url=base_url,
        zhipu_chat_model=chat_model,
        bocha_api_key=bocha_key,
    )


@lru_cache(maxsize=1)
def get_chat_llm():
    if is_offline():
        raise ValueError("MODEL_OFFLINE")
    from langchain_openai import ChatOpenAI

    settings = get_settings()
    return ChatOpenAI(
        model=settings.zhipu_chat_model,
        api_key=settings.zhipu_api_key,
        base_url=settings.zhipu_base_url,
        temperature=0.3,
        timeout=LLM_TIMEOUT_SECONDS,
        max_retries=1,
    )
