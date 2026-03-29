from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.exc import IntegrityError
from db.session import Base


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

    def save(self, db):
        """Save post and silently skip duplicates"""
        try:
            db.add(self)
            db.commit()
            db.refresh(self)
            return self
        except IntegrityError:
            db.rollback()
            return None  # duplicate skipped

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "post_id": self.post_id,
            "user_username_raw": self.user_username_raw,
            "content": self.content,
            "post_type": self.post_type,
            "date_posted": self.date_posted.strftime("%Y-%m-%d %H:%M:%S") if self.date_posted else None
        }