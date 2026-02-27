from sqlalchemy import create_engine
import config

def get_engine():
    """Create and return a SQLAlchemy database engine."""
    return create_engine(config.DATABASE_URL, echo=False)