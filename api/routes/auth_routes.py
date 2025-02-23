from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, date
from typing import Dict, Optional
from pydantic import BaseModel
import logging

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
    logging.info("Login attempt for username: %s", form_data.username)
    
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logging.warning("Login failed for username: %s", form_data.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        logging.info("Login successful for username: %s", form_data.username)
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logging.error("Error during login for username %s: %s", form_data.username, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

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
    logging.info("Received registration request for username: %s", user_data.username)

    try:
        # Check if username already exists
        if db.query(User).filter(User.username == user_data.username).first():
            logging.warning("Username already registered: %s", user_data.username)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        if db.query(User).filter(User.email == user_data.email).first():
            logging.warning("Email already registered: %s", user_data.email)
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
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logging.info("User registered successfully: %s", new_user.username)

        # Create access token for the new user
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logging.error("Error during user registration: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=Dict[str, str])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return {
        "name": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "date_of_birth": current_user.date_of_birth.isoformat(),
        "address_line1": current_user.address_line1,
        "city": current_user.city,
        "state": current_user.state,
        "postal_code": current_user.postal_code,
        "country": current_user.country,
        "phone_number": current_user.phone_number
    }

