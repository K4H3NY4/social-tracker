import requests
import json

# ================= API REQUEST =================
url = "https://tiktok-api6.p.rapidapi.com/user/videos"

querystring = {"username": "festivebreadke"}

headers = {
    "x-rapidapi-key": "bd5904a96cmsh3edcc696733215fp1eeb5ajsne133bf560c27",
    "x-rapidapi-host": "tiktok-api6.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

data = response.json()

# ================= EXTRACT FIELDS =================
videos = []
for video in data.get("videos", []):
    videos.append({
        "author": video.get("author"),
        "video_id": video.get("video_id"),
        "create_time": video.get("create_time"),
        "description": video.get("description")
    })

# ================= SAVE AS JSON FILE =================
output_file = "festivebreadke_videos.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(videos, f, ensure_ascii=False, indent=4)

print(f"✓ Saved {len(videos)} videos to '{output_file}'")