"""
MAIN ORCHESTRATOR
Runs the full pipeline end-to-end, fully automatically:

  1. Fetch a fresh tech/AI news topic
  2. Generate a script (title, narration, description, tags) via local LLM
  3. Generate voice-over audio
  4. Fetch matching free stock footage
  5. Assemble the final video with captions
  6. Generate a thumbnail
  7. Upload to YouTube

Run manually:
    python main.py

Run automatically every day (Linux/Mac cron example - runs at 9 AM daily):
    crontab -e
    0 9 * * * cd /path/to/auto-youtube-channel && /usr/bin/python3 main.py >> logs.txt 2>&1
"""

import traceback
from datetime import datetime

from topic_fetcher import fetch_topic
from script_writer import generate_script
from voice_generator import generate_voice
from visual_fetcher import fetch_clips
from video_builder import build_video
from thumbnail_generator import generate_thumbnail
from youtube_uploader import upload_video


def run_pipeline():
    print(f"\n=== Pipeline started: {datetime.now().isoformat()} ===")

    print("[1/7] Fetching topic...")
    topic = fetch_topic()
    print(f"    -> {topic['title']}")

    print("[2/7] Generating script...")
    script_data = generate_script(topic)
    print(f"    -> Title: {script_data['title']}")

    print("[3/7] Generating voice-over...")
    audio_path = generate_voice(script_data["script"])

    print("[4/7] Fetching stock footage...")
    clip_paths = fetch_clips(script_data["visual_keywords"])

    print("[5/7] Building final video...")
    video_path = build_video(audio_path, clip_paths, script_data["script"])

    print("[6/7] Generating thumbnail...")
    thumbnail_path = generate_thumbnail(video_path, script_data["title"])

    print("[7/7] Uploading to YouTube...")
    video_id = upload_video(
        video_path,
        thumbnail_path,
        script_data["title"],
        script_data["description"],
        script_data["tags"],
    )

    print(f"=== Pipeline complete: https://youtube.com/watch?v={video_id} ===\n")
    return video_id


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        print(f"PIPELINE FAILED: {e}")
        traceback.print_exc()
