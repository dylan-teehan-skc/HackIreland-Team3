from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from api.models import UploadedFile
from api.database import get_db
from api.services.subscription_parser import process_subscriptions
import logging

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
    responses={404: {"description": "Not found"}}
)
logger = logging.getLogger(__name__)

@router.get("/subscriptions/{file_id}")
async def get_subscriptions(file_id: int, db: Session = Depends(get_db)):
    try:
        uploaded_file = db.query(UploadedFile).get(file_id)
        if not uploaded_file:
            logger.error(f"File ID {file_id} not found")
            raise HTTPException(status_code=404, detail="File ID not found")

        subscriptions_json = process_subscriptions(uploaded_file.file_path)
        logger.info(f"Subscriptions retrieved for file ID {file_id}")
        return subscriptions_json
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error") 