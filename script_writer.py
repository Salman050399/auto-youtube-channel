"""
Module 2: SCRIPT WRITER
Uses Groq's free API (very fast, generous free tier, no card needed)
to turn a news topic into a short video script + title + description
+ search keywords for visuals.

Get a free API key: https://console.groq.com/keys
"""

import requests
import json
import yaml
from secrets_loader import get_secret


def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)


def generate_script(topic: dict) -> dict:
    config = load_config()

    prompt = f"""You are writing a short YouTube video script (under 60 seconds spoken,
about 130-150 words) about this tech/AI news story.

Headline: {topic['title']}
Summary: {topic['description']}
Source: {topic['source']}

Return ONLY valid JSON, no markdown, no extra text, in this exact format:
{{
  "title": "catchy YouTube title, under 70 characters",
  "script": "the full spoken narration script, plain text, no stage directions",
  "description": "2-3 sentence YouTube video description",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "visual_keywords": ["keyword1", "keyword2", "keyword3"]
}}
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {get_secret('GROQ_API_KEY')}",
            "Content-Type": "application/json",
        },
        json={
            "model": config["groq_model"],
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.7,
        },
        timeout=60,
    )
    response.raise_for_status()
    raw_output = response.json()["choices"][0]["message"]["content"]

    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        raise Exception(f"Groq did not return valid JSON:\n{raw_output}")

    required_keys = {"title", "script", "description", "tags", "visual_keywords"}
    if not required_keys.issubset(result.keys()):
        raise Exception(f"Groq output missing required fields: {result}")

    return result


if __name__ == "__main__":
    from topic_fetcher import fetch_topic

    topic = fetch_topic()
    script_data = generate_script(topic)
    print(json.dumps(script_data, indent=2))
