import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
MAVI_API_KEY = os.getenv("MAVI_API_KEY")
HEADERS = {"Authorization": MAVI_API_KEY}


def upload_video(video_path):
    files = {
        "file": (os.path.basename(video_path), open(video_path, "rb"), "video/mp4")
    }
    response = requests.post(
        "https://mavi-backend.openinterx.com/api/serve/video/upload",
        files=files,
        headers=HEADERS,
    )
    return response.json()["data"]  # returns dict with videoNo, etc.


def get_video_metadata(video_no):
    response = requests.get(
        "https://mavi-backend.openinterx.com/api/serve/video/searchDB",
        headers=HEADERS
    )
    data = response.json().get("data", {}).get("videoData", [])
    for video in data:
        if video["videoNo"] == video_no:
            return video
    return None


def submit_transcription(video_no, transcription_type="AUDIO"):
    if transcription_type not in ["AUDIO", "VIDEO"]:
        raise ValueError("Invalid type")

    payload = {
        "videoNo": video_no,
        "type": transcription_type
    }

    response = requests.post(
        "https://mavi-backend.openinterx.com/api/serve/video/subTranscription",
        headers=HEADERS,
        json=payload,
    )
    return response.json()  # includes taskNo


def get_transcription(task_no):
    response = requests.get(
        "https://mavi-backend.openinterx.com/api/serve/video/getTranscription",
        headers=HEADERS,
        params={"taskNo": task_no},
    )
    return response.json()
