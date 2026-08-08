"""
SECRETS LOADER
All API keys/tokens come from environment variables — never hardcoded
or committed to the repo. In GitHub Actions, these are injected from
GitHub Secrets (Settings -> Secrets and variables -> Actions).

Required environment variables:
    NEWS_API_KEY
    PEXELS_API_KEY
    GROQ_API_KEY
    YOUTUBE_CLIENT_SECRETS_JSON   (contents of client_secrets.json, as a string)
    YOUTUBE_TOKEN_JSON            (contents of token.json, as a string)
"""

import os


def get_secret(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(
            f"Missing required environment variable: {name}. "
            f"Set it locally (export {name}=...) or as a GitHub Actions secret."
        )
    return value
