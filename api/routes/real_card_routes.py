from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..models import User, RealCard
from ..auth import get_current_active_user
from ..database import get_db

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/real-cards",
    tags=["Real Cards"],
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"}
    }
)

class RealCardCreate(BaseModel):
    card_number: str
    card_holder_name: str
    expiry_date: str

@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_real_card(
    card_data: RealCardCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Refresh current user to ensure we have latest state
    current_user = db.merge(current_user)
    db.refresh(current_user)
    
    # Check if user already has a real card
    if current_user.real_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already has a real card registered'
        )
    
    try:
        # Create new real card
        real_card = RealCard(
            card_number=card_data.card_number,
            card_holder_name=card_data.card_holder_name,
            expiry_date=card_data.expiry_date
        )
        
        # Associate the real card with the current persistent user
        real_card.user = current_user
        
        # Add and commit
        db.add(real_card)
        db.commit()
        
        # Refresh user object to get updated relationships
        db.refresh(current_user)
        
        logger.info(f"User {current_user.id} added real card {real_card.id}")
        
        return {
            'message': 'Real card added successfully',
            'card_holder_name': real_card.card_holder_name
        }
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error adding real card for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to add real card'
        )

class RealCardResponse(BaseModel):
    card_holder_name: str
    card_number: str
    expiry_date: str

@router.get('/', response_model=RealCardResponse)
async def get_real_card(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's real card information"""
    # Get fresh user data with relationships
    user = db.query(User).filter(User.id == current_user.id).first()
    
    # Debug information
    print(f"User ID: {user.id}")
    print(f"Real Card ID: {user.real_card_id}")
    
    if not user.real_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No real card found'
        )
        
    return RealCardResponse(
        card_holder_name=current_user.real_card.card_holder_name,
        card_number='****' + current_user.real_card.card_number[-4:],  # Only show last 4 digits
        expiry_date=current_user.real_card.expiry_date
    )

@router.delete('/', status_code=status.HTTP_200_OK)
async def remove_real_card(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove user's real card"""
    if not current_user.real_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No real card found'
        )
    
    try:
        # Check if user is part of any groups
        if current_user.card_memberships:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Cannot remove card while member of groups. Leave all groups first.'
            )
        
        # Remove the real card
        db.delete(current_user.real_card)
        current_user.real_card_id = None
        db.commit()
        
        return {'message': 'Real card removed successfully'}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
