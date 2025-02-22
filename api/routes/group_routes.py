from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from ..models import User, Group, VirtualCard, CardMember
from ..auth import get_current_active_user
from ..database import get_db

router = APIRouter()

class GroupCreate(BaseModel):
    name: str

@router.post('/groups', status_code=status.HTTP_201_CREATED)
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
        
        # Create associated virtual card
        virtual_card = VirtualCard(
            virtual_card_id=f"V-{new_group.id}",  # Simple virtual card ID format
            group_id=new_group.id
        )
        db.add(virtual_card)
        
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
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Group creation failed'
        )

@router.post('/groups/{group_id}/join', status_code=status.HTTP_200_OK)
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

@router.get('/groups/{group_id}/members', response_model=List[GroupMember])
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

@router.get('/user/groups', response_model=List[UserGroup])
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
