"""
ONE-TIME SETUP SCRIPT — run this on your OWN COMPUTER, not on GitHub.

This opens a browser once so you can authorize your YouTube channel,
then prints the token content you need to paste into a GitHub Secret.

Usage:
    1. Place your downloaded client_secrets.json in config/client_secrets.json
    2. Run: python generate_youtube_token.py
    3. Log in with the Google account that owns your YouTube channel
    4. Copy the printed JSON into a GitHub Secret named YOUTUBE_TOKEN_JSON
    5. Also copy the contents of config/client_secrets.json into a GitHub
       Secret named YOUTUBE_CLIENT_SECRETS_JSON
"""

import google_auth_oauthlib.flow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "config/client_secrets.json"


def main():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES
    )
    creds = flow.run_local_server(port=0)

    print("\n" + "=" * 70)
    print("SUCCESS! Copy everything between the lines below into a")
    print("GitHub Secret named: YOUTUBE_TOKEN_JSON")
    print("=" * 70)
    print(creds.to_json())
    print("=" * 70)


if __name__ == "__main__":
    main()
