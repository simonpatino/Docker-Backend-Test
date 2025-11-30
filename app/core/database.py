from sqlmodel import create_engine, SQLModel
from app.core.config import settings

# Create the database engine
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def create_db_and_tables() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)
