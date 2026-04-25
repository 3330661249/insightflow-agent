import os
import requests
from dotenv import load_dotenv

load_dotenv()

def search_topic(topic: str) -> str:
    bocha_api_key = os.getenv("BOCHA_API_KEY")

    if not bocha_api_key:
        return "DEBUG: 未读取到 BOCHA_API_KEY"

    try:
        url = "https://api.bochaai.com/v1/web-search"
        headers = {
            "Authorization": f"Bearer {bocha_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": topic,
            "freshness": "oneYear",
            "summary": True,
            "count": 3
        }

        response = requests.post(url, headers=headers, json=payload, timeout=20)

        return f"""
DEBUG REQUEST OK
status_code = {response.status_code}

response_text =
{response.text[:1500]}
""".strip()

    except Exception as e:
        return f"DEBUG EXCEPTION: {e}"