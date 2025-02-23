from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from .base import Base
from typing import Optional

class User(Base):
    # Address fields for Stripe
    address_line1 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True, default='US')
    phone_number = Column(String, nullable=True)
    card_holder_id = Column(String, nullable=True)
    stripe_customer_id = Column(String, unique=True, nullable=True)

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    real_card_id = Column(Integer, ForeignKey('real_cards.id'), unique=True)
    
    # Legal name fields
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    
    # Additional required fields
    date_of_birth = Column(Date, nullable=False)

    real_card = relationship("RealCard", back_populates="user", uselist=False)
    groups = relationship("Group", back_populates="admin")
    card_memberships = relationship("CardMember", back_populates="user")