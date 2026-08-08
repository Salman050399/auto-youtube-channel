"""
Module 6: THUMBNAIL GENERATOR
Creates a simple but eye-catching thumbnail using Pillow -
title text over a frame grabbed from the final video.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip


def generate_thumbnail(video_path: str, title: str,
                        output_path: str = "thumbnails/thumb.jpg") -> str:
    os.makedirs("thumbnails", exist_ok=True)

    # Grab a frame ~2 seconds in as the background
    clip = VideoFileClip(video_path)
    frame_time = min(2, clip.duration / 2)
    frame = clip.get_frame(frame_time)
    img = Image.fromarray(frame).convert("RGB")
    img = img.resize((1280, 720))

    # Dark gradient overlay at the bottom for text readability
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(img.height - 300, img.height):
        alpha = int(180 * (y - (img.height - 300)) / 300)
        draw.line([(0, y), (img.width, y)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
    except OSError:
        font = ImageFont.load_default()

    # Wrap title text to fit width
    words = title.split()
    lines, current_line = [], ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > 1150:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    lines.append(current_line)

    y_text = img.height - 40 - (len(lines) * 75)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x_text = (img.width - (bbox[2] - bbox[0])) / 2
        draw.text((x_text, y_text), line, font=font, fill="white",
                   stroke_width=3, stroke_fill="black")
        y_text += 75

    img.save(output_path, quality=90)
    return output_path


if __name__ == "__main__":
    generate_thumbnail("output/final_video.mp4", "This AI Breakthrough Changes Everything")
