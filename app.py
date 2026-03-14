from flask import Flask, render_template, request, jsonify
from models import SessionLocal, init_db, Post, Client
from models import TikTokVideo
import datetime
from datetime import datetime, timedelta, timezone
from google import genai
import os
from dotenv import load_dotenv


# Load .env file
load_dotenv()

app = Flask(__name__)

# Get the API key from environment variables
api_key = os.environ.get("API_KEY")  
genai_client = genai.Client(api_key=api_key)



# initialize database
init_db()


# ================= DB SESSION HELPER =================

def get_db():
    return SessionLocal()


@app.route("/")
def index():
    db = get_db()
    try:
        clients = db.query(Client).all()
        return render_template("index.html", clients=clients)
    finally:
        db.close()


# ================= POSTS API =================

@app.route("/posts", methods=["GET"])
def get_posts():
    db = get_db()

    limit = request.args.get("limit", 100)

    try:
        posts = Post.get_all(db, int(limit))
        return jsonify([p.to_dict() for p in posts])
    finally:
        db.close()


@app.route("/posts/<code>", methods=["GET"])
def get_post(code):
    db = get_db()

    try:
        post = Post.get_by_code(db, code)

        if not post:
            return jsonify({"error": "Post not found"}), 404

        return jsonify(post.to_dict())
    finally:
        db.close()


@app.route("/posts", methods=["POST"])
def create_post():
    db = get_db()

    try:
        data = request.get_json()

        if not data or "code" not in data:
            return jsonify({"error": "code is required"}), 400

        post = Post(
            code=data["code"],
            caption=data.get("caption"),
            taken_at=data.get("taken_at"),
            username=data.get("username")
        )

        post = post.save(db)

        return jsonify(post.to_dict())

    finally:
        db.close()


@app.route("/posts/search", methods=["GET"])
def search_posts():
    db = get_db()

    keyword = request.args.get("q")

    if not keyword:
        return jsonify({"error": "q query parameter required"}), 400

    try:
        posts = Post.search_by_caption(db, keyword)
        return jsonify([p.to_dict() for p in posts])
    finally:
        db.close()


@app.route("/posts/user/<username>", methods=["GET"])
def posts_by_user(username):
    db = get_db()

    try:
        posts = Post.get_by_username(db, username)
        return jsonify([p.to_dict() for p in posts])
    finally:
        db.close()


@app.route("/posts/<code>", methods=["DELETE"])
def delete_post(code):
    db = get_db()

    try:
        post = Post.get_by_code(db, code)

        if not post:
            return jsonify({"error": "Post not found"}), 404

        post.delete(db)

        return jsonify({"message": "Post deleted"})
    finally:
        db.close()


# ================= DATE RANGE =================

@app.route("/posts/<username>/range", methods=["GET"])
def posts_by_user_date_range(username):
    db = get_db()

    start_date = request.args.get("start")
    end_date = request.args.get("end")

    if not start_date or not end_date:
        return jsonify({
            "error": "start and end query parameters required"
        }), 400

    try:
        posts = Post.get_by_username_date_range(
            db,
            username,
            start_date,
            end_date
        )

        return jsonify([p.to_dict() for p in posts])

    finally:
        db.close()


@app.route("/posts/<username>/last7days", methods=["GET"])
def posts_last_7_days(username):

    db = SessionLocal()

    # get posts for the last 7 days
    posts = Post.get_last_7_days_by_username(db, username)

    # convert to dict
    posts_list = [p.to_dict() for p in posts]

    # include count
    result = {
        "count": len(posts_list),
        "posts": posts_list
    }

    db.close()

    return jsonify(result)


# ================= TIKTOK API =================

@app.route("/tiktok", methods=["GET"])
def get_tiktok_videos():
    db = get_db()
    limit = request.args.get("limit", 100)

    try:
        videos = TikTokVideo.get_all(db, int(limit))
        return jsonify([v.to_dict() for v in videos])
    finally:
        db.close()


@app.route("/tiktok/<video_id>", methods=["GET"])
def get_tiktok_video(video_id):
    db = get_db()

    try:
        video = TikTokVideo.get_by_video_id(db, video_id)

        if not video:
            return jsonify({"error": "Video not found"}), 404

        return jsonify(video.to_dict())
    finally:
        db.close()


@app.route("/tiktok/author/<author>", methods=["GET"])
def tiktok_videos_by_author(author):
    db = get_db()

    try:
        videos = TikTokVideo.get_by_author(db, author)
        return jsonify([v.to_dict() for v in videos])
    finally:
        db.close()


@app.route("/tiktok/author/<author>/last7days", methods=["GET"])
def tiktok_last_7_days(author):
    db = get_db()

    try:
        videos = TikTokVideo.get_last_7_days_by_author(db, author)
        videos_list = [v.to_dict() for v in videos]

        result = {
            "count": len(videos_list),
            "videos": videos_list
        }

        return jsonify(result)
    finally:
        db.close()


@app.route("/tiktok", methods=["POST"])
def create_tiktok_video():
    db = get_db()

    try:
        data = request.get_json()

        required_fields = ["video_id", "author"]
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"{', '.join(required_fields)} required"}), 400

        video = TikTokVideo(
            video_id=data["video_id"],
            author=data.get("author"),
            description=data.get("description"),
            create_time=data.get("create_time")
        )

        video = video.save(db)

        return jsonify(video.to_dict())

    finally:
        db.close()


@app.route("/tiktok/<video_id>", methods=["DELETE"])
def delete_tiktok_video(video_id):
    db = get_db()

    try:
        video = TikTokVideo.get_by_video_id(db, video_id)

        if not video:
            return jsonify({"error": "Video not found"}), 404

        video.delete(db)
        return jsonify({"message": "Video deleted"})
    finally:
        db.close()


# ================= CLIENTS API =================

@app.route("/clients", methods=["GET"])
def get_clients():
    db = get_db()

    try:
        clients = Client.get_all(db)
        return jsonify([c.to_dict() for c in clients])
    finally:
        db.close()


@app.route("/clients/<int:client_id>", methods=["GET"])
def get_client(client_id):
    db = get_db()

    try:
        client = Client.get_by_id(db, client_id)

        if not client:
            return jsonify({"error": "Client not found"}), 404

        result = client.to_dict()
        result["posts"] = [p.to_dict() for p in client.get_posts(db)]

        return jsonify(result)

    finally:
        db.close()


@app.route("/clients", methods=["POST"])
def create_client():
    db = get_db()

    try:
        data = request.get_json()

        if not data or "name" not in data:
            return jsonify({"error": "name is required"}), 400

        client = Client(
            name=data["name"],
            instagram=data.get("instagram"),
            facebook=data.get("facebook"),
            tiktok=data.get("tiktok"),
            contract=data.get("contract")
        )

        client = client.save(db)

        return jsonify(client.to_dict())

    finally:
        db.close()


@app.route("/clients/search", methods=["GET"])
def search_clients():
    db = get_db()

    keyword = request.args.get("q")

    if not keyword:
        return jsonify({"error": "q query parameter required"}), 400

    try:
        clients = Client.search_by_name(db, keyword)
        return jsonify([c.to_dict() for c in clients])
    finally:
        db.close()


@app.route("/clients/<int:client_id>", methods=["PUT"])
def edit_client(client_id):
    db = get_db()  # get a database session

    try:
        client = Client.get_by_id(db, client_id)

        if not client:
            return jsonify({"error": "Client not found"}), 404

        data = request.json

        # Update only provided fields
        client.name = data.get("name", client.name)
        client.instagram = data.get("instagram", client.instagram)
        client.facebook = data.get("facebook", client.facebook)
        client.tiktok = data.get("tiktok", client.tiktok)
        client.contract = data.get("contract", client.contract)

        client.save(db)

        return jsonify({
            "message": "Client updated successfully",
            "client": client.to_dict()
        })

    finally:
        db.close()


@app.route("/clients/<int:client_id>", methods=["DELETE"])
def delete_client(client_id):
    db = get_db()

    try:
        client = Client.get_by_id(db, client_id)

        if not client:
            return jsonify({"error": "Client not found"}), 404

        client.delete(db)

        return jsonify({"message": "Client deleted"})

    finally:
        db.close()


@app.route("/summary/<client_name>/7days", methods=["GET"])
def summary_last_7days_count(client_name):
    db = SessionLocal()
    try:
        # ✅ Calculate date (timezone aware - not deprecated)
   
        seven_days_ago = datetime.utcnow() - timedelta(days=8)

        # ✅ Fetch Client
        client = db.query(Client).filter(Client.name == client_name).first()
        if not client:
            return jsonify({"error": f"Client '{client_name}' not found"}), 404

        # ================= INSTAGRAM COUNTS =================
        ig_count = 0
        ig_video_count = 0
        ig_carousel_count = 0
        ig_static_count = 0

        if client.instagram:
            # Base query for last 7 days
            base_query = db.query(Post).filter(
                Post.username == client.instagram,
                Post.taken_at >= seven_days_ago
            )

            # Total Instagram posts
            ig_count = base_query.count()

            # Video posts (video_versions IS NOT NULL)
            ig_video_count = base_query.filter(
                Post.video_versions != 'null'
            ).count()

            # Carousel posts (carousel_media IS NOT NULL)
            ig_carousel_count = base_query.filter(
                Post.carousel_media.isnot('null')
            ).count()

            # Static posts (BOTH are NULL)
            ig_static_count = base_query.filter(
                Post.video_versions.is_('null'),
                Post.carousel_media.is_('null')
            ).count()

        # ================= TIKTOK COUNTS =================
        tt_count = 0
        if client.tiktok:
            tt_count = db.query(TikTokVideo).filter(
                TikTokVideo.author == client.tiktok,
                TikTokVideo.create_time >= seven_days_ago
            ).count()

        # ================= GENERATE AI SUMMARY =================
        ai_summary = "AI summary generation unavailable."
        
        try:
            prompt = (
                f"📊 CLIENT PERFORMANCE REPORT (Date Range: {start_str} to {end_str})\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Client Name: {client.name}\n"
                f"Instagram: {client.instagram or 'Not linked'}\n"
                f"TikTok: {client.tiktok or 'Not linked'}\n"
                f"Facebook: {client.facebook or 'Not linked'}\n"
                f"Contract: {client.contract or 'N/A'}\n\n"
                f"📈 INSTAGRAM METRICS:\n"
                f"   • Total Posts: {ig_count}\n"
                f"   • 🎥 Video Posts: {ig_video_count}\n"
                f"   • 🎠 Carousel Posts: {ig_carousel_count}\n"
                f"   • 📷 Static Posts: {ig_static_count}\n\n"
                f"📈 TIKTOK METRICS:\n"
                f"   • Total Videos: {tt_count}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"TASK: Analyze if posting frequency and content mix meets expectations.\n"
                f"Consider: Video engagement typically outperforms static posts.\n"
                f"Provide brief executive summary and recommendations for the period {start_str} to {end_str}.\n\n"
                f"⚠️ FORMATTING RULES (STRICT):\n"
                f"- Use PLAIN TEXT ONLY — NO Markdown syntax\n"
                f"- Do NOT use: **bold**, *italic*, ### headers, | tables |, or --- dividers\n"
                f"- Use emojis and simple line breaks for visual structure\n"
                f"- Use ALL CAPS or emojis for emphasis instead of bold/italic\n"
                f"- Format numbers and lists with simple bullets (•) or dashes (-)\n"
                f"- Format all output as plain text with no markdown\n\n"
                f"- Use actual table where posible.\n"
                f"Example of desired format:\n"
                f"📊 EXECUTIVE SUMMARY\n"
                f"The account is over-performing with 24 Instagram posts in 6 weeks...\n\n"
                f"💡 RECOMMENDATIONS\n"
                f"• Optimize content mix: shift static posts to video\n"
                f"• Repurpose top TikToks as Instagram Reels\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )

            response = genai_client.models.generate_content(
                model="gemini-3-flash-preview",  # ✅ Use valid model name
                contents=prompt
            )
            ai_summary = response.text

        except Exception as ai_error:
            print(f"⚠️ AI Generation Error: {ai_error}")
            ai_summary = "Unable to generate AI summary at this time. Please try again later."

        # ================= RETURN RESPONSE =================
        return jsonify({
            "status": "success",
            "period": "last_7_days",
            "summary": {
                "instagram": {
                    "video": ig_video_count,
                    "carousel": ig_carousel_count,
                    "static": ig_static_count,
                    "total": ig_count,
                },
                "tiktok": {
                    "total": tt_count
                },
                "ai_summary": ai_summary
            }
        })

    except Exception as e:
        print(f"❌ Server Error: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

    finally:
        db.close()


@app.route("/summary/<client_name>/range", methods=["GET"])
def summary_date_range(client_name):
    db = SessionLocal()
    try:
        # ================= 1. PARSE DATE RANGE =================
        start_str = request.args.get('start_date')
        end_str = request.args.get('end_date')

        if not start_str or not end_str:
            return jsonify({"error": "Missing required query parameters: 'start_date' and 'end_date' (Format: YYYY-MM-DD)"}), 400

        try:
            start_dt = datetime.strptime(start_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            end_dt = datetime.strptime(end_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        except ValueError:
            return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD"}), 400

        # ================= 2. FETCH CLIENT =================
        client = db.query(Client).filter(Client.name == client_name).first()
        if not client:
            return jsonify({"error": f"Client '{client_name}' not found"}), 404

        # ================= 3. INSTAGRAM POSTS =================
        ig_posts_query = []
        ig_count = ig_video_count = ig_carousel_count = ig_static_count = 0

        if client.instagram:
            base_query = db.query(Post).filter(
                Post.username == client.instagram,
                Post.taken_at >= start_dt,
                Post.taken_at <= end_dt
            )

            ig_count = base_query.count()
            ig_video_count = base_query.filter(Post.video_versions != 'null').count()
            ig_carousel_count = base_query.filter(Post.carousel_media.isnot('null')).count()
            ig_static_count = base_query.filter(Post.video_versions.is_('null'), Post.carousel_media.is_('null')).count()

            ig_posts_query = base_query.with_entities(Post.caption, Post.taken_at, Post.video_versions, Post.carousel_media).all()

        # ================= 4. TIKTOK POSTS =================
        tt_posts_query = []
        tt_count = 0
        if client.tiktok:
            base_tt = db.query(TikTokVideo).filter(
                TikTokVideo.author == client.tiktok,
                TikTokVideo.create_time >= start_dt,
                TikTokVideo.create_time <= end_dt
            )

            tt_count = base_tt.count()
            tt_posts_query = base_tt.with_entities(TikTokVideo.description, TikTokVideo.create_time).all()

        # ================= 5. FORMAT POSTS =================
        posts = []

        for p in ig_posts_query:
            posts.append({
                "platform": "instagram",
                "caption": p.caption,
                "taken_at": p.taken_at.isoformat(),
                "video_versions": p.video_versions,
                "carousel_media": p.carousel_media
            })

        for p in tt_posts_query:
            posts.append({
                "platform": "tiktok",
                "description": p.description,
                "create_time": p.create_time.isoformat()
            })

        # ================= 6. AI SUMMARY =================
        ai_summary = "AI summary generation unavailable."
        try:
            prompt = (
                f"📊 CLIENT PERFORMANCE REPORT (Date Range: {start_str} to {end_str})\n"
                f"Client Name: {client.name}\n"
                f"Instagram: {client.instagram or 'Not linked'}\n"
                f"TikTok: {client.tiktok or 'Not linked'}\n\n"
                f"Instagram Posts: {ig_count} (Video: {ig_video_count}, Carousel: {ig_carousel_count}, Static: {ig_static_count})\n"
                f"TikTok Posts: {tt_count}\n"
                f"Include captions, descriptions and dates in the summary in a table format from the database.\n"
                f"Generate a brief executive report for the period {start_str} to {end_str}. "
                f"The report should include:Executive Summary Provide a concise overview of the client’s social media activity, highlighting key patterns in posting frequency, platform usage, and content types."
                f"Strategic Recommendations  \n"
                f"Provide 3–5 clear and actionable recommendations to improve content strategy, posting consistency, and platform performance."
                f"Formatting Guidelines:"
                f"    - Use readable text with emojis for section headers."
                f"    - Use line breaks and short paragraphs for clarity."
                f"    - Keep the tone professional and suitable for executives."
                f"    - This report was generated by crAIg, Creative Edge’s AI-powered reporting assistant."
            )
            response = genai_client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            ai_summary = response.text
        except Exception as ai_error:
            print(f"⚠️ AI Generation Error: {ai_error}")
            ai_summary = "Unable to generate AI summary at this time."

        # ================= 7. RETURN RESPONSE =================
        return jsonify({
            "status": "success",
            "period": f"{start_str} to {end_str}",
            "summary": {
                "instagram": {
                    "video": ig_video_count,
                    "carousel": ig_carousel_count,
                    "static": ig_static_count,
                    "total": ig_count
                },
                "tiktok": {
                    "total": tt_count
                },
                "ai_summary": ai_summary
            },
            "posts": posts
        })

    except Exception as e:
        print(f"❌ Server Error: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

    finally:
        db.close()

# ================= STATS =================

@app.route("/stats", methods=["GET"])
def stats():
    db = get_db()

    try:
        data = {
            "posts": Post.count(db),
            "clients": Client.count(db)
        }

        return jsonify(data)

    finally:
        db.close()


# ================= RUN SERVER =================

if __name__ == "__main__":
  
    app.run(debug=True, host="0.0.0.0", port=5001)