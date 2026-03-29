from sqlalchemy import Column, Integer, Text, DateTime
from db.session import Base

class InstagramPost(Base):
    __tablename__ = "instagram_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Text, unique=True, nullable=False, index=True)
    description = Column(Text)
    date_posted = Column(DateTime)
    content_type = Column(Text)
    user_posted = Column(Text, index=True)
    coauthor_producers = Column(Text)

    def __repr__(self):
        return f"<Post content_id='{self.content_id}' user='{self.user_posted}'>"
    
    def save(self, db):
        """Helper method to save the video"""
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.content_id,
            "caption": self.description,
            "taken_at": self.date_posted.strftime("%Y-%m-%d %H:%M:%S") if self.date_posted else None,
            "user_posted": self.user_posted,
            "coauthor_producers": self.coauthor_producers,
            "content_type": self.content_type
        }