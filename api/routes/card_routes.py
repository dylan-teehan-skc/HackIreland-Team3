from fastapi import APIRouter, Depends, HTTPException, status
from api.services.cardCreation import create_cardholder, create_virtual_card, get_virtual_card, create_test_card, create_virtual_card_for_user
from api.auth import get_current_active_user, get_db
from sqlalchemy.orm import Session
from api.models.user import User

router = APIRouter(
    prefix="/cards",
    tags=["Cards"],
    responses={404: {"description": "Not found"}}
)

@router.post("/create-cardholder")
async def create_cardholder_endpoint(
    name: str,
    email: str,
    phone_number: str,
    address_line1: str,
    city: str,
    state: str,
    postal_code: str,
    country: str = "US"
):
    result = create_cardholder(
        name=name,
        email=email,
        phone_number=phone_number,
        address_line1=address_line1,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country
    )
    return result

@router.post("/create-virtual-card", status_code=status.HTTP_201_CREATED)
async def create_virtual_card_endpoint(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Refresh current user to ensure we have latest state
    current_user = db.merge(current_user)
    db.refresh(current_user)
    
    result = create_virtual_card_for_user(current_user)
    
    if result.get("success"):
        # If card was created successfully, update the user in database
        db.commit()
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to create virtual card")
        )

@router.get("/virtual-card/{card_id}")
async def get_virtual_card_endpoint(card_id: str):
    result = get_virtual_card(card_id)
    return result

@router.post("/test-card")
async def test_card_endpoint():
    result = create_test_card()
    return result 