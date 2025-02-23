from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    admin = relationship("User", back_populates="groups")
    virtual_card = relationship("VirtualCard", uselist=False, back_populates="group")
    members = relationship("User", secondary="group_invitations", primaryjoin="and_(Group.id == GroupInvitation.group_id, GroupInvitation.accepted == True)", secondaryjoin="GroupInvitation.invitee_id == User.id", viewonly=True)