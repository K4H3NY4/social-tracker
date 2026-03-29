from datetime import datetime, timedelta, timezone
from typing import List, Optional
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session

from db.session import SessionLocal
from models.instagram import InstagramPost

instagram_bp = Blueprint("instagram", __name__)


def get_post_by_content_id(db: Session, content_id: str) -> Optional[InstagramPost]:
    """Fetch a single Instagram post by its unique content_id."""
    return db.query(InstagramPost).filter(InstagramPost.content_id == content_id).first()


def get_all_posts(db: Session, limit: int = 100, offset: int = 0) -> List[InstagramPost]:
    """Fetch recent Instagram posts with pagination support."""
    return db.query(InstagramPost).order_by(
        InstagramPost.date_posted.desc()
    ).offset(offset).limit(limit).all()


def search_posts(db: Session, keyword: str) -> List[InstagramPost]:
    """Search posts by description/caption (case-insensitive)."""
    return db.query(InstagramPost).filter(
        InstagramPost.description.ilike(f"%{keyword}%")
    ).order_by(InstagramPost.date_posted.desc()).all()


def get_posts_by_user(db: Session, username: str) -> List[InstagramPost]:
    """Fetch all posts by a specific Instagram username."""
    # Normalize: remove @ if present
    username = username.lstrip('@')
    return db.query(InstagramPost).filter(
        InstagramPost.user_posted == username
    ).order_by(InstagramPost.date_posted.desc()).all()


def get_posts_by_date_range(
    db: Session, 
    start_date: datetime, 
    end_date: datetime
) -> List[InstagramPost]:
    """Fetch posts within a specific date range."""
    return db.query(InstagramPost).filter(
        InstagramPost.date_posted >= start_date,
        InstagramPost.date_posted <= end_date
    ).order_by(InstagramPost.date_posted.desc()).all()


def get_posts_by_user_and_date(
    db: Session, 
    username: str, 
    start_date: datetime, 
    end_date: datetime
) -> List[InstagramPost]:
    """Fetch posts by user within a date range."""
    username = username.lstrip('@')
    return db.query(InstagramPost).filter(
        InstagramPost.user_posted == username,
        InstagramPost.date_posted >= start_date,
        InstagramPost.date_posted <= end_date
    ).order_by(InstagramPost.date_posted.desc()).all()


def get_posts_last_7_days(db: Session, username: str) -> List[InstagramPost]:
    """Fetch posts by user from the last 7 days (UTC)."""
    username = username.lstrip('@')
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    return db.query(InstagramPost).filter(
        InstagramPost.user_posted == username,
        InstagramPost.date_posted >= seven_days_ago
    ).order_by(InstagramPost.date_posted.desc()).all()


def count_posts(db: Session) -> int:
    """Return total count of Instagram posts."""
    return db.query(InstagramPost).count()


def count_posts_by_user(db: Session, username: str) -> int:
    """Return count of posts for a specific user."""
    username = username.lstrip('@')
    return db.query(InstagramPost).filter(
        InstagramPost.user_posted == username
    ).count()


def save_post(db: Session, post_data: dict) -> InstagramPost:
    """
    Upsert an Instagram post: create new or update existing by content_id.
    
    Args:
        db: SQLAlchemy session
        post_data: Dict with keys: content_id (required), description, date_posted, 
                   user_posted, content_type, coauthor_producers
                   
    Returns:
        The saved InstagramPost instance
    """
    # Parse date_posted if it's a string
    date_posted = post_data.get("date_posted")
    if isinstance(date_posted, str):
        try:
            date_posted = datetime.strptime(date_posted, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Fallback: try ISO format
            try:
                date_posted = datetime.fromisoformat(date_posted.replace("Z", "+00:00"))
            except ValueError:
                date_posted = None

    # Normalize username
    user_posted = post_data.get("user_posted")
    if user_posted:
        user_posted = user_posted.lstrip('@')

    # Check for existing post
    existing = db.query(InstagramPost).filter(
        InstagramPost.content_id == post_data["content_id"]
    ).first()
    
    if existing:
        # Update fields
        existing.description = post_data.get("description")
        existing.date_posted = date_posted
        existing.user_posted = user_posted
        existing.content_type = post_data.get("content_type")
        existing.coauthor_producers = post_data.get("coauthor_producers")
        db.commit()
        db.refresh(existing)
        return existing

    # Create new post
    new_post = InstagramPost(
        content_id=post_data["content_id"],
        description=post_data.get("description"),
        date_posted=date_posted,
        user_posted=user_posted,
        content_type=post_data.get("content_type"),
        coauthor_producers=post_data.get("coauthor_producers")
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


def delete_post(db: Session, post: InstagramPost) -> None:
    """Delete a post from the database."""
    db.delete(post)
    db.commit()


def delete_post_by_content_id(db: Session, content_id: str) -> bool:
    """Delete a post by content_id. Returns True if deleted, False if not found."""
    post = get_post_by_content_id(db, content_id)
    if post:
        delete_post(db, post)
        return True
    return False


@instagram_bp.route("/posts", methods=["GET"])
def list_posts():
    db = SessionLocal()
    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)

    try:
        posts = get_all_posts(db, limit=limit, offset=offset)
        return jsonify([post.to_dict() for post in posts])
    finally:
        db.close()


@instagram_bp.route("/posts/<content_id>", methods=["GET"])
def get_post(content_id: str):
    db = SessionLocal()

    try:
        post = get_post_by_content_id(db, content_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        return jsonify(post.to_dict())
    finally:
        db.close()


@instagram_bp.route("/posts", methods=["POST"])
def create_post():
    db = SessionLocal()

    try:
        data = request.get_json(silent=True) or {}
        if "content_id" not in data:
            return jsonify({"error": "content_id is required"}), 400

        post = save_post(db, data)
        return jsonify(post.to_dict())
    finally:
        db.close()


@instagram_bp.route("/posts/search", methods=["GET"])
def search_posts_route():
    db = SessionLocal()
    keyword = request.args.get("q")

    if not keyword:
        return jsonify({"error": "q query parameter required"}), 400

    try:
        posts = search_posts(db, keyword)
        return jsonify([post.to_dict() for post in posts])
    finally:
        db.close()


@instagram_bp.route("/posts/user/<username>", methods=["GET"])
def get_posts_by_username(username: str):
    db = SessionLocal()

    try:
        posts = get_posts_by_user(db, username)
        return jsonify({
            "success": True,
            "count": len(posts),
            "posts": [post.to_dict() for post in posts]
        })
    finally:
        db.close()


@instagram_bp.route("/posts/<username>/range", methods=["GET"])
def get_posts_for_user_date_range(username: str):
    db = SessionLocal()
    start_str = request.args.get("start")
    end_str = request.args.get("end")

    if not start_str or not end_str:
        return jsonify({"error": "start and end query parameters required"}), 400

    try:
        start_date = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        end_date = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
    except ValueError:
        return jsonify({"error": "Invalid date format. Use ISO 8601."}), 400

    try:
        posts = get_posts_by_user_and_date(db, username, start_date, end_date)
        return jsonify([post.to_dict() for post in posts])
    finally:
        db.close()


@instagram_bp.route("/posts/<username>/last7days", methods=["GET"])
def get_posts_for_last_7_days(username: str):
    db = SessionLocal()

    try:
        posts = get_posts_last_7_days(db, username)
        posts_list = [post.to_dict() for post in posts]
        return jsonify({"count": len(posts_list), "posts": posts_list})
    finally:
        db.close()


@instagram_bp.route("/posts/<content_id>", methods=["DELETE"])
def delete_post_route(content_id: str):
    db = SessionLocal()

    try:
        post = get_post_by_content_id(db, content_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404

        delete_post(db, post)
        return jsonify({"message": "Post deleted"})
    finally:
        db.close()
