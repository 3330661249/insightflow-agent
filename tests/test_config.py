import pytest

from src.config import MAX_TOPIC_LENGTH, get_settings


def test_get_settings(mock_env_vars):
    settings = get_settings()
    assert settings.zhipu_api_key == "test-key"
    assert settings.zhipu_base_url == "https://test.api.example.com"
    assert settings.zhipu_chat_model == "test-model"
    assert settings.bocha_api_key == "test-bocha-key"


def test_get_settings_cached(mock_env_vars):
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_get_settings_missing_api_key(monkeypatch):
    monkeypatch.delenv("ZHIPU_API_KEY", raising=False)
    from src.config import get_settings

    get_settings.cache_clear()
    with pytest.raises(ValueError, match="ZHIPU_API_KEY"):
        get_settings()


def test_get_settings_missing_base_url(monkeypatch):
    monkeypatch.delenv("ZHIPU_BASE_URL", raising=False)
    from src.config import get_settings

    get_settings.cache_clear()
    with pytest.raises(ValueError, match="ZHIPU_BASE_URL"):
        get_settings()


def test_max_topic_length():
    assert MAX_TOPIC_LENGTH == 500
