from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class GroupInvitation(Base):
    __tablename__ = 'group_invitations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    inviter_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    invitee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    accepted = Column(Boolean, default=False)
    
    group = relationship("Group", backref="invitations")
    inviter = relationship("User", foreign_keys=[inviter_id], backref="sent_invitations")
    invitee = relationship("User", foreign_keys=[invitee_id], backref="received_invitations")
