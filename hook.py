# app.py
from flask import Flask, request, jsonify
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from datetime import datetime
import requests, os, json, logging, threading, re

# Import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler

# ────────────────────────────────────────────────────────────
# 1. SETUP & CONFIG
# ─────────────────────────────────────────────────────────────
load_dotenv()
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Load environment variables
TOKEN = os.getenv("bright_data_token")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SAVE_DIR = os.getenv("SAVE_DIR", "./platform_data") 

if not TOKEN:
    raise RuntimeError("❌ Missing 'bright_data_token' in .env file")
if not WEBHOOK_URL:
    raise RuntimeError("❌ Missing 'WEBHOOK_URL' in .env file")

os.makedirs(SAVE_DIR, exist_ok=True)

# Bright Data API config
BASE_URL = "https://api.brightdata.com/datasets/v3/trigger"

# Session with retry logic
session = requests.Session()
retry = Retry(total=3, backoff_factor=0.3, status_forcelist=[429, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)

api_headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

# Initialize Scheduler
scheduler = BackgroundScheduler()

# ─────────────────────────────────────────────────────────────
# 2. HELPER: Detect Platform
# ─────────────────────────────────────────────────────────────
def detect_platform_from_payload(data):
    platforms_found = set()
    def scan_item(item):
        if isinstance(item, dict):
            url = item.get("url", "")
            if "facebook.com" in url: platforms_found.add("facebook")
            elif "instagram.com" in url: platforms_found.add("instagram")
            elif "tiktok.com" in url: platforms_found.add("tiktok")
            for v in item.values():
                if isinstance(v, (list, dict)): scan_item(v)
        elif isinstance(item, list):
            for sub in item: scan_item(sub)
    scan_item(data)
    if len(platforms_found) == 1: return platforms_found.pop()
    elif len(platforms_found) > 1: return "mixed"
    else: return "unknown"

# ─────────────────────────────────────────────────────────────
# 3. WEBHOOK ENDPOINT
# ─────────────────────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        incoming_auth = request.headers.get("Authorization", "")
        if incoming_auth.startswith("Bearer "):
            incoming_auth = incoming_auth[7:].strip()
        
        if incoming_auth != TOKEN:
            return jsonify({"error": "unauthorized"}), 401

        raw_data = request.get_data(as_text=True)
        if not raw_data: return jsonify({"error": "empty payload"}), 400

        try:
            parsed_json = json.loads(raw_data)
        except json.JSONDecodeError:
            return jsonify({"error": "invalid json"}), 400

        platform_name = detect_platform_from_payload(parsed_json)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_platform = re.sub(r'[^a-z0-9]', '_', platform_name.lower())
        filename = f"{safe_platform}_posts.json"
        filepath = os.path.join(SAVE_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(raw_data)

        logging.info(f"✅ Saved raw data to Platform Data: {filename}")
        return jsonify({"status": "saved", "file": filename}), 200

    except Exception as e:
        logging.error(f"❌ Webhook error: {str(e)}", exc_info=True)
        return jsonify({"error": "server error"}), 500

# ─────────────────────────────────────────────────────────────
# 4. TRIGGER LOGIC (The Function to Run Automatically)
# ─────────────────────────────────────────────────────────────
def trigger_social_dataset(dataset_id, config, platform_name):
    params = {
        "dataset_id": dataset_id,
        "endpoint": WEBHOOK_URL,
        "auth_header": f"Bearer {TOKEN}",
        "format": "json",
        "uncompressed_webhook": "true",
        "include_errors": "true",
        **config.get("extra_params", {})
    }
    
    try:
        logging.info(f"🚀 Triggering {platform_name} job...")
        resp = session.post(BASE_URL, headers=api_headers, params=params, json=config["data"], timeout=30)
        resp.raise_for_status()
        result = resp.json()
        job_id = result.get("job_id", "N/A")
        logging.info(f"✅ {platform_name} job triggered: {job_id}")
        return result
    except Exception as e:
        logging.error(f"❌ {platform_name} failed: {e}", exc_info=True)
        return None

def trigger_all_platforms():
    """This function runs automatically every 8 hours"""
    logging.info("⏰ Scheduled Job Started: Triggering all platforms...")
    
    platforms = {
        "Facebook": {
            "dataset_id": "gd_lkaxegm826bjpoo9m5",
            "data": [
                {"url":"https://www.facebook.com/LGEastAfrica","start_date":"2026-04-01","end_date":"","num_of_posts":20},
                {"url":"https://www.facebook.com/BascoPaintsKenya","start_date":"2026-04-01","end_date":"","num_of_posts":20},
                {"url":"https://www.facebook.com/DPOPaybyNetwork","start_date":"2026-04-01","end_date":"","num_of_posts":100},
                {"url":"https://www.facebook.com/TotalEnergiesKenya","start_date":"2026-04-01","end_date":"","num_of_posts":100},
                {"url":"https://www.facebook.com/DoveEastAfrica","start_date":"2026-04-01","end_date":"","num_of_posts":100},
                {"url":"https://www.facebook.com/BrooksideDairyOfficial","start_date":"2026-04-01","end_date":"","num_of_posts":100},
                {"url":"https://www.facebook.com/tuzoKE","start_date":"2026-04-01","end_date":"","num_of_posts":100},
                {"url":"https://www.facebook.com/DelamereKenya","start_date":"2026-04-01","end_date":"","num_of_posts":100},
                {"url":"https://www.facebook.com/IlaraDairyProducts","start_date":"2026-04-01","end_date":"","num_of_posts":100},
                {"url":"https://www.facebook.com/profile.php?id=61556698456835","start_date":"2026-04-01","end_date":"","num_of_posts":100},
               
            ],
            "extra_params": {}
        },
        "Instagram": {
            "dataset_id": "gd_lk5ns7kz21pck8jpis",
            "data": [
                    {"url":"https://www.instagram.com/lg_eastafrica/","start_date":"2026-01-01","end_date":"","post_type":"","num_of_posts":20},
                    {"url":"https://www.instagram.com/basco_paints/","start_date":"2026-01-01","end_date":"","post_type":"","num_of_posts":20},
                    {"url":"https://www.instagram.com/dpo_bynetwork/","start_date":"2026-04-01","end_date":"","post_type":"","num_of_posts":100},
                    {"url":"https://www.instagram.com/visa_kenya/","start_date":"2026-04-01","end_date":"","post_type":"","num_of_posts":100},
                    {"url":"https://www.instagram.com/totalenergies_ke/","start_date":"2026-04-01","end_date":"","post_type":"","num_of_posts":100},
                    {"url":"https://www.instagram.com/dove.kenya/","start_date":"2026-04-01","end_date":"","post_type":"","num_of_posts":100},
                    {"url":"https://www.instagram.com/brooksidedairyltd/","start_date":"2026-04-01","end_date":"","post_type":"","num_of_posts":100},
                    {"url":"https://www.instagram.com/tuzo_ke/","start_date":"2026-04-01","end_date":"","post_type":"","num_of_posts":100},
                    {"url":"https://www.instagram.com/delamerekenya/","start_date":"2026-04-01","end_date":"","post_type":"","num_of_posts":100},
                    {"url":"https://www.instagram.com/ilaradairyproducts/","start_date":"2026-04-01","end_date":"","post_type":"","num_of_posts":100},
                    {"url":"https://www.instagram.com/brookside___plus/","start_date":"2026-04-01","end_date":"","post_type":"","num_of_posts":100},

                    
                
            ],
            "extra_params": {"type": "discover_new", "discover_by": "url"}
        },
        "TikTok": {
            "dataset_id": "gd_m7n5v2gq296pex2f5m",
            "data": [
                {"url":"https://www.tiktok.com/@lg_eastafrica","num_of_posts":10},
                {"url":"https://www.tiktok.com/@bascopaintskenya","num_of_posts":10},
                {"url":"https://www.tiktok.com/@dpopaybynetwork","num_of_posts":100},
                {"url":"https://www.tiktok.com/@totalenergieske","num_of_posts":100},
                {"url":"https://www.tiktok.com/@brookside.dairyltd","num_of_posts":100},
                {"url":"https://www.tiktok.com/@delamerekenya","num_of_posts":100},
                {"url":"https://www.tiktok.com/@tuzokenya","num_of_posts":100},
                {"url":"https://www.tiktok.com/@delamerekenya","num_of_posts":100},
                    
            ],
            "extra_params": {}
        }
    }

    for name, config in platforms.items():
        # Run sequentially or wrap in threads if you want them parallel
        trigger_social_dataset(config["dataset_id"], config, name)
    
    logging.info(" Scheduled Job Finished.")

# ─────────────────────────────────────────────────────────────
# 5. MANUAL TRIGGER ROUTE (Optional: for testing)
# ─────────────────────────────────────────────────────────────
@app.route("/trigger", methods=["POST"])
def manual_trigger():
    """Allows you to manually trigger via POST if needed"""
    threading.Thread(target=trigger_all_platforms, daemon=True).start()
    return jsonify({"status": "triggered_manually"}), 202

# ─────────────────────────────────────────────────────────────
# 6. SCHEDULER SETUP & RUN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Add the job: Run every 8 hours
    scheduler.add_job(
        func=trigger_all_platforms, 
        trigger="interval", 
        hours=4,
        id="social_scrape_job", 
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    
    logging.info("⏰ Scheduler started: Jobs will run every 4 hours.")
    logging.info(f"🌐 Server starting on port 5020...")
    
    # Optional: Run once immediately on startup (remove comment to enable)
    # trigger_all_platforms() 

    app.run(host="0.0.0.0", port=5020, debug=True)