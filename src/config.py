import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

MAX_TOPIC_LENGTH = 500
VECTORSTORE_ROOT = os.getenv("VECTORSTORE_ROOT", "")


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
    chat_model = os.getenv("ZHIPU_CHAT_MODEL", "glm-4-flash").strip()
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
    from langchain_openai import ChatOpenAI

    settings = get_settings()
    return ChatOpenAI(
        model=settings.zhipu_chat_model,
        api_key=settings.zhipu_api_key,
        base_url=settings.zhipu_base_url,
        temperature=0.3,
    )
