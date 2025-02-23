from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import BaseModel
import stripe
from ..config import settings

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
    payment_method_id: str  # Stripe payment method ID from frontend
    card_holder_name: str

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
        try:
            # Verify the user has a Stripe customer ID
            if not current_user.stripe_customer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='User does not have a Stripe customer ID'
                )

            # Retrieve payment method to get card details
            payment_method = stripe.PaymentMethod.retrieve(card_data.payment_method_id)
            if not payment_method or payment_method.type != 'card':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Invalid payment method ID'
                )

            # Attach payment method to customer if not already attached
            if payment_method.customer != current_user.stripe_customer_id:
                stripe.PaymentMethod.attach(
                    card_data.payment_method_id,
                    customer=current_user.stripe_customer_id,
                )

            # Set as default payment method
            stripe.Customer.modify(
                current_user.stripe_customer_id,
                invoice_settings={
                    'default_payment_method': card_data.payment_method_id
                }
            )

            # Create new real card in our database
            card = payment_method.card
            real_card = RealCard(
                card_number=f"**** **** **** {card.last4}",  # Only store last 4 digits
                card_holder_name=card_data.card_holder_name,
                expiry_date=f"{card.exp_month:02d}/{str(card.exp_year)[-2:]}",
                cvc="***",  # Don't store actual CVC
                stripe_payment_method_id=card_data.payment_method_id
            )

            # Associate the real card with the current persistent user
            real_card.user = current_user

            # Add and commit
            db.add(real_card)
            db.commit()
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error while adding card for user {current_user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Failed to add card to Stripe: {str(e)}'
            )
        
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
    cvc: str

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

@router.get('/has-card', response_model=dict)
async def check_has_card(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if user has a real card"""
    # Refresh current user to ensure we have latest state
    current_user = db.merge(current_user)
    db.refresh(current_user)
    
    return {"has_card": bool(current_user.real_card)}

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
