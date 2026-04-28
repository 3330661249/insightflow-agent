import pytest


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("ZHIPU_API_KEY", "test-key")
    monkeypatch.setenv("ZHIPU_BASE_URL", "https://test.api.example.com")
    monkeypatch.setenv("ZHIPU_CHAT_MODEL", "test-model")
    monkeypatch.setenv("BOCHA_API_KEY", "test-bocha-key")


@pytest.fixture(autouse=True)
def clear_lru_cache():
    from src.config import get_chat_llm, get_settings

    get_settings.cache_clear()
    get_chat_llm.cache_clear()
    yield
    get_settings.cache_clear()
    get_chat_llm.cache_clear()
