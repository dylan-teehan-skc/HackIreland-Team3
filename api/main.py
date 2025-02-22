from fastapi import FastAPI
import api.database as database 
from .models.base import Base
from .config import get_settings, setup_logging
from .routes import file_router, card_router, subscription_router, auth_router

# Initialize settings and logging
settings = get_settings()
setup_logging()

# Create database tables
Base.metadata.create_all(bind=database.engine)

# Initialize FastAPI app
app = FastAPI(
    title="Subscription Analysis API",
    debug=settings.DEBUG
)

# Include routers
app.include_router(auth_router)
app.include_router(file_router)
app.include_router(card_router)
app.include_router(subscription_router)
