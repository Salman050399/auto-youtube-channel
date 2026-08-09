"""
Module 5: VIDEO BUILDER
Combines the voice-over audio + stock video clips + burned-in captions
into a single final video using MoviePy (built on FFmpeg).

Captions are rendered with Pillow (not MoviePy's TextClip/ImageMagick),
since ImageMagick's default security policy on Ubuntu CI runners blocks
the text-rendering operations TextClip relies on.
"""

import os
import yaml
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
    ImageClip,
)


def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)


def _make_caption_image(text: str, width: int, height: int) -> np.ndarray:
    """Render caption text onto a transparent RGBA image using Pillow."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40
        )
    except OSError:
        font = ImageFont.load_default()

    max_width = int(width * 0.85)
    words = text.split()
    lines, current = [], ""
    for word in words:
        test_line = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > max_width:
            lines.append(current)
            current = word
        else:
            current = test_line
    if current:
        lines.append(current)

    line_height = 55
    total_height = len(lines) * line_height
    y = height - total_height - 60

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (width - (bbox[2] - bbox[0])) / 2
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            draw.text((x + dx, y + dy), line, font=font, fill="black")
        draw.text((x, y), line, font=font, fill="white")
        y += line_height

    return np.array(img)


def build_video(audio_path: str, clip_paths: list, script_text: str,
                 output_path: str = "output/final_video.mp4") -> str:
    config = load_config()
    width, height = config["video_resolution"]

    narration = AudioFileClip(audio_path)
    total_duration = min(narration.duration, config["max_video_length_seconds"])

    per_clip_duration = total_duration / len(clip_paths)
    processed_clips = []
    for path in clip_paths:
        clip = VideoFileClip(path)
        clip = clip.resize(height=height)
        if clip.w > width:
            x_center = clip.w / 2
            clip = clip.crop(x_center=x_center, width=width)
        clip = clip.subclip(0, min(per_clip_duration, clip.duration))

        # Ken Burns style slow zoom-in: resize larger over time, then
        # composite onto a fixed-size canvas so the output frame size
        # stays constant while the visible content appears to zoom in.
        clip_duration = clip.duration
        base_w, base_h = clip.size
        zoomed = clip.resize(lambda t: 1 + 0.06 * (t / clip_duration))
        zoomed = zoomed.set_position(("center", "center"))
        clip = CompositeVideoClip([zoomed], size=(base_w, base_h)).set_duration(clip_duration)

        processed_clips.append(clip)

    video = concatenate_videoclips(processed_clips, method="compose")
    video = video.set_audio(narration).set_duration(total_duration)

    caption_array = _make_caption_image(script_text, width, height)
    caption = ImageClip(caption_array).set_duration(total_duration)

    final = CompositeVideoClip([video, caption])

    os.makedirs("output", exist_ok=True)
    final.write_videofile(
        output_path,
        fps=config["video_fps"],
        codec="libx264",
        audio_codec="aac",
        threads=4,
    )

    return output_path


if __name__ == "__main__":
    build_video(
        "audio/narration.wav",
        ["visuals/clip_0.mp4", "visuals/clip_1.mp4"],
        "Sample caption text for testing.",
    )
