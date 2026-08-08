"""
Module 4: VISUAL FETCHER
Downloads free, royalty-free stock video clips from Pexels
based on keywords extracted from the script.
"""

import requests
import os
import yaml
from secrets_loader import get_secret


def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)


def fetch_clips(keywords: list, output_dir: str = "visuals") -> list:
    config = load_config()
    headers = {"Authorization": get_secret("PEXELS_API_KEY")}
    os.makedirs(output_dir, exist_ok=True)

    downloaded_paths = []
    clips_needed = config.get("num_stock_clips", 5)
    per_keyword = max(1, clips_needed // max(1, len(keywords)))

    for keyword in keywords:
        if len(downloaded_paths) >= clips_needed:
            break

        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params={"query": keyword, "per_page": per_keyword, "orientation": "landscape"},
            timeout=15,
        )
        resp.raise_for_status()
        videos = resp.json().get("videos", [])

        for video in videos:
            if len(downloaded_paths) >= clips_needed:
                break
            # pick a decent quality file (hd)
            files = sorted(
                video["video_files"],
                key=lambda f: f.get("width", 0),
                reverse=True,
            )
            hd_files = [f for f in files if f.get("width", 0) <= 1920]
            chosen = hd_files[0] if hd_files else files[-1]

            file_path = os.path.join(output_dir, f"clip_{len(downloaded_paths)}.mp4")
            video_data = requests.get(chosen["link"], timeout=60)
            with open(file_path, "wb") as f:
                f.write(video_data.content)
            downloaded_paths.append(file_path)

    if not downloaded_paths:
        raise Exception("No stock clips could be downloaded. Check keywords/API key.")

    return downloaded_paths


if __name__ == "__main__":
    clips = fetch_clips(["artificial intelligence", "technology", "computer"])
    print(clips)
