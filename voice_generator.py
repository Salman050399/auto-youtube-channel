"""
Module 3: VOICE GENERATOR
Converts the script text into a natural voice-over audio file using
ElevenLabs (free tier - no card required, just email signup).
Much more natural sounding than offline TTS engines like Piper.

Get a free API key: https://elevenlabs.io (Sign up -> Profile -> API Keys)
Free tier: ~10,000 characters/month, plenty for one short video/day.
"""

import os
import requests
from secrets_loader import get_secret

# "Adam" - a clear, natural-sounding default voice available on the free tier.
# Browse more voices at https://elevenlabs.io/app/voice-library and swap the ID.
DEFAULT_VOICE_ID = "pNInz6obpgDQGcFmaJgB"


def generate_voice(script_text: str, output_path: str = "audio/narration.mp3") -> str:
    os.makedirs("audio", exist_ok=True)

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{DEFAULT_VOICE_ID}",
        headers={
            "xi-api-key": get_secret("ELEVENLABS_API_KEY"),
            "Content-Type": "application/json",
        },
        json={
            "text": script_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.45,
                "similarity_boost": 0.8,
                "style": 0.35,
                "use_speaker_boost": True,
            },
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise Exception(
            f"ElevenLabs TTS failed ({response.status_code}): {response.text}"
        )

    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path


if __name__ == "__main__":
    sample_text = "This is a test of the automated voice generation system."
    path = generate_voice(sample_text)
    print(f"Audio saved to: {path}")
