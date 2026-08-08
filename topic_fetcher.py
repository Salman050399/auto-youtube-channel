"""
Module 1: TOPIC FETCHER
Pulls latest Tech/AI news headlines using NewsAPI (free tier).
Picks one topic that hasn't been used before (tracked in topics/used.json).
"""

import requests
import json
import os
import yaml
from datetime import datetime
from secrets_loader import get_secret

USED_TOPICS_FILE = "topics/used.json"


def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)


def load_used_topics():
    if os.path.exists(USED_TOPICS_FILE):
        with open(USED_TOPICS_FILE, "r") as f:
            return json.load(f)
    return []


def save_used_topic(title):
    used = load_used_topics()
    used.append({"title": title, "date": datetime.now().isoformat()})
    os.makedirs("topics", exist_ok=True)
    with open(USED_TOPICS_FILE, "w") as f:
        json.dump(used, f, indent=2)


def fetch_topic():
    config = load_config()
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": config["news_query"],
        "language": config["news_language"],
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": get_secret("NEWS_API_KEY"),
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    articles = response.json().get("articles", [])

    if not articles:
        raise Exception("No articles found. Check your NewsAPI key/query.")

    used_titles = {t["title"] for t in load_used_topics()}

    for article in articles:
        title = article.get("title", "").strip()
        description = article.get("description", "") or ""
        if title and title not in used_titles:
            topic = {
                "title": title,
                "description": description,
                "source": article.get("source", {}).get("name", "Unknown"),
                "url": article.get("url", ""),
            }
            save_used_topic(title)
            return topic

    raise Exception("All recent articles already used. Try again later.")


if __name__ == "__main__":
    topic = fetch_topic()
    print(json.dumps(topic, indent=2))
