"""
Module 7: YOUTUBE UPLOADER
Uploads the finished video + thumbnail to YouTube using the
YouTube Data API v3.

IMPORTANT — how auth works in this GitHub Actions setup:
    Since GitHub Actions runs on a fresh machine every time (no browser,
    no persistent files), the OAuth token must be generated ONCE on your
    own computer, then stored as a GitHub Secret so every automated run
    can reuse it without a browser popping up.

    One-time local steps (see README "YouTube API access" section):
        1. Run `python generate_youtube_token.py` on your own PC once.
        2. It opens a browser, you log in/authorize your channel.
        3. It prints the contents of token.json — copy that into a
           GitHub Secret called YOUTUBE_TOKEN_JSON.
        4. Also copy your client_secrets.json contents into a GitHub
           Secret called YOUTUBE_CLIENT_SECRETS_JSON.
"""

import os
import json
import yaml
import googleapiclient.discovery
import googleapiclient.http
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from secrets_loader import get_secret

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)


def get_authenticated_service():
    token_data = json.loads(get_secret("YOUTUBE_TOKEN_JSON"))
    creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception(
                "YouTube token is invalid/expired and has no refresh token. "
                "Re-run generate_youtube_token.py locally and update the "
                "YOUTUBE_TOKEN_JSON secret."
            )

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)


def upload_video(video_path: str, thumbnail_path: str, title: str,
                  description: str, tags: list) -> str:
    config = load_config()
    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": config["youtube_category_id"],
        },
        "status": {
            "privacyStatus": config["youtube_privacy_status"],
            "selfDeclaredMadeForKids": False,
        },
    }

    media = googleapiclient.http.MediaFileUpload(
        video_path, chunksize=-1, resumable=True, mimetype="video/mp4"
    )

    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]

    if os.path.exists(thumbnail_path):
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=googleapiclient.http.MediaFileUpload(thumbnail_path),
        ).execute()

    print(f"Uploaded: https://youtube.com/watch?v={video_id}")
    return video_id


if __name__ == "__main__":
    upload_video(
        "output/final_video.mp4",
        "thumbnails/thumb.jpg",
        "Test Upload",
        "This is a test description.",
        ["test", "ai"],
    )
