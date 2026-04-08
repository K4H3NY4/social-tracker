import os
import json
import logging
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()
logging.basicConfig(level=logging.INFO)
app = Flask(__name__) 

# Config
BASE_URL = "https://api.brightdata.com/datasets/v3/trigger"
API_TOKEN = os.getenv("bright_data_token")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


# Session with retries
session = requests.Session()
retry = Retry(total=3, backoff_factor=0.3, status_forcelist=[429, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}


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


def trigger_social_dataset(dataset_id, payload, platform_name):
    params = {
        "dataset_id": dataset_id,
        "endpoint": WEBHOOK_URL,
        "auth_header": f"Bearer {API_TOKEN}",
        "format": "json",
        "uncompressed_webhook": "true",
        "include_errors": "true",
        **payload.get("extra_params", {})
    }
    
    try:
        resp = session.post(BASE_URL, headers=headers, params=params, json=payload["data"], timeout=30)
        resp.raise_for_status()
        result = resp.json()
        logging.info(f"✅ {platform_name} job triggered: {result.get('job_id', 'N/A')}")
        return result
    except Exception as e:
        logging.error(f"❌ {platform_name} failed: {e}")
        return None

# Usage
platforms = {
    "Facebook": {
        "dataset_id": "gd_lkaxegm826bjpoo9m5",
        "data": [
            {"url":"https://www.facebook.com/LGEastAfrica","start_date":"2026-01-01","end_date":"","num_of_posts":10},
            {"url":"https://www.facebook.com/BascoPaintsKenya","start_date":"2026-01-01","end_date":"","num_of_posts":10},
        ],
        "extra_params": {}
    },
    "Instagram": {
        "dataset_id": "gd_lk5ns7kz21pck8jpis",
        "data": [
            {"url":"https://www.instagram.com/lg_eastafrica/","start_date":"2026-01-01","end_date":"","post_type":"","num_of_posts":10},
            {"url":"https://www.instagram.com/basco_paints/","start_date":"2026-01-01","end_date":"","post_type":"","num_of_posts":10},
        ],
        "extra_params": {"type": "discover_new", "discover_by": "url"}
    },
    "TikTok": {
        "dataset_id": "gd_m7n5v2gq296pex2f5m",
        "data": [
            {"url":"https://www.tiktok.com/@lg_eastafrica","num_of_posts":10},
            {"url":"https://www.tiktok.com/@bascopaintskenya","num_of_posts":10},
        ],
        "extra_params": {}  # Add endpoint/auth if supported
    }
}

for name, config in platforms.items():
    trigger_social_dataset(config["dataset_id"], config, name)