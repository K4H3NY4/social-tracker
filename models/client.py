from sqlalchemy import Column, Integer, Text, DateTime
from db.session import Base

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