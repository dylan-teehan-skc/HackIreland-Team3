from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class GroupMemberRatio(Base):
    __tablename__ = 'group_member_ratios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ratio_percentage = Column(Float, nullable=False)  # Stored as decimal (e.g., 25.5 for 25.5%)

    # Relationships
    group = relationship("Group", backref="member_ratios")
    user = relationship("User", backref="group_ratios")

    # Ensure a user can only have one ratio entry per group
    __table_args__ = (
        UniqueConstraint('group_id', 'user_id', name='unique_group_member_ratio'),
    )
