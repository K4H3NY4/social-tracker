from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ================= CONFIGURATION =================
DB_FILE = "instagram_clients.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"
# =================================================

# Create engine
engine = create_engine(
    DATABASE_URL, 
    echo=False,  # Set to True to see SQL queries
    connect_args={"check_same_thread": False}  # Required for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()