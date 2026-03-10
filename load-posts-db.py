import json
import sqlite3
import pandas as pd
from datetime import datetime

# ================= CONFIGURATION =================
JSON_FILE = "festivebreadke_posts.json"
DB_FILE = "instagram_clients.db"
TABLE_NAME = "instagram_posts"
USERNAME = "festivebreadke"
# =================================================

print(f"📂 Reading {JSON_FILE}...")

try:
    with open(JSON_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
    print("✓ JSON loaded successfully\n")
except FileNotFoundError:
    print(f"✗ Error: File '{JSON_FILE}' not found.")
    exit()
except json.JSONDecodeError as e:
    print(f"✗ Invalid JSON: {e}")
    exit()

# ================= EXTRACT POSTS =================
rows = []

for post in data.get("posts", []):
    node = post.get("node", {})
    
    code = node.get("code")
    caption = node.get("caption", {}).get("text")
    
    # Convert lists to JSON strings for SQLite storage
    video_versions = json.dumps(node.get("video_versions", []))
    carousel_media = json.dumps(node.get("carousel_media", []))
    
    timestamp = node.get("taken_at")
    
    if not code:
        continue
    
    # Convert unix timestamp -> datetime
    taken_at = None
    if isinstance(timestamp, (int, float)):
        taken_at = datetime.fromtimestamp(timestamp)
    
    # ✅ FIXED: Include ALL 6 fields matching the INSERT statement
    rows.append((code, caption, video_versions, carousel_media, taken_at, USERNAME))

print(f"✓ Extracted {len(rows)} posts\n")

# ================= DATABASE =================
print(f"🗄️ Connecting to database: {DB_FILE}")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    caption TEXT,
    video_versions TEXT,
    carousel_media TEXT,
    taken_at DATETIME,
    username TEXT
)
""")

print(f"✓ Table '{TABLE_NAME}' ready\n")

# ================= INSERT DATA =================
print(f"📝 Inserting {len(rows)} records...")

try:
    # ✅ FIXED: 6 columns = 6 placeholders
    cursor.executemany(f"""
        INSERT OR REPLACE INTO {TABLE_NAME}
        (code, caption, video_versions, carousel_media, taken_at, username)
        VALUES (?, ?, ?, ?, ?, ?)
    """, rows)
    
    conn.commit()
    print("✓ Insert completed\n")
except sqlite3.Error as e:
    print(f"✗ Database error: {e}")
    conn.rollback()

# ================= VERIFY =================
print("=" * 100)
print(f"DATABASE CONTENTS ({TABLE_NAME})")
print("=" * 100)

df = pd.read_sql_query(f"""
SELECT code, caption, video_versions, carousel_media, taken_at, username
FROM {TABLE_NAME}
ORDER BY taken_at DESC
""", conn)

pd.set_option("display.max_colwidth", 80)
pd.set_option("display.width", 150)

print(df.to_string(index=False))

print("=" * 100)
print(f"Total Records: {len(df)}\n")

# ================= CLOSE =================
conn.close()

print("✓ Database connection closed")
print(f"✓ Database saved as: {DB_FILE}")