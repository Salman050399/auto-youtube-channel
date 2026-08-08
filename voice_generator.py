"""
Module 3: VOICE GENERATOR
Converts the script text into a natural voice-over audio file
using Piper TTS (free, offline, open-source).

Setup (one-time):
    1. Download piper binary: https://github.com/rhasspy/piper/releases
    2. Download a voice model, e.g. en_US-lessac-medium (.onnx + .onnx.json)
    3. Place both in a `voices/` folder
"""

import subprocess
import os
import yaml


def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)


def generate_voice(script_text: str, output_path: str = "audio/narration.wav") -> str:
    config = load_config()
    voice_model = config["piper_voice_model"]
    model_path = f"voices/{voice_model}.onnx"

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Voice model not found at {model_path}. "
            f"Download it from https://github.com/rhasspy/piper/releases"
        )

    os.makedirs("audio", exist_ok=True)

    piper_bin = os.environ.get("PIPER_BINARY", "piper")

    # Piper reads text from stdin and writes wav to --output_file
    process = subprocess.run(
        [piper_bin, "--model", model_path, "--output_file", output_path],
        input=script_text,
        text=True,
        capture_output=True,
    )

    if process.returncode != 0:
        raise Exception(f"Piper TTS failed: {process.stderr}")

    return output_path


if __name__ == "__main__":
    sample_text = "This is a test of the automated voice generation system."
    path = generate_voice(sample_text)
    print(f"Audio saved to: {path}")
