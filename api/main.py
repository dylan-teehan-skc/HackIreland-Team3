from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import logging
from .database import SessionLocal, engine, Base
from .models import UploadedFile
from .subscription_parser import load_data, preprocess_data, find_subscriptions
from .cardCreation import create_cardholder, create_virtual_card, get_virtual_card, create_test_card
from .config import get_settings, setup_logging
import json

# Initialize settings and logging
settings = get_settings()
setup_logging()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Subscription Analysis API",
    debug=settings.DEBUG
)

# Get logger
logger = logging.getLogger(__name__)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Save the file to a temporary location
        file_id = str(db.query(UploadedFile).count() + 1)
        file_path = f"temp_{file_id}.xlsx"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Store file metadata in the database
        new_file = UploadedFile(file_path=file_path)
        db.add(new_file)
        db.commit()

        logger.info(f"File uploaded successfully with ID {new_file.id}")
        return {"message": "File uploaded successfully", "file_id": new_file.id}
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/subscriptions/{file_id}")
async def get_subscriptions(file_id: int, db: Session = Depends(get_db)):
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

# Card-related endpoints
@app.post("/cards/create-cardholder")
async def create_cardholder_endpoint(
    name: str,
    email: str,
    phone_number: str,
    address_line1: str,
    city: str,
    state: str,
    postal_code: str,
    country: str = "US"
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

@app.post("/cards/create-virtual-card")
async def create_virtual_card_endpoint(cardholder_id: str):
    """Endpoint to create a new virtual card"""
    result = create_virtual_card(cardholder_id)
    return result

@app.get("/cards/virtual-card/{card_id}")
async def get_virtual_card_endpoint(card_id: str):
    """Endpoint to get virtual card details"""
    result = get_virtual_card(card_id)
    return result

@app.post("/cards/test-card")
async def test_card_endpoint():
    """Endpoint to create a test card"""
    result = create_test_card()
    return result
