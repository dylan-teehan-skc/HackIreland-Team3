from fastapi import APIRouter, HTTPException, Query
from api.routes.file_routes import file_storage  # Import the in-memory storage
from api.services.subscription_parser import process_subscriptions, get_subscriptions_sorted_by_date
import logging
import os
import json
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
    responses={404: {"description": "Not found"}}
)
logger = logging.getLogger(__name__)

@router.get("/subscriptions/{file_id}", responses={200: {"description": "List of subscriptions", "content": {"application/json": {"example": [{"Description": "POS NETFLIX", "Amount": 15.99, "Dates": ["2025-01-03"], "Estimated_Next": "2025-02-03"}]}}}})
async def get_subscriptions(file_id: str):
    logger.debug(f"Fetching subscriptions for file ID: {file_id}")
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

@router.get("/subscriptions/sorted/{file_id}", responses={200: {"description": "Sorted list of subscription transactions", "content": {"application/json": {"example": [{"Description": "POS NETFLIX", "Amount": 15.99, "Date": "2025-01-03", "Estimated_Next": "2025-02-03"}]}}}})
async def get_sorted_subscriptions(file_id: str):
    logger.debug(f"Fetching sorted subscriptions for file ID: {file_id}")
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

@router.get("/filter/{file_id}", responses={200: {"description": "Filtered list of subscriptions", "content": {"application/json": {"example": [{"Description": "POS NETFLIX", "Amount": 15.99, "Dates": ["2025-01-03"], "Estimated_Next": "2025-02-03"}]}}}})
async def filter_subscriptions(file_id: str, price: float = Query(None), description: str = Query(None)):
    logger.debug(f"Filtering subscriptions for file ID: {file_id} with price: {price}, description: {description}")
    try:
        # Retrieve the file path using the file ID from in-memory storage
        file_path = file_storage.get(file_id)
        if not file_path or not os.path.exists(file_path):
            logger.error(f"File ID {file_id} not found")
            raise HTTPException(status_code=404, detail="File ID not found")

        # Get all subscriptions for the file
        all_subscriptions = process_subscriptions(file_path)

        # Filter subscriptions based on price and description
        filtered_subscriptions = [
            sub for sub in all_subscriptions
            if (price is None or sub['Amount'] == price) and
               (description is None or description.lower() in sub['Description'].lower())
        ]

        logger.info(f"Filtered {len(filtered_subscriptions)} subscriptions for file ID {file_id}")
        return filtered_subscriptions
    except Exception as e:
        logger.error(f"Error filtering subscriptions: {str(e)}")
        raise HTTPException(status_code=500, detail="Error filtering subscriptions")

@router.get("/total_spent/{file_id}", responses={200: {"description": "Total amount spent on subscriptions in the last 12 months", "content": {"application/json": {"example": {"total_spent": 150.75}}}}})
async def total_spent(file_id: str):
    logger.debug(f"Calculating total spent for file ID: {file_id}")
    try:
        file_path = file_storage.get(file_id)
        logger.debug(f"File path: {file_path}")
        if not file_path or not os.path.exists(file_path):
            logger.error(f"File ID {file_id} not found")
            raise HTTPException(status_code=404, detail="File ID not found")

        subscriptions = process_subscriptions(file_path)
        logger.debug(f"Subscriptions: {subscriptions}")
        one_year_ago = datetime.now() - timedelta(days=365)
        logger.debug(f"One year ago: {one_year_ago}")

        total_spent = sum(
            sub['Amount'] for sub in subscriptions
            for date in sub['Dates']
            if datetime.strptime(date, "%Y-%m-%d") >= one_year_ago
        )

        logger.info(f"Total spent in the last 12 months: {total_spent}")
        return {"total_spent": total_spent}
    except Exception as e:
        logger.error(f"Error calculating total spent: {str(e)}")
        raise HTTPException(status_code=500, detail="Error calculating total spent")

@router.get("/specific_spent/{file_id}", responses={200: {"description": "Amount spent on a specific subscription in the last 12 months", "content": {"application/json": {"example": {"specific_spent": 59.97}}}}})
async def specific_spent(file_id: str, description: str, price: float):
    logger.debug(f"Calculating specific spent for file ID: {file_id}, description: {description}, price: {price}")
    try:
        file_path = file_storage.get(file_id)
        logger.debug(f"File path: {file_path}")
        if not file_path or not os.path.exists(file_path):
            logger.error(f"File ID {file_id} not found")
            raise HTTPException(status_code=404, detail="File ID not found")

        subscriptions = process_subscriptions(file_path)
        logger.debug(f"Subscriptions: {subscriptions}")
        one_year_ago = datetime.now() - timedelta(days=365)
        logger.debug(f"One year ago: {one_year_ago}")

        specific_spent = sum(
            sub['Amount'] for sub in subscriptions
            if sub['Description'].lower() == description.lower() and sub['Amount'] == price
            for date in sub['Dates']
            if datetime.strptime(date, "%Y-%m-%d") >= one_year_ago
        )

        logger.info(f"Specific spent in the last 12 months: {specific_spent}")
        return {"specific_spent": specific_spent}
    except Exception as e:
        logger.error(f"Error calculating specific spent: {str(e)}")
        raise HTTPException(status_code=500, detail="Error calculating specific spent")

@router.delete("/subscriptions/{file_id}/{description}/{amount}/{date}", responses={200: {"description": "Subscription deleted"}})
async def delete_subscription(file_id: str, description: str, amount: float, date: str):
    logger.debug(f"Deleting subscription for file ID: {file_id} with description: {description}, amount: {amount}, date: {date}")
    try:
        # Retrieve the file path using the file ID from in-memory storage
        file_path = file_storage.get(file_id)
        if not file_path or not os.path.exists(file_path):
            logger.error(f"File ID {file_id} not found")
            raise HTTPException(status_code=404, detail="File ID not found")

        # Process the subscriptions to get the current data
        subscriptions_data = get_subscriptions_sorted_by_date(file_path)

        # Find the subscription to delete
        subscription_to_delete = next(
            (sub for sub in subscriptions_data if sub["Description"] == description and sub["Amount"] == amount and sub["Date"] == date),
            None
        )
        
        if not subscription_to_delete:
            logger.error(f"Subscription with description {description}, amount {amount}, date {date} not found")
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Remove the subscription from the list
        subscriptions_data = [sub for sub in subscriptions_data if not (sub["Description"] == description and sub["Amount"] == amount and sub["Date"] == date)]
        logger.info(f"Subscription with description {description}, amount {amount}, date {date} deleted")
        return {"message": "Subscription deleted"}
    except Exception as e:
        logger.error(f"Error deleting subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting subscription") 