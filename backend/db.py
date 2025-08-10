from sqlmodel import SQLModel, create_engine, Session
from config import settings

# Create engine
engine = create_engine(
    settings.database_url,
    echo=False,  # Set to True for SQL logging
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session
