from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, validator
from datetime import datetime

from ..models import User, Group, VirtualCard, CardMember, GroupInvitation
from ..auth import get_current_active_user
from ..database import get_db
from ..services.cardCreation import create_cardholder, create_virtual_card, get_virtual_card

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

class InviteUser(BaseModel):
    username: str

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
        display_name = f"{current_user.first_name} {current_user.last_name}"
        cardholder_result = create_cardholder(
            name=display_name,  # Use admin's full name for Stripe cardholder
            email=current_user.email,  # Use admin's email for now
            phone_number=current_user.phone_number,
            address_line1=current_user.address_line1,
            city=current_user.city,
            state=current_user.state,
            postal_code=current_user.postal_code,
            country=current_user.country,  # Pass the user's country
            date_of_birth=current_user.date_of_birth,
            full_legal_name={
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
            }
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
                detail=f'Failed to create virtual card: {card_result["error"]}'
            )

        # Store virtual card details with the group
        new_group.virtual_card_id = card_result["card"].id
        new_group.virtual_card_last4 = card_result["card"].last4
        new_group.virtual_card_exp_month = card_result["card"].exp_month
        new_group.virtual_card_exp_year = card_result["card"].exp_year
        db.add(new_group)
        db.flush()  # This will assign an ID to new_group
        
        # Create virtual card record
        virtual_card = VirtualCard(
            virtual_card_id=card_result["card"].id,
            group_id=new_group.id
        )
        db.add(virtual_card)
        db.flush()  # This will assign an ID to virtual_card
        
        # Add the creator as a member of the group via CardMember
        card_member = CardMember(
            card_id=virtual_card.id,
            user_id=current_user.id
        )
        db.add(card_member)
        
        db.commit()
        return {
            'message': 'Group created successfully',
            'group_id': new_group.id,
            'virtual_card_id': new_group.virtual_card_id
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
    username: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
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
                username=member.username,
                first_name=member.first_name,
                last_name=member.last_name,
                middle_name=member.middle_name,
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
    group_name: str  # This is the group's name, not the user's name
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
                group_name=group.name,
                is_admin=group.admin_id == current_user.id,
                virtual_card_id=group.virtual_card_id
            ) for group in groups
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post('/{group_id}/invite')
async def invite_to_group(
    group_id: int,
    invite_data: InviteUser,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if group exists and user is admin
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Group not found'
        )
    
    if group.admin_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only group admin can invite users'
        )
    
    # Find invitee by username
    invitee = db.query(User).filter(User.username == invite_data.username).first()
    if not invitee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    # Check if user is already in group
    existing_member = db.query(CardMember).filter(
        CardMember.user_id == invitee.id,
        CardMember.card_id == group.virtual_card.id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User is already a member of this group'
        )
    
    # Check if invitation already exists
    existing_invitation = db.query(GroupInvitation).filter(
        GroupInvitation.group_id == group_id,
        GroupInvitation.invitee_id == invitee.id,
        GroupInvitation.accepted == False
    ).first()
    
    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User has already been invited to this group'
        )
    
    # Create invitation
    invitation = GroupInvitation(
        group_id=group_id,
        inviter_id=current_user.id,
        invitee_id=invitee.id
    )
    
    db.add(invitation)
    db.commit()
    
    return {'message': f'Invitation sent to {invitee.username}'}

@router.get('/invitations/pending', response_model=List[dict])
async def get_pending_invitations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    invitations = db.query(GroupInvitation).filter(
        GroupInvitation.invitee_id == current_user.id,
        GroupInvitation.accepted == False
    ).all()
    
    return [{
        'id': inv.id,
        'group_name': inv.group.name,
        'inviter_username': inv.inviter.username,
        'created_at': inv.created_at.isoformat()
    } for inv in invitations]

@router.post('/invitations/{invitation_id}/accept')
async def accept_invitation(
    invitation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    invitation = db.query(GroupInvitation).filter(
        GroupInvitation.id == invitation_id,
        GroupInvitation.invitee_id == current_user.id,
        GroupInvitation.accepted == False
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Invitation not found or already accepted'
        )
    
    # Add user to group
    group = invitation.group
    if not group.virtual_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Group does not have a virtual card'
        )
    
    new_member = CardMember(
        user_id=current_user.id,
        card_id=group.virtual_card.id
    )
    
    invitation.accepted = True
    db.add(new_member)
    db.commit()
    
    return {'message': f'Successfully joined group {group.name}'}

@router.get('/{group_id}/card')
async def get_group_card_details(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if user is a member of the group by joining through virtual_cards
    member = db.query(CardMember).join(
        VirtualCard, CardMember.card_id == VirtualCard.id
    ).filter(
        VirtualCard.group_id == group_id,
        CardMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not a member of this group'
        )
    
    # Retrieve the virtual card id associated with the group id
    virtual_card = db.query(VirtualCard).filter(VirtualCard.group_id == group_id).first()
    if not virtual_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Virtual card not found for this group'
        )

    print(virtual_card.virtual_card_id)

    # Return the virtual card id along with other card details
    card_data = get_virtual_card(virtual_card.virtual_card_id)
    if not card_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Group not found'
        )
    
    return {
        'virtual_card_id': virtual_card.id,
        'card_details': {
            'number': card_data['card']['number'],
            'exp_month': card_data['card']['exp_month'],
            'exp_year': card_data['card']['exp_year'],
            'cvc': card_data['card']['cvc'],
            'status': card_data['card'].get('status', 'active'),
            'type': card_data['card'].get('type', 'debit')
        }
    }

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
