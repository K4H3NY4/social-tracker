from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ Create engine
engine = create_engine('sqlite:///instagram_clients.db', echo=False)

# ✅ Create Base
Base = declarative_base()

# ✅ Create session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# ✅ Helper to initialize tables (call once)
def init_db():
    Base.metadata.create_all(bind=engine)