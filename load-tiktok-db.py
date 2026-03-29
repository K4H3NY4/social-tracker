import json
from datetime import datetime
from models import SessionLocal, TikTokVideo

# ================= CONFIGURATION =================
JSON_FILE = "tiktok-sample.json"  # path to your JSON file
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
     
        dt = datetime.fromisoformat(item["create_time"].replace("Z", "+00:00"))

        video = TikTokVideo(
            video_id=item["post_id"],
            author=item.get("account_id"),
            description=item.get("description"),
            post_type=item.get("post_type"),
            create_time=dt
        )

        # Save or update the video
        video.save(db)

    print(f"✓ {len(json_data)} TikTok videos added/updated successfully!")

finally:
    db.close()