import json
from datetime import datetime
from models import SessionLocal, TikTokVideo

# ================= CONFIGURATION =================
JSON_FILE = "festivebreadke_videos.json"  # path to your JSON file
# =================================================

# ================= DATABASE SESSION =================
db = SessionLocal()

try:
    # 1️⃣ Read JSON from file
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 2️⃣ Loop through each video and save to DB
    for item in json_data:
        # Convert UNIX timestamp to datetime
        dt = datetime.utcfromtimestamp(item["create_time"])

        video = TikTokVideo(
            video_id=item["video_id"],
            author=item.get("author"),
            description=item.get("description"),
            create_time=dt
        )

        # Save or update the video
        video.save(db)

    print(f"✓ {len(json_data)} TikTok videos added/updated successfully!")

finally:
    db.close()