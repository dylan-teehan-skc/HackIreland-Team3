from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta
import json
import logging
from .models import UploadedFile, User
from .database import SessionLocal
from .subscription_parser import load_data, preprocess_data, find_subscriptions
from .cardCreation import create_cardholder, create_virtual_card, get_virtual_card, create_test_card
from .auth import (
    get_current_active_user,
    get_password_hash,
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Get logger
logger = logging.getLogger(__name__)

# Create routers
auth_router = APIRouter(prefix="/auth", tags=["auth"])
file_router = APIRouter(prefix="/files", tags=["files"])
card_router = APIRouter(prefix="/cards", tags=["cards"])
health_router = APIRouter(tags=["health"])

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth routes
@auth_router.post("/register", response_model=dict)
def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User created successfully"}

@auth_router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# File routes
@file_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Save the file to a temporary location
        file_id = str(db.query(UploadedFile).count() + 1)
        file_path = f"temp_{file_id}.xlsx"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Store file metadata in the database
        new_file = UploadedFile(file_path=file_path, user_id=current_user.id)
        db.add(new_file)
        db.commit()

        logger.info(f"File uploaded successfully with ID {new_file.id}")
        return {"message": "File uploaded successfully", "file_id": new_file.id}
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

@file_router.get("/subscriptions/{file_id}")
async def get_subscriptions(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        uploaded_file = db.query(UploadedFile).get(file_id)
        if not uploaded_file:
            logger.error(f"File ID {file_id} not found")
            raise HTTPException(status_code=404, detail="File ID not found")

        df = load_data(uploaded_file.file_path)
        
        if "Money Out" not in df.columns:
            logger.error("The 'Money Out' column is missing from the data")
            raise HTTPException(status_code=400, detail="The 'Money Out' column is missing from the data")

        df = preprocess_data(df)
        if df.empty:
            logger.warning("No data to process")
            raise HTTPException(status_code=400, detail="No data to process")

        subscriptions_json = find_subscriptions(df)
        logger.info(f"Subscriptions retrieved for file ID {file_id}")
        return json.loads(subscriptions_json)
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

# Health route
@health_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

# Card routes
@card_router.post("/create-cardholder")
async def create_cardholder_endpoint(
    name: str,
    email: str,
    phone_number: str,
    address_line1: str,
    city: str,
    state: str,
    postal_code: str,
    country: str = "US",
    current_user: User = Depends(get_current_active_user)
):
    """Endpoint to create a new cardholder"""
    result = create_cardholder(
        name=name,
        email=email,
        phone_number=phone_number,
        address_line1=address_line1,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country
    )
    return result

@card_router.post("/create-virtual-card")
async def create_virtual_card_endpoint(cardholder_id: str):
    """Endpoint to create a new virtual card"""
    result = create_virtual_card(cardholder_id)
    return result

@card_router.get("/virtual-card/{card_id}")
async def get_virtual_card_endpoint(card_id: str):
    """Endpoint to get virtual card details"""
    result = get_virtual_card(card_id)
    return result

@card_router.post("/test-card")
async def test_card_endpoint():
    """Endpoint to create a test card"""
    result = create_test_card()
    return result
