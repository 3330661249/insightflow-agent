import re
from pathlib import Path

from src.config import MAX_TOPIC_LENGTH, REPORTS_DIR
from src.logging_utils import get_logger

logger = get_logger(__name__)


def validate_topic(topic: str) -> str:
    normalized_topic = topic.strip()
    if not normalized_topic:
        raise ValueError("研究主题不能为空。")
    if len(normalized_topic) > MAX_TOPIC_LENGTH:
        raise ValueError(f"研究主题超过最大限制：{MAX_TOPIC_LENGTH} 字符。")
    return normalized_topic


def sanitize_topic_for_filename(topic: str) -> str:
    normalized = re.sub(r"\s+", "_", topic.strip())
    sanitized = re.sub(r'[\\\\/:*?\"<>|]+', "_", normalized)
    compacted = re.sub(r"_+", "_", sanitized).strip("_")
    return compacted or "report"


def save_report(topic: str, report: str):
    reports_dir = Path(REPORTS_DIR)
    reports_dir.mkdir(exist_ok=True)

    safe_topic = sanitize_topic_for_filename(topic)
    file_path = reports_dir / f"{safe_topic}.md"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info("报告已保存: topic=%r, path=%s", topic, file_path)
    return file_path
