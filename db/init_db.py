# db/init_db.py

from db.session import engine, Base

# Explicitly import ALL models so SQLAlchemy registers them
from models.instagram import InstagramPost
from models.tiktok import TikTokVideo
from models.client import Client
from models.facebook import FacebookPost


def init_db():
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully!")
    
    # List all tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    print("\nCreated tables:")
    for table in inspector.get_table_names():
        print(f"  - {table}")

if __name__ == "__main__":
    init_db()