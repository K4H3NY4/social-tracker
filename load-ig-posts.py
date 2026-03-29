import json
from datetime import datetime
from models import SessionLocal, InstagramPost as Post

# ================= CONFIGURATION =================
JSON_FILE = "ig-sample.json"  # path to your JSON file
# =================================================

# ================= DATABASE SESSION =================
db = SessionLocal()

try:
    # 1️⃣ Read JSON from file
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 2️⃣ Loop through each post and save to DB
    for item in json_data:
        # Get post ID (required)
        content_id = item.get("post_id") or item.get("id") or item.get("code")
        if not content_id:
            print("Skipping post with no ID")
            continue

        # Convert ISO date string to datetime
        date_str = item.get("date_posted") or item.get("taken_at")
        dt = None
        if date_str:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

        # Convert list to string for coauthor_producers
        coauthors = item.get("coauthor_producers")
        if isinstance(coauthors, list):
            coauthors = ", ".join(coauthors)

        post = Post(
            content_id=content_id,
            user_posted=item.get("user_posted") or item.get("username") or item.get("user"),
            description=item.get("description") or item.get("caption"),
            content_type=item.get("content_type"),
            date_posted=dt,
            coauthor_producers=coauthors,
        )

        # Save or update the post
        post.save(db)

    print(f"✓ {len(json_data)} IG posts added/updated successfully!")

finally:
    db.close()