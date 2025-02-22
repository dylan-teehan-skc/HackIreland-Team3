from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class RealCard(Base):
    __tablename__ = 'real_cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_number = Column(String, nullable=False, unique=True)
    card_holder_name = Column(String, nullable=False)
    expiry_date = Column(String, nullable=False)
    
    # One-to-one relationship with User
    user = relationship("User", back_populates="real_card", uselist=False)
