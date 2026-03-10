"""All-in-one database setup with models and initialization."""

from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
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

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(Text, unique=True, nullable=False, index=True)
    caption = Column(Text, nullable=True)
    video_versions = Column(Text, nullable=True) 
    carousel_media = Column(Text, nullable=True)  

    # FIXED: real datetime
    taken_at = Column(DateTime, nullable=True)

    username = Column(Text, nullable=True, index=True)

    def __repr__(self) -> str:
        return f"<Post code='{self.code}' username='{self.username}'>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "caption": self.caption,
            "video_versions": self.video_versions,
            "carousel_media": self.carousel_media,
            "taken_at": self.taken_at.strftime("%Y-%m-%d %H:%M:%S") if self.taken_at else None,
            "username": self.username
        }

    # ================= QUERIES =================

    @classmethod
    def get_by_code(cls, db, code: str) -> Optional['Post']:
        return db.query(cls).filter(cls.code == code).first()

    @classmethod
    def get_all(cls, db, limit: int = 100) -> List['Post']:
        return db.query(cls).order_by(cls.taken_at.desc()).limit(limit).all()

    @classmethod
    def search_by_caption(cls, db, keyword: str) -> List['Post']:
        return db.query(cls).filter(
            cls.caption.ilike(f"%{keyword}%")
        ).order_by(cls.taken_at.desc()).all()

    @classmethod
    def get_by_username(cls, db, username: str) -> List['Post']:
        return db.query(cls).filter(cls.username == username)\
            .order_by(cls.taken_at.desc()).all()

    @classmethod
    def get_by_date_range(cls, db, start_date: datetime, end_date: datetime) -> List['Post']:
        return db.query(cls).filter(
            cls.taken_at >= start_date,
            cls.taken_at <= end_date
        ).order_by(cls.taken_at.desc()).all()

    @classmethod
    def get_by_username_date_range(cls, db, username: str, start_date: datetime, end_date: datetime) -> List['Post']:
        return db.query(cls).filter(
            cls.username == username,
            cls.taken_at >= start_date,
            cls.taken_at <= end_date
        ).order_by(cls.taken_at.desc()).all()
    

    @classmethod
    def get_last_7_days_by_username(cls, db, username: str):
        seven_days_ago = datetime.utcnow() - timedelta(days=8)

        return db.query(cls).filter(
        cls.username == username,
        cls.taken_at >= seven_days_ago
    ).order_by(cls.taken_at.desc()).all()

    @classmethod
    def count(cls, db) -> int:
        return db.query(cls).count()

    # ================= SAVE =================

    def save(self, db) -> 'Post':

        # convert string date if needed
        if isinstance(self.taken_at, str):
            self.taken_at = datetime.strptime(self.taken_at, "%Y-%m-%d %H:%M:%S")

        existing = db.query(Post).filter(Post.code == self.code).first()

        if existing:
            existing.caption = self.caption
            existing.taken_at = self.taken_at
            existing.username = self.username

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


# ================= TIKTOK VIDEO MODEL =================

class TikTokVideo(Base):
    """TikTok videos model (table: tiktok_videos)"""

    __tablename__ = "tiktok_videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Text, unique=True, nullable=False, index=True)
    author = Column(Text, nullable=True, index=True)
    description = Column(Text, nullable=True)
    create_time = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<TikTokVideo video_id='{self.video_id}' author='{self.author}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "video_id": self.video_id,
            "author": self.author,
            "description": self.description,
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