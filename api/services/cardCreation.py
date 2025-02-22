import stripe
import logging
from api.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_cardholder(name, email, phone_number, address_line1, city, state, postal_code, country='US'):
    logger.info(f"Creating new cardholder for {email}")
    try:
        cardholder = stripe.issuing.Cardholder.create(
            type='individual',
            name=name,
            email=email,
            phone_number=phone_number,
            billing={
                'address': {
                    'line1': address_line1,
                    'city': city,
                    'state': state,
                    'postal_code': postal_code,
                    'country': country
                }
            }
        )
        logger.info(f"Successfully created cardholder with ID: {cardholder.id}")
        return {"success": True, "cardholder": cardholder}
    except stripe.error.StripeError as e:
        logger.error(f"Failed to create cardholder for {email}: {str(e)}")
        return {"success": False, "error": str(e)}

def create_virtual_card(cardholder_id):
    logger.info(f"Creating virtual card for cardholder: {cardholder_id}")
    try:
        card = stripe.issuing.Card.create(
            cardholder=cardholder_id,
            type='virtual',
            currency='eur',
            status='active'
        )
        logger.info(f"Successfully created virtual card with ID: {card.id}")
        return {"success": True, "card": card}
    except stripe.error.StripeError as e:
        logger.error(f"Failed to create virtual card for cardholder {cardholder_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_virtual_card(card_id):
    logger.info(f"Retrieving virtual card: {card_id}")
    try:
        card = stripe.issuing.Card.retrieve(card_id)
        logger.info(f"Successfully retrieved virtual card: {card_id}")
        return {"success": True, "card": card}
    except stripe.error.StripeError as e:
        logger.error(f"Failed to retrieve virtual card {card_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def create_test_card():
    logger.info("Creating test card")
    cardholder_id = "test_cardholder_id"  # Replace with actual test cardholder ID
    card_result = create_virtual_card(cardholder_id)
    if not card_result["success"]:
        logger.error("Failed to create virtual card for test cardholder")
        return card_result
    logger.info("Successfully created test card")
    return {
        "success": True,
        "cardholder": {"id": cardholder_id},
        "card": card_result["card"]
    } 