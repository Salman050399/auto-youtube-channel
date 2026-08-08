"""
Module 5: VIDEO BUILDER
Combines the voice-over audio + stock video clips + burned-in captions
into a single final video using MoviePy (built on FFmpeg).
"""

import yaml
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
    TextClip,
)


def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)


def build_video(audio_path: str, clip_paths: list, script_text: str,
                 output_path: str = "output/final_video.mp4") -> str:
    config = load_config()
    width, height = config["video_resolution"]

    narration = AudioFileClip(audio_path)
    total_duration = min(narration.duration, config["max_video_length_seconds"])

    # Loop/trim clips to fill the narration duration
    per_clip_duration = total_duration / len(clip_paths)
    processed_clips = []
    for path in clip_paths:
        clip = VideoFileClip(path)
        clip = clip.resize(height=height)
        # center-crop to target width
        if clip.w > width:
            x_center = clip.w / 2
            clip = clip.crop(x_center=x_center, width=width)
        clip = clip.subclip(0, min(per_clip_duration, clip.duration))
        processed_clips.append(clip)

    video = concatenate_videoclips(processed_clips, method="compose")
    video = video.set_audio(narration).set_duration(total_duration)

    # Simple burned-in caption (full script, bottom third, semi-transparent)
    caption = (
        TextClip(
            script_text,
            fontsize=36,
            color="white",
            font="Arial-Bold",
            method="caption",
            size=(width * 0.85, None),
            align="center",
        )
        .set_position(("center", "bottom"))
        .set_duration(total_duration)
        .margin(bottom=60, opacity=0)
    )

    final = CompositeVideoClip([video, caption])

    import os
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
