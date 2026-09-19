from main import main


def test_offline_cli_writes_limitation_report_without_loading_dotenv(monkeypatch, tmp_path, capsys):
    import dotenv

    import src.utils as utils

    def forbidden(*args, **kwargs):
        raise AssertionError("Offline mode must not load credentials")

    monkeypatch.setattr(dotenv, "load_dotenv", forbidden)
    monkeypatch.setattr(utils, "REPORTS_DIR", tmp_path)
    assert main(["--offline", "--topic", "本周 AI 新闻"]) == 0
    report = next(tmp_path.glob("*.md")).read_text(encoding="utf-8")
    assert "未获得可用外部证据" in report
    assert "unavailable" in capsys.readouterr().out


def test_invalid_topic_returns_readable_error_without_traceback(capsys):
    assert main(["--offline", "--topic", " "]) == 2
    captured = capsys.readouterr()
    assert "不能为空" in captured.err
    assert "Traceback" not in captured.err
