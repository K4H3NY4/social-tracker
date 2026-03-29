# controllers/client_controller.py
from typing import List, Optional
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session

from db.session import SessionLocal
from models.client import Client
from controllers.instagram_controller import get_posts_by_user

client_bp = Blueprint("clients", __name__)

def get_client_by_id(db: Session, client_id: int) -> Optional[Client]:
    return db.query(Client).filter(Client.id == client_id).first()

def get_client_by_instagram(db: Session, handle: str) -> Optional[Client]:
    handle = handle.lstrip('@')
    return db.query(Client).filter(Client.instagram == handle).first()

def get_all_clients(db: Session) -> List[Client]:
    return db.query(Client).all()

def search_clients(db: Session, keyword: str) -> List[Client]:
    return db.query(Client).filter(Client.name.ilike(f"%{keyword}%")).all()

def count_clients(db: Session) -> int:
    return db.query(Client).count()

def save_client(db: Session, client_data: dict) -> Client:
    # Normalize instagram handle
    if client_data.get("instagram"):
        client_data["instagram"] = client_data["instagram"].lstrip('@')
    
    existing = None
    if client_data.get("instagram"):
        existing = db.query(Client).filter(Client.instagram == client_data["instagram"]).first()
    
    if existing:
        existing.name = client_data.get("name", existing.name)
        existing.facebook = client_data.get("facebook", existing.facebook)
        existing.tiktok = client_data.get("tiktok", existing.tiktok)
        existing.contract = client_data.get("contract", existing.contract)
        db.commit()
        db.refresh(existing)
        return existing

    new_client = Client(**client_data)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client

def delete_client(db: Session, client: Client) -> None:
    db.delete(client)
    db.commit()

def get_client_posts(db: Session, client: Client) -> List:
    """Get all Instagram posts for a client by their handle"""
    if not client.instagram:
        return []
    username = client.instagram.lstrip('@')
    return get_posts_by_user(db, username)


@client_bp.route("/clients", methods=["GET"])
def list_clients():
    db = SessionLocal()

    try:
        clients = get_all_clients(db)
        return jsonify([client.to_dict() for client in clients])
    finally:
        db.close()


@client_bp.route("/clients/<int:client_id>", methods=["GET"])
def get_client(client_id: int):
    db = SessionLocal()

    try:
        client = get_client_by_id(db, client_id)
        if not client:
            return jsonify({"error": "Client not found"}), 404

        result = client.to_dict()
        result["posts"] = [post.to_dict() for post in get_client_posts(db, client)]
        return jsonify(result)
    finally:
        db.close()


@client_bp.route("/clients", methods=["POST"])
def create_client():
    db = SessionLocal()

    try:
        data = request.get_json(silent=True) or {}
        if "name" not in data:
            return jsonify({"error": "name is required"}), 400

        client = save_client(db, data)
        return jsonify(client.to_dict())
    finally:
        db.close()


@client_bp.route("/clients/search", methods=["GET"])
def search_clients_route():
    db = SessionLocal()
    keyword = request.args.get("q")

    if not keyword:
        return jsonify({"error": "q query parameter required"}), 400

    try:
        clients = search_clients(db, keyword)
        return jsonify([client.to_dict() for client in clients])
    finally:
        db.close()


@client_bp.route("/clients/<int:client_id>", methods=["PUT"])
def update_client(client_id: int):
    db = SessionLocal()

    try:
        client = get_client_by_id(db, client_id)
        if not client:
            return jsonify({"error": "Client not found"}), 404

        data = request.get_json(silent=True) or {}
        client.name = data.get("name", client.name)
        instagram = data.get("instagram", client.instagram)
        client.instagram = instagram.lstrip("@") if instagram else None
        client.facebook = data.get("facebook", client.facebook)
        client.tiktok = data.get("tiktok", client.tiktok)
        client.contract = data.get("contract", client.contract)

        db.commit()
        db.refresh(client)

        return jsonify({
            "message": "Client updated successfully",
            "client": client.to_dict()
        })
    finally:
        db.close()


@client_bp.route("/clients/<int:client_id>", methods=["DELETE"])
def remove_client(client_id: int):
    db = SessionLocal()

    try:
        client = get_client_by_id(db, client_id)
        if not client:
            return jsonify({"error": "Client not found"}), 404

        delete_client(db, client)
        return jsonify({"message": "Client deleted"})
    finally:
        db.close()
