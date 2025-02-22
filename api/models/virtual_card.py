from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class VirtualCard(Base):
    __tablename__ = 'virtual_cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    virtual_card_id = Column(String, unique=True, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False, unique=True)

    group = relationship("Group", back_populates="virtual_card")
    card_members = relationship("CardMember", back_populates="virtual_card") 