# controllers/tiktok_controller.py
from datetime import datetime, timedelta
from typing import List, Optional
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session

from db.session import SessionLocal
from models.tiktok import TikTokVideo

tiktok_bp = Blueprint("tiktok", __name__)

def get_video_by_id(db: Session, video_id: str) -> Optional[TikTokVideo]:
    return db.query(TikTokVideo).filter(TikTokVideo.video_id == video_id).first()

def get_all_videos(db: Session, limit: int = 100) -> List[TikTokVideo]:
    return db.query(TikTokVideo).order_by(TikTokVideo.create_time.desc()).limit(limit).all()

def get_videos_by_author(db: Session, author: str) -> List[TikTokVideo]:
    return db.query(TikTokVideo).filter(TikTokVideo.author == author).order_by(TikTokVideo.create_time.desc()).all()

def get_videos_last_7_days(db: Session, author: str) -> List[TikTokVideo]:
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    return db.query(TikTokVideo).filter(
        TikTokVideo.author == author,
        TikTokVideo.create_time >= seven_days_ago
    ).order_by(TikTokVideo.create_time.desc()).all()

def count_videos(db: Session) -> int:
    return db.query(TikTokVideo).count()

def save_video(db: Session, video_data: dict) -> TikTokVideo:
    create_time = video_data.get("create_time")
    if isinstance(create_time, str):
        create_time = datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")

    existing = db.query(TikTokVideo).filter(TikTokVideo.video_id == video_data["video_id"]).first()
    
    if existing:
        existing.author = video_data.get("author")
        existing.description = video_data.get("description")
        existing.create_time = create_time
        existing.post_type = video_data.get("post_type")
        db.commit()
        db.refresh(existing)
        return existing

    new_video = TikTokVideo(
        video_id=video_data["video_id"],
        author=video_data.get("author"),
        description=video_data.get("description"),
        create_time=create_time,
        post_type=video_data.get("post_type")
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    return new_video

def delete_video(db: Session, video: TikTokVideo) -> None:
    db.delete(video)
    db.commit()


@tiktok_bp.route("/tiktok", methods=["GET"])
def list_videos():
    db = SessionLocal()
    limit = request.args.get("limit", 100, type=int)

    try:
        videos = get_all_videos(db, limit=limit)
        return jsonify([video.to_dict() for video in videos])
    finally:
        db.close()


@tiktok_bp.route("/tiktok/<video_id>", methods=["GET"])
def get_video(video_id: str):
    db = SessionLocal()

    try:
        video = get_video_by_id(db, video_id)
        if not video:
            return jsonify({"error": "Video not found"}), 404
        return jsonify(video.to_dict())
    finally:
        db.close()


@tiktok_bp.route("/tiktok/author/<author>", methods=["GET"])
def list_videos_by_author(author: str):
    db = SessionLocal()

    try:
        videos = get_videos_by_author(db, author)
        return jsonify([video.to_dict() for video in videos])
    finally:
        db.close()


@tiktok_bp.route("/tiktok/author/<author>/last7days", methods=["GET"])
def list_recent_videos_by_author(author: str):
    db = SessionLocal()

    try:
        videos = get_videos_last_7_days(db, author)
        videos_list = [video.to_dict() for video in videos]
        return jsonify({"count": len(videos_list), "videos": videos_list})
    finally:
        db.close()


@tiktok_bp.route("/tiktok", methods=["POST"])
def create_video():
    db = SessionLocal()

    try:
        data = request.get_json(silent=True) or {}
        required_fields = ["video_id", "author"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"{', '.join(required_fields)} required"}), 400

        video = save_video(db, data)
        return jsonify(video.to_dict())
    finally:
        db.close()


@tiktok_bp.route("/tiktok/<video_id>", methods=["DELETE"])
def delete_video_route(video_id: str):
    db = SessionLocal()

    try:
        video = get_video_by_id(db, video_id)
        if not video:
            return jsonify({"error": "Video not found"}), 404

        delete_video(db, video)
        return jsonify({"message": "Video deleted"})
    finally:
        db.close()
