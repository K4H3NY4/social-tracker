from flask import Flask, request, jsonify
import requests
import threading
import os
import json
from datetime import datetime

app = Flask(__name__)

# Token
TOKEN = "3bb5d1d5-cff1-4c14-aacb-d441ebe63e58"

SAVE_DIR = "webhook_data"
os.makedirs(SAVE_DIR, exist_ok=True)


# -----------------------------
# 1. WEBHOOK (receives results)
# -----------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # --- Auth check ---
        if request.headers.get("Authorization") != TOKEN:
            return jsonify({"error": "unauthorized"}), 401

        payload = request.get_json(force=True)

        print("\nReceived payload type:", type(payload))

        # --- FIX: handle both list and dict ---
        if isinstance(payload, list):
            results = payload
        elif isinstance(payload, dict):
            results = payload.get("data") or payload.get("results") or []
        else:
            results = []

        print(f"Processing {len(results)} posts...")

        # --- Filter fields ---
        filtered_posts = []
        for post in results:
            if not isinstance(post, dict):
                continue  # skip weird entries

            filtered_posts.append({
                "profile_handle": post.get("profile_handle"),
                "post_id": post.get("post_id"),
                "content": post.get("content"),
                "post_type": post.get("post_type"),
                "date_posted": post.get("date_posted") or post.get("timestamp")
            })

        # --- Save JSON ---
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"facebook_posts.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(filtered_posts, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved: {filename}")

        return jsonify({"status": "saved", "count": len(filtered_posts)}), 200

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": "server error"}), 500


# -----------------------------
# 2. TRIGGER JOB
# -----------------------------
def trigger_job():
    try:
        url = "https://api.brightdata.com/datasets/v3/trigger"

        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        }

        params = {
            "dataset_id": "sd_mn2z791x7mc4pskjn",
            "endpoint": "https://abb6-217-21-114-58.ngrok-free.app/webhook",  # 🔁 replace if ngrok changes
            "auth_header": TOKEN,
            "format": "json",
            "uncompressed_webhook": "true",
            "include_errors": "true",
        }

        data = [
            {
                "url": "https://www.facebook.com/Festivebreadke",
                "num_of_posts": 150,
                "start_date": "",
                "end_date": ""
            }
        ]

        response = requests.post(url, headers=headers, params=params, json=data)

        print("\n🚀 Trigger response:")
        print(response.json())

    except Exception as e:
        print("❌ Trigger error:", str(e))


# -----------------------------
# 3. RUN EVERYTHING
# -----------------------------
if __name__ == "__main__":
    # Run trigger in background
    threading.Thread(target=trigger_job).start()

    # Start Flask
    app.run(port=5000, debug=True)