"""All-in-one database setup with models and initialization."""

from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime, timedelta
from typing import List, Optional


# ================= DATABASE CONFIGURATION =================

DATABASE_URL = "sqlite:///./instagram_clients.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ================= POST MODEL =================

class Post(Base):
    """Instagram posts model (table: instagram_posts)"""

    __tablename__ = "instagram_posts"
    
    # --- Columns (Strictly matching provided DB schema) ---
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Text, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    date_posted = Column(DateTime, nullable=True)
    content_type = Column(Text, nullable=True)
    user_posted = Column(Text, nullable=True, index=True)
    coauthor_producers = Column(Text, nullable=True)

    def __repr__(self) -> str:
        # Updated to use actual DB column attributes
        return f"<Post content_id='{self.content_id}' user_posted='{self.user_posted}'>"

    def to_dict(self) -> dict:
        # Maps DB columns to API-friendly keys for backward compatibility
        # Removed video_versions/carousel_media as they are not in the DB schema
        return {
            "id": self.id,
            "code": self.content_id,              # Map content_id -> code
            "caption": self.description,          # Map description -> caption
            "taken_at": self.date_posted.strftime("%Y-%m-%d %H:%M:%S") if self.date_posted else None, # Map date_posted -> taken_at
            "user_posted": self.user_posted,         # Map user_posted -> username
            "coauthor_producers": self.coauthor_producers,
            "content_type": self.content_type
        }

    # ================= QUERIES =================

    @classmethod
    def get_by_content_id(cls, db: Session, content_id: str) -> Optional['Post']:
        # Updated filter to use content_id
        return db.query(cls).filter(cls.content_id == content_id).first()

    @classmethod
    def get_all(cls, db: Session, limit: int = 100) -> List['Post']:
        # Updated order_by to use date_posted
        return db.query(cls).order_by(cls.date_posted.desc()).limit(limit).all()

    @classmethod
    def search_by_description(cls, db: Session, keyword: str) -> List['Post']:
        # Updated filter to use description
        return db.query(cls).filter(
            cls.description.ilike(f"%{keyword}%")
        ).order_by(cls.date_posted.desc()).all()

    @staticmethod
    def get_by_user_posted(db: Session, username: str):
        return (
            db.query(Post)
            .filter(Post.user_posted == username)
            .order_by(Post.date_posted.desc())
            .all()
        )

    @classmethod
    def get_by_date_range(cls, db: Session, start_date: datetime, end_date: datetime) -> List['Post']:
        # Updated filter to use date_posted
        return db.query(cls).filter(
            cls.date_posted >= start_date,
            cls.date_posted <= end_date
        ).order_by(cls.date_posted.desc()).all()

    @classmethod
    def get_by_user_posted_date_range(cls, db: Session, user_posted: str, start_date: datetime, end_date: datetime) -> List['Post']:
        # Updated filters to use user_posted and date_posted
        return db.query(cls).filter(
            cls.user_posted == user_posted,
            cls.date_posted >= start_date,
            cls.date_posted <= end_date
        ).order_by(cls.date_posted.desc()).all()
    
    @classmethod    
    def get_last_7_days_by_user_posted(cls, db: Session, user_posted: str) -> List['Post']:
        # FIXED: Use timezone-aware datetime and correct timedelta (7 days)
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        return db.query(cls).filter(
            cls.user_posted == user_posted,
            cls.date_posted >= seven_days_ago
        ).order_by(cls.date_posted.desc()).all()

    @classmethod
    def count(cls, db: Session) -> int:
        return db.query(cls).count()

    # ================= SAVE =================

    def save(self, db: Session) -> 'Post':
        # Convert string date to datetime object if needed
        if isinstance(self.date_posted, str):
            try:
                self.date_posted = datetime.strptime(self.date_posted, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                self.date_posted = None

        # Check for existing post based on unique 'content_id'
        existing = db.query(Post).filter(Post.content_id == self.content_id).first()

        if existing:
            # Update existing record using DB column names
            existing.description = self.description
            existing.date_posted = self.date_posted
            existing.user_posted = self.user_posted
            existing.content_type = self.content_type
            existing.coauthor_producers = self.coauthor_producers
            
            db.commit()
            db.refresh(existing)
            return existing

        # Add new record
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session) -> None:
        db.delete(self)
        db.commit()

# ================= TIKTOK VIDEO MODEL =================

class TikTokVideo(Base):
    """TikTok videos model (table: tiktok_videos)"""

    __tablename__ = "tiktok_videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Text, unique=True, nullable=False, index=True)
    author = Column(Text, nullable=True, index=True)
    description = Column(Text, nullable=True)
    create_time = Column(DateTime, nullable=True)
    post_type = Column(Text, nullable=True)

    def __repr__(self):
        return f"<TikTokVideo video_id='{self.video_id}' author='{self.author}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "video_id": self.video_id,
            "author": self.author,
            "description": self.description,
            "post_type": self.post_type,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None
        }

    # ================= QUERIES =================

    @classmethod
    def get_by_video_id(cls, db, video_id: str) -> Optional['TikTokVideo']:
        return db.query(cls).filter(cls.video_id == video_id).first()

    @classmethod
    def get_all(cls, db, limit: int = 100) -> List['TikTokVideo']:
        return db.query(cls).order_by(cls.create_time.desc()).limit(limit).all()

    @classmethod
    def get_by_author(cls, db, author: str) -> List['TikTokVideo']:
        return db.query(cls).filter(cls.author == author).order_by(cls.create_time.desc()).all()

    @classmethod
    def get_last_7_days_by_author(cls, db, author: str) -> List['TikTokVideo']:
        seven_days_ago = datetime.utcnow() - timedelta(days=8)
        return db.query(cls).filter(
            cls.author == author,
            cls.create_time >= seven_days_ago
        ).order_by(cls.create_time.desc()).all()

    @classmethod
    def count(cls, db) -> int:
        return db.query(cls).count()

    # ================= SAVE =================

    def save(self, db) -> 'TikTokVideo':
        # convert string to datetime if needed
        if isinstance(self.create_time, str):
            self.create_time = datetime.strptime(self.create_time, "%Y-%m-%d %H:%M:%S")

        existing = db.query(TikTokVideo).filter(TikTokVideo.video_id == self.video_id).first()

        if existing:
            existing.author = self.author
            existing.description = self.description
            existing.create_time = self.create_time
            existing.post_type = self.post_type
            db.commit()
            db.refresh(existing)
            return existing

        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db) -> None:
        db.delete(self)
        db.commit()




# ================= CLIENT MODEL =================

class Client(Base):
    """Clients model (table: clients)"""

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    instagram = Column(Text, nullable=True, unique=True, index=True)
    facebook = Column(Text, nullable=True)
    tiktok = Column(Text, nullable=True)
    contract = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Client name='{self.name}' instagram='{self.instagram}'>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "instagram": self.instagram,
            "facebook": self.facebook,
            "tiktok": self.tiktok,
            "contract": self.contract
        }

    def get_posts(self, db) -> List[Post]:
        if not self.instagram:
            return []

        username = self.instagram.lstrip('@')

        return Post.get_by_username(db, username)

    @classmethod
    def get_by_id(cls, db, client_id: int) -> Optional['Client']:
        return db.query(cls).filter(cls.id == client_id).first()

    @classmethod
    def get_by_instagram(cls, db, instagram_handle: str) -> Optional['Client']:
        handle = instagram_handle.lstrip('@')

        return db.query(cls).filter(cls.instagram == handle).first()

    @classmethod
    def get_all(cls, db) -> List['Client']:
        return db.query(cls).all()

    @classmethod
    def search_by_name(cls, db, keyword: str) -> List['Client']:
        return db.query(cls).filter(
            cls.name.ilike(f"%{keyword}%")
        ).all()

    @classmethod
    def count(cls, db) -> int:
        return db.query(cls).count()

    def save(self, db) -> 'Client':
        db.add(self)
        db.commit()
        db.refresh(self)

        return self

    def delete(self, db) -> None:
        db.delete(self)
        db.commit()





# ================= FACEBOOK POST MODEL =================

class FacebookPost(Base):
        """Facebook posts model (table: facebook_posts)"""

        __tablename__ = "facebook_posts"

        id = Column(Integer, primary_key=True, autoincrement=True)
        post_id = Column(Text, unique=True, nullable=False, index=True)
        user_username_raw = Column(Text, nullable=True, index=True)
        content = Column(Text, nullable=True)
        post_type = Column(Text, nullable=True)
        date_posted = Column(DateTime, nullable=True, index=True)

        def __repr__(self) -> str:
            return f"<FacebookPost post_id='{self.post_id}' user='{self.user_username_raw}'>"

        def to_dict(self) -> dict:
            return {
                "id": self.id,
                "post_id": self.post_id,
                "user_username_raw": self.user_username_raw,
                "content": self.content,
                "post_type": self.post_type,
                "date_posted": self.date_posted.strftime("%Y-%m-%d %H:%M:%S") if self.date_posted else None
            }

        # ================= QUERIES =================

        @classmethod
        def get_by_post_id(cls, db, post_id: str) -> Optional['FacebookPost']:
            return db.query(cls).filter(cls.post_id == post_id).first()

        @classmethod
        def get_all(cls, db, limit: int = 100) -> List['FacebookPost']:
            return db.query(cls).order_by(cls.date_posted.desc()).limit(limit).all()

        @classmethod
        def get_by_username(cls, db, username: str) -> List['FacebookPost']:
            return db.query(cls).filter(
                cls.user_username_raw == username
            ).order_by(cls.date_posted.desc()).all()

        @classmethod
        def get_last_7_days_by_username(cls, db, username: str) -> List['FacebookPost']:
            from datetime import timedelta
            seven_days_ago = datetime.utcnow() - timedelta(days=7)

            return db.query(cls).filter(
                cls.user_username_raw == username,
                cls.date_posted >= seven_days_ago
            ).order_by(cls.date_posted.desc()).all()

        @classmethod
        def search_by_content(cls, db, keyword: str) -> List['FacebookPost']:
            return db.query(cls).filter(
                cls.content.ilike(f"%{keyword}%")
            ).order_by(cls.date_posted.desc()).all()

        @classmethod
        def count(cls, db) -> int:
            return db.query(cls).count()

        # ================= SAVE =================

        def save(self, db) -> 'FacebookPost':
            # Convert ISO string → datetime
            if isinstance(self.date_posted, str):
                self.date_posted = datetime.fromisoformat(
                    self.date_posted.replace("Z", "+00:00")
                )

            existing = db.query(FacebookPost).filter(
                FacebookPost.post_id == self.post_id
            ).first()

            if existing:
                existing.user_username_raw = self.user_username_raw
                existing.content = self.content
                existing.post_type = self.post_type
                existing.date_posted = self.date_posted

                db.commit()
                db.refresh(existing)
                return existing

            db.add(self)
            db.commit()
            db.refresh(self)
            return self

        def delete(self, db) -> None:
            db.delete(self)
            db.commit()

# ================= DATABASE INITIALIZATION =================

def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()