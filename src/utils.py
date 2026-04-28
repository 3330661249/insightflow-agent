from pathlib import Path


def save_report(topic: str, report: str):
    reports_dir = Path(__file__).resolve().parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    safe_topic = topic.replace(" ", "_").replace("/", "_")
    file_path = reports_dir / f"{safe_topic}.md"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report)

    return file_path
