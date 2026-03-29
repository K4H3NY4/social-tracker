from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime
from google import genai
import os
import json
from dotenv import load_dotenv

from db.session import SessionLocal
from models.facebook import FacebookPost
from models.instagram import InstagramPost
from models.tiktok import TikTokVideo
from models.client import Client

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ✅ Enable CORS (optional, for separate frontend)

CORS(app)

# ✅ Initialize Google GenAI Client
api_key = os.environ.get("API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


# ═══════════════════════════════════════════════════════
# ✅ DASHBOARD ROUTE
# ═══════════════════════════════════════════════════════

@app.route('/')
def dashboard():
    """Serve the dashboard HTML file"""
    return send_from_directory('templates', 'index.html')


# ═══════════════════════════════════════════════════════
# ✅ HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════

# ✅ Helper: Count Facebook posts vs videos
def count_facebook_content(posts: list) -> dict:
    post_count = 0
    video_count = 0
    
    for post in posts:
        raw_type = post.get('post_type', '').strip().lower()
        
        if raw_type in ['reel', 'reels', 'video', 'videos', 'vid', 'vids',
                        'animation', 'animations', 'animated', 'anim', 'anims']:
            video_count += 1
        else:
            post_count += 1
    
    return {
        'posts': post_count,
        'videos': video_count,
        'total': post_count + video_count
    }


# ✅ Helper: Count Instagram content types (carousel, image, video)
def count_instagram_content_types(posts: list) -> dict:
    """
    Count Instagram posts by content_type field
    - Carousel
    - Image  
    - Video (includes Reel, Video, Animation)
    """
    carousel_count = 0
    image_count = 0
    video_count = 0
    
    for post in posts:
        content_type = post.get('content_type', '').strip().lower()
        
        if content_type in ['carousel', 'carousels', 'album']:
            carousel_count += 1
        elif content_type in ['image', 'images', 'photo', 'photos', 'picture']:
            image_count += 1
        elif content_type in ['video', 'videos', 'reel', 'reels', 'vid', 'vids',
                              'animation', 'animations', 'animated', 'anim', 'anims']:
            video_count += 1
        else:
            image_count += 1  # Default to image if unknown
    
    return {
        'carousel': carousel_count,
        'image': image_count,
        'video': video_count,
        'total': carousel_count + image_count + video_count
    }



# ✅ Helper: Count TikTok content (mostly videos, some images)
def count_tiktok_content(posts: list) -> dict:
    video_count = 0
    image_count = 0
    
    for post in posts:
        raw_type = post.get('post_type', '').strip().lower()
        
        if raw_type in ['video', 'videos', 'vid', 'vids']:
            video_count += 1
        elif raw_type in ['image', 'images', 'photo', 'photos', 'picture']:
            image_count += 1
        else:
            video_count += 1
    
    return {
        'videos': video_count,
        'images': image_count,
        'total': video_count + image_count
    }


# ✅ Helper: Count collaborative posts (Instagram only)
def count_collaborative_posts(posts: list, username: str = None) -> dict:
    """
    Count posts with co-authors/producers
    If username is provided, count posts where username appears in coauthor_producers
    """
    collaborative_count = 0
    solo_count = 0
    
    for post in posts:
        coauthors = post.get('coauthor_producers', '')
        user_posted = post.get('user_posted', '')
        
        # Check if this is a collaboration
        is_collab = False
        
        if username:
            # Check if username is in coauthor_producers
            if coauthors and username in coauthors:
                is_collab = True
            # Or if user_posted != username but they're listed as co-author
            elif user_posted != username and coauthors and username in coauthors:
                is_collab = True
        else:
            # Generic check - just see if there are coauthors
            if coauthors and coauthors.strip():
                is_collab = True
        
        if is_collab:
            collaborative_count += 1
        else:
            solo_count += 1
    
    total = collaborative_count + solo_count
    
    return {
        'collaborative': collaborative_count,
        'solo': solo_count,
        'total': total,
        'collaboration_rate': round((collaborative_count / total * 100), 2) if total > 0 else 0
    }




# ✅ Helper: Analyze contract compliance
def analyze_contract_compliance(contract: str, posts: list, username: str, date_range: dict, 
                                 platform: str, content_stats: dict, collaboration_stats: dict = None) -> dict:
    start_date = date_range.get('start', 'N/A')
    end_date = date_range.get('end', 'N/A')
    
    if not client or not contract:
        return {
            'compliance_status': 'unknown',
            'compliance_score': 0,
            'analysis': 'AI not configured or no contract found',
            'deliverables_met': [],
            'deliverables_missing': [],
            'recommendations': []
        }
    
    try:
        # Build platform-specific summary
        if platform == 'instagram':
            posts_summary = f"""
            Platform: INSTAGRAM
            Client: {username}
            Date Range: {start_date} to {end_date}
            Total Posts: {len(posts)}
            
            Content Type Breakdown:
            - Carousel Posts: {content_stats.get('carousel', 0)}
            - Image Posts: {content_stats.get('image', 0)}
            - Video Posts (Reels+Videos+Animations): {content_stats.get('video', 0)}
            
            Collaboration Stats:
            - Collaborative Posts: {collaboration_stats.get('collaborative', 0)}
            - Solo Posts: {collaboration_stats.get('solo', 0)}
            - Collaboration Rate: {collaboration_stats.get('collaboration_rate', 0)}%
            """
        elif platform == 'tiktok':
            posts_summary = f"""
            Platform: TIKTOK
            Client: {username}
            Date Range: {start_date} to {end_date}
            Total Videos: {len(posts)}
            
            Content Breakdown:
            - Videos: {content_stats.get('videos', 0)}
            - Images: {content_stats.get('images', 0)}
            """
        else:  # Facebook
            posts_summary = f"""
            Platform: FACEBOOK
            Client: {username}
            Date Range: {start_date} to {end_date}
            Total Posts: {len(posts)}
            
            Content Breakdown:
            - Static Posts: {content_stats.get('posts', 0)}
            - Videos (Reels+Videos+Animations): {content_stats.get('videos', 0)}
            """
        
        if posts:
            posts_summary += "\n\nSample Content:\n"
            for i, post in enumerate(posts[:3]):
                content = post.get('description') or post.get('content', '')[:150]
                if platform == 'instagram':
                    ctype = post.get('content_type', 'Unknown')
                    coauthors = post.get('coauthor_producers', '')
                    collab_note = f" [COLLAB with {coauthors}]" if coauthors else ""
                    posts_summary += f"\n{i+1}. [{ctype}] {content}...{collab_note}"
                elif platform == 'tiktok':
                    ptype = post.get('post_type', 'Unknown')
                    posts_summary += f"\n{i+1}. [{ptype}] {content}..."
                else:
                    ptype = post.get('post_type', 'Unknown')
                    posts_summary += f"\n{i+1}. [{ptype}] {content}..."
        
        # Platform-specific prompt
        if platform == 'instagram':
            content_json = f"""
            "content_breakdown": {{
                "carousel": {content_stats.get('carousel', 0)},
                "image": {content_stats.get('image', 0)},
                "video": {content_stats.get('video', 0)},
                "status": "complete" or "incomplete"
            }},
            "collaborations": {{
                "collaborative_posts": {collaboration_stats.get('collaborative', 0)},
                "solo_posts": {collaboration_stats.get('solo', 0)},
                "collaboration_rate": "{collaboration_stats.get('collaboration_rate', 0)}%",
                "status": "strong" or "moderate" or "weak"
            }},
            """
        elif platform == 'tiktok':
            content_json = f"""
            "content_breakdown": {{
                "videos": {content_stats.get('videos', 0)},
                "images": {content_stats.get('images', 0)},
                "status": "complete" or "incomplete"
            }},
            """
        else:  # Facebook
            content_json = f"""
            "content_breakdown": {{
                "posts": {content_stats.get('posts', 0)},
                "videos": {content_stats.get('videos', 0)},
                "status": "complete" or "incomplete"
            }},
            """
        
        prompt = f"""
        You are a contract compliance analyst. Focus ONLY on {platform.upper()}.
        
        CONTRACT REQUIREMENTS:
        {contract}
        
        DELIVERED CONTENT:
        {posts_summary}
        
        Note: Video includes Reels, Videos, and Animations (all combined).
        
        Return ONLY valid JSON:
        {{
            "compliance_status": "fully_compliant" or "partially_compliant" or "non_compliant",
            "compliance_score": 0 to 100,
            "analysis": "detailed analysis referencing date range {start_date} to {end_date}",
            "deliverables_met": ["deliverable 1", "deliverable 2"],
            "deliverables_missing": ["missing 1", "missing 2"],
            "post_frequency": {{
                "required": "contract requirement",
                "delivered": "{len(posts)} posts from {start_date} to {end_date}",
                "status": "met" or "not_met"
            }},
            "content_quality": {{
                "assessment": "assessment",
                "score": 0 to 100
            }},
            {content_json}
            "recommendations": ["recommendation 1", "recommendation 2"]
        }}
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        response_text = response.text.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        response_text = response_text.strip()
        
        return json.loads(response_text)
        
    except Exception as e:
        return {
            'compliance_status': 'error',
            'compliance_score': 0,
            'analysis': f'Error: {str(e)}',
            'deliverables_met': [],
            'deliverables_missing': [],
            'recommendations': []
        }


# ═══════════════════════════════════════════════════════
# ✅ FACEBOOK ENDPOINT
# ═══════════════════════════════════════════════════════

@app.route('/api/facebook/<username>/contract-compliance', methods=['GET'])
def check_facebook_contract_compliance(username):
    db: Session = SessionLocal()
    
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        client_record = db.execute(
            select(Client).where(Client.facebook == username)
        ).scalars().first()
        
        if not client_record:
            return jsonify({'error': 'Client not found'}), 404
        
        if not client_record.contract:
            return jsonify({'error': 'No contract found'}), 404
        
        stmt = select(FacebookPost).where(FacebookPost.user_username_raw == username)
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            stmt = stmt.where(FacebookPost.date_posted >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end.replace(hour=23, minute=59, second=59)
            stmt = stmt.where(FacebookPost.date_posted <= end)
        
        stmt = stmt.order_by(FacebookPost.date_posted.desc())
        posts = db.execute(stmt).scalars().all()
        
        posts_data = [post.to_dict() for post in posts]
        date_range = {'start': start_date, 'end': end_date}
        content_stats = count_facebook_content(posts_data)
        
        compliance_analysis = analyze_contract_compliance(
            contract=client_record.contract,
            posts=posts_data,
            username=username,
            date_range=date_range,
            platform='facebook',
            content_stats=content_stats
        )
        
        return jsonify({
            'platform': 'facebook',
            'username': username,
            'client_name': client_record.name,
            'date_range': date_range,
            'total_posts_delivered': len(posts),
            'content_breakdown': {
                'posts': content_stats['posts'],
                'videos': content_stats['videos'],
                'total': content_stats['total'],
                'note': 'Videos include: Reels, Videos, and Animations'
            },
            'contract_preview': client_record.contract[:200] + '...' if len(client_record.contract) > 200 else client_record.contract,
            'compliance_analysis': compliance_analysis
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.close()


# ═══════════════════════════════════════════════════════
# ✅ INSTAGRAM ENDPOINT
# ═══════════════════════════════════════════════════════

@app.route('/api/instagram/<username>/contract-compliance', methods=['GET'])
def check_instagram_contract_compliance(username):
    """
    Analyze Instagram contract compliance
    Example: GET /api/instagram/basco_paints/contract-compliance?start=2026-03-01&end=2026-03-31
    """
    db: Session = SessionLocal()
    
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        # Get client by Instagram handle
        client_record = db.execute(
            select(Client).where(Client.instagram == username)
        ).scalars().first()
        
        if not client_record:
            return jsonify({'error': 'Client not found'}), 404
        
        if not client_record.contract:
            return jsonify({'error': 'No contract found'}), 404
        
        # Get Instagram posts where client is EITHER user_posted OR coauthor_producers
        stmt = select(InstagramPost).where(
            (InstagramPost.user_posted == username) |
            (InstagramPost.coauthor_producers.like(f'%{username}%'))
        )
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            stmt = stmt.where(InstagramPost.date_posted >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end.replace(hour=23, minute=59, second=59)
            stmt = stmt.where(InstagramPost.date_posted <= end)
        
        stmt = stmt.order_by(InstagramPost.date_posted.desc())
        posts = db.execute(stmt).scalars().all()
        
        # Convert to dict and mark if it's a collaboration
        posts_data = []
        for post in posts:
            post_dict = {
                'id': post.id,
                'content_id': post.content_id,
                'description': post.description,
                'date_posted': post.date_posted.isoformat() if post.date_posted else None,
                'content_type': post.content_type,
                'user_posted': post.user_posted,
                'coauthor_producers': post.coauthor_producers,
                # Mark if this is a collaboration post
                'is_collaboration': (
                    post.user_posted != username and 
                    post.coauthor_producers and 
                    username in post.coauthor_producers
                )
            }
            posts_data.append(post_dict)
        
        date_range = {'start': start_date, 'end': end_date}
        
        # Count Instagram content types
        content_stats = count_instagram_content_types(posts_data)
        
        # Count collaborations - posts where client is co-author
        collaboration_stats = count_collaborative_posts(posts_data, username)
        
        compliance_analysis = analyze_contract_compliance(
            contract=client_record.contract,
            posts=posts_data,
            username=username,
            date_range=date_range,
            platform='instagram',
            content_stats=content_stats,
            collaboration_stats=collaboration_stats
        )
        
        return jsonify({
            'platform': 'instagram',
            'username': username,
            'client_name': client_record.name,
            'date_range': date_range,
            'total_posts_delivered': len(posts),
            'content_types': {
                'carousel': content_stats['carousel'],
                'image': content_stats['image'],
                'video': content_stats['video'],
                'total': content_stats['total'],
                'note': 'Video includes: Reels, Videos, and Animations'
            },
            'collaboration_stats': {
                'collaborative_posts': collaboration_stats['collaborative'],
                'solo_posts': collaboration_stats['solo'],
                'total': collaboration_stats['total'],
                'collaboration_rate': f"{collaboration_stats['collaboration_rate']}%",
                'note': 'Includes posts where client is co-author'
            },
            'contract_preview': client_record.contract[:200] + '...' if len(client_record.contract) > 200 else client_record.contract,
            'compliance_analysis': compliance_analysis
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.close()




# ═══════════════════════════════════════════════════════
# ✅ TIKTOK ENDPOINT
# ═══════════════════════════════════════════════════════

@app.route('/api/tiktok/<username>/contract-compliance', methods=['GET'])
def check_tiktok_contract_compliance(username):
    db: Session = SessionLocal()
    
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        client_record = db.execute(
            select(Client).where(Client.tiktok == username)
        ).scalars().first()
        
        if not client_record:
            return jsonify({'error': 'Client not found'}), 404
        
        if not client_record.contract:
            return jsonify({'error': 'No contract found'}), 404
        
        stmt = select(TikTokVideo).where(TikTokVideo.author == username)
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            stmt = stmt.where(TikTokVideo.create_time >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end.replace(hour=23, minute=59, second=59)
            stmt = stmt.where(TikTokVideo.create_time <= end)
        
        stmt = stmt.order_by(TikTokVideo.create_time.desc())
        videos = db.execute(stmt).scalars().all()
        
        videos_data = [video.to_dict() for video in videos]
        date_range = {'start': start_date, 'end': end_date}
        content_stats = count_tiktok_content(videos_data)
        
        compliance_analysis = analyze_contract_compliance(
            contract=client_record.contract,
            posts=videos_data,
            username=username,
            date_range=date_range,
            platform='tiktok',
            content_stats=content_stats
        )
        
        return jsonify({
            'platform': 'tiktok',
            'username': username,
            'client_name': client_record.name,
            'date_range': date_range,
            'total_videos_delivered': len(videos),
            'content_breakdown': {
                'videos': content_stats['videos'],
                'images': content_stats['images'],
                'total': content_stats['total'],
                'note': 'TikTok is primarily video content'
            },
            'contract_preview': client_record.contract[:200] + '...' if len(client_record.contract) > 200 else client_record.contract,
            'compliance_analysis': compliance_analysis
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.close()



# ═══════════════════════════════════════════════════════
# ✅ CLIENT CRUD ENDPOINTS
# ═══════════════════════════════════════════════════════

@app.route('/api/clients', methods=['GET'])
def get_all_clients():
    """Get all clients for dropdown selection"""
    db: Session = SessionLocal()
    
    try:
        clients = db.execute(select(Client)).scalars().all()
        
        clients_data = [{
            'id': client.id,
            'name': client.name,
            'facebook': client.facebook,
            'instagram': client.instagram,
            'tiktok': client.tiktok,
            'contract': client.contract[:100] + '...' if client.contract and len(client.contract) > 100 else client.contract
        } for client in clients]
        
        return jsonify({
            'total': len(clients_data),
            'clients': clients_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.close()


@app.route('/api/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """Get a single client by ID"""
    db: Session = SessionLocal()
    
    try:
        client = db.execute(
            select(Client).where(Client.id == client_id)
        ).scalars().first()
        
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        return jsonify({
            'id': client.id,
            'name': client.name,
            'facebook': client.facebook,
            'instagram': client.instagram,
            'tiktok': client.tiktok,
            'contract': client.contract
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.close()


@app.route('/api/clients', methods=['POST'])
def create_client():
    """
    Create a new client
    
    Request Body:
    {
        "name": "Client Name",
        "facebook": "facebook_handle",
        "instagram": "instagram_handle",
        "tiktok": "tiktok_handle",
        "contract": "Contract text..."
    }
    """
    db: Session = SessionLocal()
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('name'):
            return jsonify({'error': 'Client name is required'}), 400
        
        # Check if client with same name already exists
        existing = db.execute(
            select(Client).where(Client.name == data.get('name'))
        ).scalars().first()
        
        if existing:
            return jsonify({'error': 'Client with this name already exists'}), 409
        
        # Create new client
        new_client = Client(
            name=data.get('name', '').strip(),
            facebook=data.get('facebook', '').strip() if data.get('facebook') else None,
            instagram=data.get('instagram', '').strip() if data.get('instagram') else None,
            tiktok=data.get('tiktok', '').strip() if data.get('tiktok') else None,
            contract=data.get('contract', '')
        )
        
        db.add(new_client)
        db.commit()
        db.refresh(new_client)
        
        return jsonify({
            'message': 'Client created successfully',
            'client': {
                'id': new_client.id,
                'name': new_client.name,
                'facebook': new_client.facebook,
                'instagram': new_client.instagram,
                'tiktok': new_client.tiktok
            }
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.close()


@app.route('/api/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    """
    Update an existing client
    
    Request Body (all fields optional):
    {
        "name": "Updated Client Name",
        "facebook": "updated_facebook_handle",
        "instagram": "updated_instagram_handle",
        "tiktok": "updated_tiktok_handle",
        "contract": "Updated contract text..."
    }
    """
    db: Session = SessionLocal()
    
    try:
        client = db.execute(
            select(Client).where(Client.id == client_id)
        ).scalars().first()
        
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if new name conflicts with existing client
        if data.get('name') and data.get('name') != client.name:
            existing = db.execute(
                select(Client).where(
                    Client.name == data.get('name'),
                    Client.id != client_id
                )
            ).scalars().first()
            
            if existing:
                return jsonify({'error': 'Another client with this name already exists'}), 409
        
        # Update fields (only if provided)
        if data.get('name'):
            client.name = data.get('name').strip()
        
        if data.get('facebook') is not None:
            client.facebook = data.get('facebook').strip() if data.get('facebook') else None
        
        if data.get('instagram') is not None:
            client.instagram = data.get('instagram').strip() if data.get('instagram') else None
        
        if data.get('tiktok') is not None:
            client.tiktok = data.get('tiktok').strip() if data.get('tiktok') else None
        
        if data.get('contract') is not None:
            client.contract = data.get('contract')
        
        db.commit()
        db.refresh(client)
        
        return jsonify({
            'message': 'Client updated successfully',
            'client': {
                'id': client.id,
                'name': client.name,
                'facebook': client.facebook,
                'instagram': client.instagram,
                'tiktok': client.tiktok
            }
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.close()


@app.route('/api/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Delete a client"""
    db: Session = SessionLocal()
    
    try:
        client = db.execute(
            select(Client).where(Client.id == client_id)
        ).scalars().first()
        
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        db.delete(client)
        db.commit()
        
        return jsonify({
            'message': 'Client deleted successfully',
            'deleted_client_id': client_id
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.close()


@app.route('/api/clients/search', methods=['GET'])
def search_clients():
    """
    Search clients by name or social handle
    
    Query Params:
    - q: search query
    """
    db: Session = SessionLocal()
    
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Search across name and social handles
        clients = db.execute(
            select(Client).where(
                (Client.name.ilike(f'%{query}%')) |
                (Client.facebook.ilike(f'%{query}%')) |
                (Client.instagram.ilike(f'%{query}%')) |
                (Client.tiktok.ilike(f'%{query}%'))
            )
        ).scalars().all()
        
        clients_data = [{
            'id': client.id,
            'name': client.name,
            'facebook': client.facebook,
            'instagram': client.instagram,
            'tiktok': client.tiktok
        } for client in clients]
        
        return jsonify({
            'query': query,
            'total': len(clients_data),
            'clients': clients_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.close()

# ═══════════════════════════════════════════════════════
# ✅ HEALTH CHECK
# ═══════════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        db = SessionLocal()
        db.execute(select(FacebookPost).limit(1))
        db.execute(select(InstagramPost).limit(1))
        db.execute(select(TikTokVideo).limit(1))
        db.execute(select(Client).limit(1))
        db.close()
        
        return jsonify({
            'status': 'ok',
            'database': 'connected',
            'platforms': ['facebook', 'instagram', 'tiktok'],
            'ai_configured': client is not None
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)