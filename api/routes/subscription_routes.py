from fastapi import APIRouter, HTTPException
from api.routes.file_routes import file_storage  # Import the in-memory storage
from api.services.subscription_parser import process_subscriptions, get_subscriptions_sorted_by_date
import logging
import os
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/subscriptions/{file_id}")
async def get_subscriptions(file_id: str):
    try:
        # Retrieve the file path using the file ID from in-memory storage
        file_path = file_storage.get(file_id)
        if not file_path or not os.path.exists(file_path):
            logger.error(f"File ID {file_id} not found")
            raise HTTPException(status_code=404, detail="File ID not found")

        # Directly return the result from process_subscriptions
        subscriptions = process_subscriptions(file_path)
        logger.info(f"Subscriptions retrieved for file ID {file_id}")
        return subscriptions
    except Exception as e:
        logger.error(f"Error processing subscriptions: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing subscriptions")

@router.get("/subscriptions/sorted/{file_id}")
async def get_sorted_subscriptions(file_id: str):
    try:
        # Retrieve the file path using the file ID from in-memory storage
        file_path = file_storage.get(file_id)
        if not file_path or not os.path.exists(file_path):
            logger.error(f"File ID {file_id} not found")
            raise HTTPException(status_code=404, detail="File ID not found")

        # Directly return the result from get_subscriptions_sorted_by_date
        sorted_subscriptions = get_subscriptions_sorted_by_date(file_path)
        logger.info(f"Sorted subscriptions retrieved for file ID {file_id}")
        return sorted_subscriptions
    except Exception as e:
        logger.error(f"Error processing sorted subscriptions: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing sorted subscriptions") 