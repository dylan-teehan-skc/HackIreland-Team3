from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, date
from typing import Dict, Optional
from pydantic import BaseModel
import stripe
from api.config import settings

from api.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    get_db
)
from api.models import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}}
)

@router.post("/token", response_model=Dict[str, str])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

class LegalName(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None

class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    legal_name: LegalName
    date_of_birth: date
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = 'US'
    phone_number: Optional[str] = None

@router.post("/register", response_model=Dict[str, str])
async def register_user(
    user_data: UserRegistration,
    db: Session = Depends(get_db)
):
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    # Create new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.legal_name.first_name,
        last_name=user_data.legal_name.last_name,
        middle_name=user_data.legal_name.middle_name,
        date_of_birth=user_data.date_of_birth,
        address_line1=user_data.address_line1,
        city=user_data.city,
        state=user_data.state,
        postal_code=user_data.postal_code,
        country=user_data.country,
        phone_number=user_data.phone_number
    )
    
    # Create Stripe customer
    try:
        customer = stripe.Customer.create(
            email=user_data.email,
            name=f"{user_data.legal_name.first_name} {user_data.legal_name.last_name}",
            phone=user_data.phone_number,
            address={
                'line1': user_data.address_line1,
                'city': user_data.city,
                'state': user_data.state,
                'postal_code': user_data.postal_code,
                'country': user_data.country,
            } if user_data.address_line1 else None
        )
        new_user.stripe_customer_id = customer.id
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Stripe customer: {str(e)}"
        )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token for the new user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=Dict[str, str])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return {
        "name": current_user.name,
        "email": current_user.email
    }
