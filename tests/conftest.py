import os
import socket

import pytest

# Set before src.config can import python-dotenv; tests never read a real .env.
os.environ["PYTHON_DOTENV_DISABLED"] = "1"


@pytest.fixture(autouse=True)
def prohibit_network(monkeypatch):
    attempts = []

    def denied(*args, **kwargs):
        attempts.append(True)
        raise AssertionError("Tests must stub external APIs; network is disabled")

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket.socket, "connect_ex", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket, "getaddrinfo", denied)
    yield
    assert not attempts, "A test attempted network access, even if product code caught the error"


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.delenv("INSIGHTFLOW_OFFLINE", raising=False)
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
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
