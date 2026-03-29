from sqlalchemy import Column, Integer, Text, DateTime
from db.session import Base

from sqlalchemy import Column, Integer, Text, DateTime
from db.session import Base

class TikTokVideo(Base):
    __tablename__ = "tiktok_videos"  # ✅ Fixed underscores

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Text, unique=True, nullable=False, index=True)
    author = Column(Text, index=True)
    description = Column(Text)
    create_time = Column(DateTime)
    post_type = Column(Text)

    def __repr__(self):
        return f"<TikTokVideo video_id='{self.video_id}' author='{self.author}'>"
    
    def save(self, db):
        """Helper method to save the video"""
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "video_id": self.video_id,
            "author": self.author,
            "description": self.description,
            "post_type": self.post_type,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None
        }