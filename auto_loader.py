import json
import os
import glob
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from models import SessionLocal, FacebookPost, InstagramPost, TikTokVideo

# ================= CONFIGURATION =================
# Folder where your JSON files are saved (e.g., from the webhook)
DATA_FOLDER = "./platform_data"  # <-- Change this to your actual folder path
# File patterns to look for
FILE_PATTERNS = ["*.json"]

# Mapping of keywords to Platform Models
PLATFORM_MAP = {
    "facebook": {"model": FacebookPost, "keywords": ["facebook", "fb"]},
    "instagram": {"model": InstagramPost, "keywords": ["instagram", "ig"]},
    "tiktok": {"model": TikTokVideo, "keywords": ["tiktok", "tt"]}
}
# ==================================================

def get_platform_from_filename(filename):
    """Detects platform based on filename keywords."""
    lower_name = filename.lower()
    for platform, config in PLATFORM_MAP.items():
        if any(kw in lower_name for kw in config["keywords"]):
            return platform
    return "unknown"

def parse_date(date_str):
    """Safely converts various date formats to datetime object."""
    if not date_str:
        return None
    try:
        clean_str = str(date_str).replace("Z", "+00:00")
        return datetime.fromisoformat(clean_str)
    except ValueError:
        try:
            return datetime.fromtimestamp(float(date_str))
        except (ValueError, TypeError):
            return None

def process_facebook(data, db):
    count = 0
    for item in data:
        if not isinstance(item, dict): continue
        post_id = item.get("post_id") or item.get("id")
        if not post_id: continue
        
        # Check if already exists to avoid duplicates (optional optimization)
        # existing = db.query(FacebookPost).filter_by(post_id=post_id).first()
        # if existing: continue 

        date_posted = parse_date(item.get("date_posted"))
        post = FacebookPost(
            post_id=post_id,
            user_username_raw=item.get("profile_handle") or item.get("username"),
            content=item.get("content") or item.get("message"),
            post_type=item.get("post_type"),
            date_posted=date_posted
        )
        post.save(db)
        count += 1
    return count

def process_instagram(data, db):
    count = 0
    for item in data:
        if not isinstance(item, dict): continue
        post_id = item.get("post_id") or item.get("id") or item.get("code")
        if not post_id: continue

        date_str = item.get("date_posted") or item.get("taken_at")
        dt = parse_date(date_str)

        coauthors = item.get("coauthor_producers")
        if isinstance(coauthors, list):
            coauthors = ", ".join([str(x) for x in coauthors])

        post = InstagramPost(
            content_id=post_id,
            user_posted=item.get("user_posted") or item.get("username") or item.get("user"),
            description=item.get("description") or item.get("caption"),
            content_type=item.get("content_type"),
            date_posted=dt,
            coauthor_producers=coauthors
        )
        post.save(db)
        count += 1
    return count

def process_tiktok(data, db):
    count = 0
    for item in data:
        if not isinstance(item, dict): continue
        post_id = item.get("post_id") or item.get("video_id") or item.get("id")
        if not post_id: continue

        time_val = item.get("create_time") or item.get("timestamp")
        dt = None
        if time_val:
            if isinstance(time_val, (int, float)):
                dt = datetime.fromtimestamp(time_val)
            else:
                dt = parse_date(time_val)

        video = TikTokVideo(
            video_id=post_id,
            author=item.get("account_id") or item.get("author") or item.get("username"),
            description=item.get("description") or item.get("text"),
            post_type=item.get("post_type"),
            create_time=dt
        )
        video.save(db)
        count += 1
    return count

def run_loader_job():
    """The main function that runs every 2 hours."""
    print(f"\n⏰ [{datetime.now()}] Starting scheduled data load...")
    
    db = SessionLocal()
    total_processed = 0
    files_found = 0

    try:
        # Find all JSON files in the folder
        json_files = []
        for pattern in FILE_PATTERNS:
            json_files.extend(glob.glob(os.path.join(DATA_FOLDER, pattern)))
        
        # Remove duplicates and sort
        json_files = sorted(list(set(json_files)))

        if not json_files:
            print("️ No JSON files found to process.")
            return

        for file_path in json_files:
            filename = os.path.basename(file_path)
            print(f"📂 Processing: {filename}")
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                
                if isinstance(json_data, dict):
                    json_data = json_data.get("data") or json_data.get("results") or []
                
                if not isinstance(json_data, list):
                    continue

                platform = get_platform_from_filename(filename)
                count = 0

                if platform == "facebook":
                    count = process_facebook(json_data, db)
                elif platform == "instagram":
                    count = process_instagram(json_data, db)
                elif platform == "tiktok":
                    count = process_tiktok(json_data, db)
                else:
                    # Fallback detection
                    if json_data and isinstance(json_data[0], dict):
                        first = json_data[0]
                        if "profile_handle" in first: count = process_facebook(json_data, db)
                        elif "coauthor_producers" in first: count = process_instagram(json_data, db)
                        elif "create_time" in first: count = process_tiktok(json_data, db)
                
                if count > 0:
                    print(f"   ✅ Saved {count} records from {platform.upper()}")
                    total_processed += count
                    files_found += 1
                
                # Optional: Move processed file to 'archive' folder to avoid re-processing
                # archive_dir = os.path.join(DATA_FOLDER, "processed")
                # os.makedirs(archive_dir, exist_ok=True)
                # os.rename(file_path, os.path.join(archive_dir, filename))

            except Exception as e:
                print(f"   ❌ Error processing {filename}: {e}")

        print(f" Job Complete. Files: {files_found}, Records: {total_processed}")

    except Exception as e:
        print(f"❌ Critical Error in Job: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Initializing Auto-Loader (Runs every 2 hours)...")
    
    # Run once immediately on startup
    run_loader_job()

    # Setup Scheduler
    scheduler = BlockingScheduler()
    
    # Schedule job every 2 hours
    scheduler.add_job(
        func=run_loader_job,
        trigger="interval",
        hours=2,
        id="social_data_loader",
        replace_existing=True
    )
    
    print("⏳ Waiting for next run in 2 hours... (Press Ctrl+C to stop)")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n Scheduler stopped.")