import json
import os
import re
import subprocess
import tempfile
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o"
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_segments(audio_results, video_results, style="recap"):
    if style not in ["tiktok", "recap"]:
        raise ValueError("Invalid style: must be 'tiktok' or 'recap'")

    tiktok_system_prompt = """
You are a creative TikTok video editor. Given a transcript with timestamps, extract up to 10 visually and emotionally engaging moments totaling no more than 30 seconds.

Return JSON: a list of up to 10 objects. Each object must include:
- segment_start_time (in seconds)
- segment_end_time (in seconds)
- content (the corresponding text)

Only include moments that would make viewers stop scrolling: surprising, powerful, visual, emotional, or funny.

Return only valid JSON. Do not include any extra explanation or text.
"""

    recap_system_prompt = """
You are an academic assistant helping students study. From a transcript with timestamps, extract up to 20 educational moments totaling no more than 120 seconds.

Return JSON: a list of up to 20 objects. Each object must include:
- segment_start_time (in seconds)
- segment_end_time (in seconds)
- content (the corresponding text)

Focus on clear, useful, and information-dense content. Summarize the most essential concepts from the transcript.

Return only valid JSON. Do not include any extra explanation or text.
"""

    system_message = tiktok_system_prompt if style == "tiktok" else recap_system_prompt

    transcriptions = []
    if style == "tiktok":
        transcriptions = (
            video_results.get("data", {}).get("transcriptions", []) +
            audio_results.get("data", {}).get("transcriptions", [])
        )
    else:
        transcriptions = audio_results.get("data", {}).get("transcriptions", [])

    messages = [
        {"role": "system", "content": system_message.strip()},
        {"role": "user", "content": json.dumps(transcriptions)}
    ]

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except Exception:
        match = re.search(r"(\[.*\])", content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise ValueError("Invalid response format")

def edit_video_with_ffmpeg(segments, input_video_path, prefix="Recap", output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    temp_dir = tempfile.mkdtemp()
    segment_paths = []

    video_filename = os.path.basename(input_video_path)
    video_name = os.path.splitext(video_filename)[0]
    output_path = os.path.join(output_dir, f"{prefix}_{video_name}.mp4")

    for i, seg in enumerate(segments):
        start = float(seg["segment_start_time"])
        end = float(seg["segment_end_time"])
        duration = end - start
        out_path = os.path.join(temp_dir, f"segment_{i}.mp4")
        segment_paths.append(out_path)

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", input_video_path,
            "-t", str(duration),
            "-c:v", "libx264", "-c:a", "aac",
            out_path
        ]
        subprocess.run(cmd, check=True)

    list_file_path = os.path.join(temp_dir, "list.txt")
    with open(list_file_path, "w") as f:
        for seg_path in segment_paths:
            f.write(f"file '{seg_path}'\n")

    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file_path,
        "-c", "copy",
        output_path
    ]
    subprocess.run(concat_cmd, check=True)

    return output_path

def make_recap(audio_results, video_results, input_video_path):
    segments = extract_segments(audio_results, video_results, style="recap")
    return edit_video_with_ffmpeg(segments, input_video_path, prefix="Recap", output_dir="results")

def make_tiktok(audio_results, video_results, input_video_path):
    segments = extract_segments(audio_results, video_results, style="tiktok")
    return edit_video_with_ffmpeg(segments, input_video_path, prefix="TikTok", output_dir="results")
