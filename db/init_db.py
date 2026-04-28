# db/init_db.py

from db.session import Base, engine

# Explicitly import all models so SQLAlchemy registers them.
from models.client import Client
from models.facebook import FacebookPost
from models.instagram import InstagramPost
from models.tiktok import TikTokVideo
from models.user import User


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

    from sqlalchemy import inspect

    inspector = inspect(engine)
    print("\nCreated tables:")
    for table in inspector.get_table_names():
        print(f"  - {table}")


if __name__ == "__main__":
    init_db()
