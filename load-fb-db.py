import json
from datetime import datetime
from models import SessionLocal, FacebookPost

# ================= CONFIGURATION =================
JSON_FILE = "facebook_posts.json"
# =================================================

db = SessionLocal()

try:
    # 1️⃣ Load JSON
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 2️⃣ Loop through posts
    for item in json_data:

        # Convert ISO datetime string → datetime object
        date_posted = None
        if item.get("date_posted"):
            date_posted = datetime.fromisoformat(
                item["date_posted"].replace("Z", "+00:00")
            )

        post = FacebookPost(
            post_id=item["post_id"],
            user_username_raw=item.get("profile_handle"),
            content=item.get("content"),
            post_type=item.get("post_type"),
            date_posted=date_posted
        )

        # Save (upsert logic handled in model)
        post.save(db)

    print(f"✓ {len(json_data)} Facebook posts added/updated successfully!")

finally:
    db.close()