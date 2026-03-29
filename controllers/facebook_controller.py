# controllers/facebook_controller.py
from datetime import datetime, timedelta
from typing import List, Optional
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session

from db.session import SessionLocal
from models.facebook import FacebookPost

facebook_bp = Blueprint("facebook", __name__)

def get_post_by_id(db: Session, post_id: str) -> Optional[FacebookPost]:
    return db.query(FacebookPost).filter(FacebookPost.post_id == post_id).first()

def get_all_posts(db: Session, limit: int = 100) -> List[FacebookPost]:
    return db.query(FacebookPost).order_by(FacebookPost.date_posted.desc()).limit(limit).all()

def get_posts_by_username(db: Session, username: str) -> List[FacebookPost]:
    return db.query(FacebookPost).filter(
        FacebookPost.user_username_raw == username
    ).order_by(FacebookPost.date_posted.desc()).all()

def get_posts_last_7_days(db: Session, username: str) -> List[FacebookPost]:
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    return db.query(FacebookPost).filter(
        FacebookPost.user_username_raw == username,
        FacebookPost.date_posted >= seven_days_ago
    ).order_by(FacebookPost.date_posted.desc()).all()

def search_posts(db: Session, keyword: str) -> List[FacebookPost]:
    return db.query(FacebookPost).filter(
        FacebookPost.content.ilike(f"%{keyword}%")
    ).order_by(FacebookPost.date_posted.desc()).all()

def count_posts(db: Session) -> int:
    return db.query(FacebookPost).count()

def save_post(db: Session, post_data: dict) -> FacebookPost:
    date_posted = post_data.get("date_posted")
    if isinstance(date_posted, str):
        date_posted = datetime.fromisoformat(date_posted.replace("Z", "+00:00"))

    existing = db.query(FacebookPost).filter(FacebookPost.post_id == post_data["post_id"]).first()
    
    if existing:
        existing.user_username_raw = post_data.get("user_username_raw")
        existing.content = post_data.get("content")
        existing.post_type = post_data.get("post_type")
        existing.date_posted = date_posted
        db.commit()
        db.refresh(existing)
        return existing

    new_post = FacebookPost(
        post_id=post_data["post_id"],
        user_username_raw=post_data.get("user_username_raw"),
        content=post_data.get("content"),
        post_type=post_data.get("post_type"),
        date_posted=date_posted
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def delete_post(db: Session, post: FacebookPost) -> None:
    db.delete(post)
    db.commit()


@facebook_bp.route("/facebook/posts", methods=["POST"])
def create_facebook_post():
    db = SessionLocal()

    try:
        data = request.get_json(silent=True) or {}
        if "post_id" not in data:
            return jsonify({"error": "post_id is required"}), 400

        post = save_post(db, data)
        return jsonify({"status": "success", "data": post.to_dict()})
    finally:
        db.close()


@facebook_bp.route("/facebook/posts", methods=["GET"])
def list_facebook_posts():
    db = SessionLocal()
    limit = request.args.get("limit", 100, type=int)

    try:
        posts = get_all_posts(db, limit=limit)
        return jsonify({
            "status": "success",
            "count": len(posts),
            "data": [post.to_dict() for post in posts]
        })
    finally:
        db.close()


@facebook_bp.route("/facebook/posts/user/<username>", methods=["GET"])
def list_facebook_posts_by_user(username: str):
    db = SessionLocal()

    try:
        posts = get_posts_by_username(db, username)
        return jsonify({
            "status": "success",
            "user": username,
            "count": len(posts),
            "data": [post.to_dict() for post in posts]
        })
    finally:
        db.close()


@facebook_bp.route("/facebook/posts/<post_id>", methods=["GET"])
def get_facebook_post(post_id: str):
    db = SessionLocal()

    try:
        post = get_post_by_id(db, post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404

        return jsonify({"status": "success", "data": post.to_dict()})
    finally:
        db.close()


@facebook_bp.route("/facebook/posts/<post_id>", methods=["DELETE"])
def delete_facebook_post(post_id: str):
    db = SessionLocal()

    try:
        post = get_post_by_id(db, post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404

        delete_post(db, post)
        return jsonify({"status": "deleted", "post_id": post_id})
    finally:
        db.close()
