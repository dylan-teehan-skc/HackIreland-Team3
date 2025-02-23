from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, validator
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)
from ..models import User, Group, GroupMemberRatio, GroupInvitation
from ..auth import get_current_active_user
from ..database import get_db

router = APIRouter(
    prefix="/groups",
    tags=["Group Ratios"],
    responses={401: {"description": "Unauthorized"}}
)

class MemberRatio(BaseModel):
    user_id: int
    ratio_percentage: float

    @validator('ratio_percentage')
    def validate_ratio(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Ratio must be between 0 and 100')
        return v

class GroupRatios(BaseModel):
    ratios: List[MemberRatio]

    @validator('ratios')
    def validate_total_ratio(cls, v):
        total = sum(ratio.ratio_percentage for ratio in v)
        if not (99.99 <= total <= 100.01):  # Allow small floating-point imprecision
            raise ValueError('Total ratio percentages must equal 100%')
        return v


@router.post('/{group_id}/ratios', status_code=status.HTTP_200_OK)
async def set_group_ratios(
    group_id: int,
    ratios: GroupRatios,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get the group
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        logger.error(f"Group not found for group_id: {group_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Group not found'
        )

    # Debug log for admin check
    logger.info(f"Current user ID: {current_user.id}, Group admin ID: {group.admin_id}")
    
    # Only admin can set ratios
    if not group.admin_id == current_user.id:
        logger.error(f"User {current_user.id} is not admin of group {group_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only group admin can set payment ratios'
        )
    
    # Debug log for members
    logger.info(f"Group members before conversion: {group.members}")
    member_ids = {member.id for member in group.members}
    # Include the admin explicitly
    member_ids.add(group.admin_id)
    logger.info(f"Member IDs set (including admin): {member_ids}")
    logger.info(f"Ratios to set: {[r.dict() for r in ratios.ratios]}")

    # Alternative way to get members - let's check both methods
    direct_members = db.query(GroupInvitation).filter(
        GroupInvitation.group_id == group_id,
        GroupInvitation.accepted == True
    ).all()
    direct_member_ids = {inv.invitee_id for inv in direct_members}
    direct_member_ids.add(group.admin_id)  # Add admin here too
    logger.info(f"Direct query member IDs (including admin): {direct_member_ids}")

    # Verify all users in ratios are group members using both sets
    for ratio in ratios.ratios:
        if ratio.user_id not in member_ids and ratio.user_id not in direct_member_ids:
            logger.error(f"User {ratio.user_id} not found in either member set. Member IDs: {member_ids}, Direct IDs: {direct_member_ids}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'User {ratio.user_id} is not a member of this group'
            )

    # Delete existing ratios
    db.query(GroupMemberRatio).filter(
        GroupMemberRatio.group_id == group_id
    ).delete()

    # Create new ratios
    for ratio in ratios.ratios:
        new_ratio = GroupMemberRatio(
            group_id=group_id,
            user_id=ratio.user_id,
            ratio_percentage=ratio.ratio_percentage
        )
        db.add(new_ratio)

    try:
        db.commit()
    except Exception as e:
        print(e)
        logger.error(f"Failed to update ratios for group {group_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to update ratios: {str(e)}'
        )

    return {'message': 'Group payment ratios updated successfully'}

@router.get('/{group_id}/ratios', response_model=GroupRatios)
async def get_group_ratios(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get the group
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Group not found'
        )

    # Check if user is group member or admin
    is_member = db.query(GroupInvitation).filter(
        GroupInvitation.group_id == group_id,
        GroupInvitation.invitee_id == current_user.id,
        GroupInvitation.accepted == True
    ).first() is not None
    
    if not (is_member or group.admin_id == current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only group members can view payment ratios'
        )

    # Get all group members
    member_invitations = db.query(GroupInvitation).filter(
        GroupInvitation.group_id == group_id,
        GroupInvitation.accepted == True
    ).all()
    member_ids = [inv.invitee_id for inv in member_invitations]
    
    # Get existing ratios
    ratios = db.query(GroupMemberRatio).filter(
        GroupMemberRatio.group_id == group_id
    ).all()
    
    # If no ratios exist, create default equal ratios
    if not ratios:
        num_members = len(member_ids)
        if num_members > 0:
            equal_ratio = 100.0 / num_members
            # Create default ratios in database
            for member_id in member_ids:
                new_ratio = GroupMemberRatio(
                    group_id=group_id,
                    user_id=member_id,
                    ratio_percentage=equal_ratio
                )
                db.add(new_ratio)
            try:
                db.commit()
                # Fetch the newly created ratios
                ratios = db.query(GroupMemberRatio).filter(
                    GroupMemberRatio.group_id == group_id
                ).all()
            except Exception as e:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to create default ratios: {str(e)}'
                )
    
    return GroupRatios(
        ratios=[
            MemberRatio(
                user_id=ratio.user_id,
                ratio_percentage=ratio.ratio_percentage
            )
            for ratio in ratios
        ]
    )
