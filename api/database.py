from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.config import get_settings
# Import models to ensure they are registered with SQLAlchemy
from api.models import user, group, virtual_card, card_member, uploaded_file

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()