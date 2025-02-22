from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, validator

from ..models import User, Group, VirtualCard, CardMember
from ..auth import get_current_active_user
from ..database import get_db
from ..services.cardCreation import create_cardholder, create_virtual_card

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/groups",
    tags=["Groups"],
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"}
    }
)

class GroupCreate(BaseModel):
    name: str
    
    @validator('name')
    def validate_name(cls, v):
        # Remove leading/trailing whitespace
        v = v.strip()
        if not v:
            raise ValueError('Name cannot be empty')
        if len(v) > 50:  # Reasonable limit for a group name
            raise ValueError('Name cannot be longer than 50 characters')
        return v

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    
    # Check if user has a real card
    if not current_user.real_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You must add a real card before creating a group'
        )
    
    try:
        # Create the group
        new_group = Group(
            name=group_data.name,
            admin_id=current_user.id
        )
        db.add(new_group)
        db.flush()  # Get the group ID
        
        logging.debug(f"User {current_user.id} is creating group {new_group.id}")
        logging.debug(f"User {current_user.id} is from {current_user.country}")
        # Verify country is Ireland before creating cardholder
        if current_user.country != 'IE':
            logging.debug(f"User {current_user.id} is from {current_user.country}, so can't create groups")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Only users from Ireland (IE) can create groups at this time'
            )

        # Create Stripe cardholder for the group
        cardholder_result = create_cardholder(
            name=current_user.name,  # Use admin's name for Stripe cardholder
            email=current_user.email,  # Use admin's email for now
            phone_number=current_user.phone_number,
            address_line1=current_user.address_line1,
            city=current_user.city,
            state=current_user.state,
            postal_code=current_user.postal_code,
            country=current_user.country  # Pass the user's country
        )
        
        if not cardholder_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Failed to create Stripe cardholder: {cardholder_result["error"]}'
            )
            
        # Create Stripe virtual card
        card_result = create_virtual_card(cardholder_result["cardholder"].id)
        if not card_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Failed to create Stripe virtual card: {card_result["error"]}'
            )
            
        # Create associated virtual card in our database
        virtual_card = VirtualCard(
            virtual_card_id=card_result["card"].id,  # Use Stripe card ID
            group_id=new_group.id
        )
        db.add(virtual_card)
        db.flush()  # Flush to assign virtual_card.id
        
        # Add admin as first member
        member = CardMember(
            card_id=virtual_card.id,
            user_id=current_user.id
        )
        db.add(member)
        
        db.commit()
        return {
            'message': 'Group created successfully',
            'group_id': new_group.id,
            'virtual_card_id': virtual_card.virtual_card_id
        }
        
    except IntegrityError as e:
        db.rollback()
        logger.error("IntegrityError: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Group creation failed'
        )


@router.post('/{group_id}/join', status_code=status.HTTP_200_OK)
async def join_group(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    
    # Check if user has a real card
    if not current_user.real_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You must add a real card before joining a group'
        )
    
    try:
        # Check if group exists
        group = db.query(Group).get(group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Group not found'
            )
        # Check if user is already a member
        existing_membership = db.query(CardMember).join(VirtualCard).filter(
            VirtualCard.group_id == group_id,
            CardMember.user_id == current_user.id
        ).first()
        
        if existing_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Already a member of this group'
            )
            
        # Add user as member
        virtual_card = db.query(VirtualCard).filter_by(group_id=group_id).first()
        member = CardMember(
            card_id=virtual_card.id,
            user_id=current_user.id
        )
        db.add(member)
        db.commit()
        
        return {'message': 'Successfully joined group'}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to join group'
        )

class GroupMember(BaseModel):
    id: int
    name: str
    email: str
    is_admin: bool

@router.get('/{group_id}/members', response_model=List[GroupMember])
async def get_group_members(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all members of a group"""
    try:
        # Check if group exists
        group = db.query(Group).get(group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Group not found'
            )
        # Get all members
        members = db.query(User).join(CardMember).join(VirtualCard).filter(
            VirtualCard.group_id == group_id
        ).all()
        
        return [
            GroupMember(
                id=member.id,
                name=member.name,
                email=member.email,
                is_admin=member.id == group.admin_id
            ) for member in members
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

class UserGroup(BaseModel):
    id: int
    name: str
    is_admin: bool
    virtual_card_id: str

@router.get('/my', response_model=List[UserGroup])
async def get_user_groups(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        # Get all groups user is a member of
        groups = db.query(Group).join(VirtualCard).join(CardMember).filter(
            CardMember.user_id == current_user.id
        ).all()
        
        return [
            UserGroup(
                id=group.id,
                name=group.name,
                is_admin=group.admin_id == current_user.id,
                virtual_card_id=group.virtual_card.virtual_card_id
            ) for group in groups
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete('/{group_id}', status_code=status.HTTP_200_OK)
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a group. Only the group admin can delete their group."""
    
    # Get the group
    group = db.query(Group).get(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Group not found'
        )
    
    # Check if current user is the admin
    if group.admin_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only the group admin can delete the group'
        )
    
    try:
        # Delete all card memberships associated with the group's virtual card
        db.query(CardMember).filter(
            CardMember.card_id == group.virtual_card.id
        ).delete()
        
        # Delete the virtual card
        db.query(VirtualCard).filter(
            VirtualCard.group_id == group.id
        ).delete()
        
        # Delete the group
        db.delete(group)
        db.commit()
        
        return {'message': 'Group deleted successfully'}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to delete group'
        )
