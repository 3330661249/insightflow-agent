from src.utils import save_report


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
