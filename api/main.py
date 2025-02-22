from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import api.database as database 
from .models.base import Base
from .config import get_settings, setup_logging
from .routes import file_router, card_router, subscription_router, auth_router, webhook_routes, group_routes, real_card_routes
import logging

# Import all models to ensure they are registered with SQLAlchemy
from .models import User, Group, VirtualCard, CardMember, RealCard, UploadedFile

# Initialize settings and logging
settings = get_settings()
setup_logging()  # This sets up logging as per the configuration in logging_config.py

# Debug database URL
print(f"Database URL: {settings.DATABASE_URL}")

# Ensure all models are registered with Base
print("Registered models:", Base.metadata.tables.keys())

# Create database tables
print("Creating database tables...")
Base.metadata.create_all(bind=database.engine)
print("Database tables created successfully")

# Initialize FastAPI app
app = FastAPI(
    title="Subscription Analysis API",
    debug=settings.DEBUG,
    # Add OpenAPI security scheme configuration
    openapi_tags=[{
        "name": "Authentication",
        "description": "Operations with users. OAuth2 with Password and Bearer token."
    }],
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth_router)
app.include_router(file_router)
app.include_router(card_router)
app.include_router(subscription_router)
app.include_router(webhook_routes.router)
app.include_router(group_routes.router)
app.include_router(real_card_routes.router)


# Example of logging usage in main.py
logger = logging.getLogger(__name__)
logger.info("Application startup complete")
