import pytest

from src.config import MAX_TOPIC_LENGTH
from src.utils import sanitize_topic_for_filename, save_report, validate_topic


def test_save_report(tmp_path, monkeypatch):
    from pathlib import Path

    import src.utils as utils_module

    monkeypatch.setattr(utils_module, "Path", lambda *args: Path(tmp_path) / "reports")

    file_path = save_report("测试主题", "# 报告内容")
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == "# 报告内容"


def test_save_report_sanitizes_filename(tmp_path, monkeypatch):
    from pathlib import Path

    import src.utils as utils_module

    monkeypatch.setattr(utils_module, "Path", lambda *args: Path(tmp_path) / "reports")

    file_path = save_report("主题/带斜杠", "# 内容")
    assert "/" not in file_path.name
    assert file_path.exists()


def test_validate_topic_success():
    assert validate_topic("  AI Agent  ") == "AI Agent"


def test_validate_topic_empty():
    with pytest.raises(ValueError, match="不能为空"):
        validate_topic("   ")


def test_validate_topic_too_long():
    with pytest.raises(ValueError, match="超过最大限制"):
        validate_topic("x" * (MAX_TOPIC_LENGTH + 1))


def test_sanitize_topic_for_filename():
    assert sanitize_topic_for_filename("主题 / 研究:计划") == "主题_研究_计划"
