from fastapi import APIRouter
from api.services.cardCreation import create_cardholder, create_virtual_card, get_virtual_card, create_test_card

router = APIRouter()

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

@router.post("/create-virtual-card")
async def create_virtual_card_endpoint(cardholder_id: str):
    result = create_virtual_card(cardholder_id)
    return result

@router.get("/virtual-card/{card_id}")
async def get_virtual_card_endpoint(card_id: str):
    result = get_virtual_card(card_id)
    return result

@router.post("/test-card")
async def test_card_endpoint():
    result = create_test_card()
    return result 