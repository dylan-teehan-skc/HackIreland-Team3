from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from api.routes.file_routes import get_file_path
from api.services.subscription_parser import process_subscriptions, get_subscriptions_sorted_by_date
from api.database import get_db
from api.auth import get_current_active_user
from api.models.subscription import Subscription
from api.models.user import User
from api.models.uploaded_file import UploadedFile
from api.models import Group
import logging
import os
import json
from datetime import datetime, timedelta
from typing import List

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
    responses={404: {"description": "Not found"}}
)
logger = logging.getLogger(__name__)

@router.post("/upload/{file_id}")
async def create_subscriptions_from_file(
    file_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create subscriptions from an uploaded file and associate them with the current user."""
    try:
        # Get the file path and verify it exists
        file_path = get_file_path(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
            
        # Process subscriptions from the file
        subscriptions_data = process_subscriptions(file_path)
        
        # Create UploadedFile record
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        uploaded_file = UploadedFile(
            file_name=os.path.basename(file_path),
            file_content=file_content,
            file_path=file_path,
            user_id=current_user.id
        )
        db.add(uploaded_file)
        db.commit()
        db.refresh(uploaded_file)
        
        # Delete any existing subscriptions for this user from this file
        db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.file_id == uploaded_file.id
        ).delete()
        
        # Create new subscription records
        for sub in subscriptions_data:
            subscription = Subscription(
                description=sub["Description"],
                amount=sub["Amount"],
                date=datetime.strptime(sub["Dates"][-1], '%Y-%m-%d').date(),
                estimated_next_date=datetime.strptime(sub["Estimated_Next"], '%Y-%m-%d').date() if sub.get("Estimated_Next") else None,
                user_id=current_user.id,
                file_id=uploaded_file.id,
                group_id=sub.get("GroupID")  # Optional group association
            )
            db.add(subscription)
            logger.info(f"Prepared to add subscription: {sub['Description']} for user ID: {current_user.id}")

        db.commit()
        logger.info(f"Successfully saved {len(subscriptions_data)} subscriptions for user ID: {current_user.id}")
        return {"message": "Subscriptions created successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating subscriptions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user")
async def get_user_subscriptions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all subscriptions for the current user."""
    try:
        subscriptions = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).all()
        
        return [{
            "id": sub.id,
            "description": sub.description,
            "amount": sub.amount,
            "date": sub.date.strftime('%Y-%m-%d'),
            "estimated_next_date": sub.estimated_next_date.strftime('%Y-%m-%d') if sub.estimated_next_date else None,
            "file_id": sub.file_id
        } for sub in subscriptions]
        
    except Exception as e:
        logger.error(f"Error getting user subscriptions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{subscription_id}")
async def delete_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a specific subscription."""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id,
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
            
        db.delete(subscription)
        db.commit()
        
        return {"message": "Subscription deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscriptions/{file_id}", responses={200: {"description": "List of subscriptions", "content": {"application/json": {"example": [{"Description": "POS NETFLIX", "Amount": 15.99, "Dates": ["2025-01-03"], "Estimated_Next": "2025-02-03"}]}}}})
async def get_subscriptions(file_id: str):
    logger.debug(f"Fetching subscriptions for file ID: {file_id}")
    try:
        # Retrieve the file path using the file ID from in-memory storage
        file_path = get_file_path(file_id)
        if not file_path:
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
        file_path = get_file_path(file_id)
        if not file_path:
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
        file_path = get_file_path(file_id)
        if not file_path:
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
        file_path = get_file_path(file_id)
        logger.debug(f"File path: {file_path}")
        if not file_path:
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
    logger.setLevel(logging.DEBUG)
    logger.debug(f"Calculating specific spent for file ID: {file_id}, description: {description}, price: {price}")
    try:
        file_path = get_file_path(file_id)
        logger.debug(f"File path: {file_path}")
        if not file_path:
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
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/subscriptions/{file_id}/{description}/{amount}/{date}", responses={200: {"description": "Subscription deleted"}})
async def delete_subscription(file_id: str, description: str, amount: float, date: str):
    logger.debug(f"Deleting subscription for file ID: {file_id} with description: {description}, amount: {amount}, date: {date}")
    try:
        # Retrieve the file path using the file ID from in-memory storage
        file_path = get_file_path(file_id)
        if not file_path:
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

@router.post("/subscriptions/create")
async def create_subscriptions(subscriptions: List[dict], db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    try:
        for sub in subscriptions:
            new_subscription = Subscription(
                description=sub['description'],
                amount=sub['amount'],
                date=sub['date'],
                estimated_next_date=sub.get('estimated_next_date'),
                user_id=current_user.id,  # Associate with the current user
                file_id=sub['file_id']
            )
            db.add(new_subscription)
            logger.info(f"Prepared to add subscription: {sub['description']} for user ID: {current_user.id}")

        db.commit()
        logger.info(f"Successfully saved {len(subscriptions)} subscriptions for user ID: {current_user.id}")
        return {"message": "Subscriptions created successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving subscriptions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscriptions/{subscription_id}/add-to-group")
async def add_subscription_to_group(subscription_id: int, group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    subscription.group_id = group_id
    db.commit()
    return {"message": "Subscription added to group successfully"} 