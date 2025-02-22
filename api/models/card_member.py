from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class CardMember(Base):
    __tablename__ = 'card_members'

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(Integer, ForeignKey('virtual_cards.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    virtual_card = relationship("VirtualCard", back_populates="card_members")
    user = relationship("User", back_populates="card_memberships") 