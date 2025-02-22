import stripe
import logging
from .config import get_settings

# Configure logger
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Configure Stripe with your secret key
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_cardholder(
    name: str,
    email: str,
    phone_number: str,
    address_line1: str,
    city: str,
    state: str,
    postal_code: str,
    country: str = 'US') -> dict:
    """
    Create a new cardholder in Stripe.
    
    Args:
        name: Full name of the cardholder
        email: Email address of the cardholder
        phone_number: Phone number of the cardholder
        address_line1: Street address of the cardholder
        city: City of the cardholder
        state: State/province of the cardholder
        postal_code: Postal code of the cardholder
        country: Country code (default: 'US')
        
    Returns:
        Dict containing the created cardholder information or error details
    """
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

def create_virtual_card(cardholder_id: str) -> dict:
    """
    Create a new virtual card for a cardholder.
    
    Args:
        cardholder_id: The ID of the cardholder to create the card for
        
    Returns:
        Dict containing the created virtual card information or error details
    """
    logger.info(f"Creating virtual card for cardholder: {cardholder_id}")
    try:
        if if_cardholder_has_cards(cardholder_id):
            logger.warning(f"Cardholder {cardholder_id} already has a card")
            return {"success": False, "error": "Cardholder already has a card"}

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

def get_virtual_card(card_id: str) -> dict:
    """
    Retrieve details of a specific virtual card.
    
    Args:
        card_id: The ID of the virtual card to retrieve
        
    Returns:
        Dict containing the virtual card information or error details
    """
    logger.info(f"Retrieving virtual card: {card_id}")
    try:
        card = stripe.issuing.Card.retrieve(card_id)
        logger.info(f"Successfully retrieved virtual card: {card_id}")
        return {"success": True, "card": card}
    except stripe.error.StripeError as e:
        logger.error(f"Failed to retrieve virtual card {card_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def create_test_card() -> dict:
    """Create a test virtual card with example values."""
    logger.info("Creating test card")
    # First test if a test cardholder already exists
    if not settings.TEST_CARDHOLDER_ID:
        logger.info("No test cardholder found, creating new one")
        cardholder_result = create_cardholder(
            name=settings.TEST_CARDHOLDER_NAME,
            email=settings.TEST_CARDHOLDER_EMAIL,
            phone_number=settings.TEST_CARDHOLDER_PHONE,
            address_line1=settings.TEST_CARDHOLDER_ADDRESS,
            city=settings.TEST_CARDHOLDER_CITY,
            state=settings.TEST_CARDHOLDER_STATE,
            postal_code=settings.TEST_CARDHOLDER_POSTAL,
            country=settings.TEST_CARDHOLDER_COUNTRY
        )

        if not cardholder_result["success"]:
            logger.error("Failed to create test cardholder")
            return cardholder_result
        
        # Note: We can't modify settings at runtime, so this ID needs to be saved elsewhere
        # or retrieved from the API if needed
        logger.info(f"Created test cardholder with ID: {cardholder_result['cardholder']['id']}")
        cardholder_id = cardholder_result["cardholder"]["id"]
    else:
        cardholder_id = settings.TEST_CARDHOLDER_ID
    
    # Then create a virtual card for this cardholder
    logger.info("Creating virtual card for test cardholder")
    card_result = create_virtual_card(cardholder_id)
    
    if not card_result["success"]:
        logger.error("Failed to create virtual card for test cardholder")
        return card_result
    
    logger.info("Successfully created test card")
    return {
        "success": True,
        "cardholder": {"id": cardholder_id},  # We might not have the full cardholder object
        "card": card_result["card"]
    }

def if_cardholder_has_cards(cardholder_id: str) -> bool:
    """Check if a cardholder has any cards."""
    logger.debug(f"Checking if cardholder {cardholder_id} has any cards")
    cards = stripe.issuing.Card.list(cardholder=cardholder_id)
    has_cards = len(cards.data) > 0
    if has_cards:
        logger.debug(f"Cardholder {cardholder_id} has existing cards")
    return has_cards
