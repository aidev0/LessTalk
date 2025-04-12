import yt_dlp
import os
from urllib.parse import urlparse, parse_qs

def download_youtube_by_id(url, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)

    # Extract video ID
    query = parse_qs(urlparse(url).query)
    video_id = query.get("v", [None])[0]
    if not video_id:
        raise ValueError("Invalid YouTube URL: can't extract video ID")

    output_path = os.path.join(output_dir, f"{video_id}.mp4")

    # ✅ Force h264 video + aac audio for MAVI compatibility
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]',
        'merge_output_format': 'mp4',
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print(f"✅ Downloaded (MAVI-ready) to: {output_path}")
    return output_path
