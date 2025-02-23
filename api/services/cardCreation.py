import stripe
import logging
from api.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_cardholder(name, email, phone_number, address_line1, city, state, postal_code, date_of_birth, full_legal_name, country='US'):
    logger.info(f"Creating new cardholder for {email}")
    try:
        cardholder_data = {
            'type': 'individual',
            'name': name,
            'email': email,
            'phone_number': phone_number,
            'billing': {
                'address': {
                    'line1': address_line1,
                    'city': city,
                    'state': state,
                    'postal_code': postal_code,
                    'country': country
                }
            }
        }

        # Add required individual data
        cardholder_data['individual'] = {
            'dob': {
                'year': date_of_birth.year,
                'month': date_of_birth.month,
                'day': date_of_birth.day
            },
            'first_name': full_legal_name['first_name'],
            'last_name': full_legal_name['last_name']
        }
        
        # Add optional middle name if provided
        if middle_name := full_legal_name.get('middle_name'):
            cardholder_data['individual']['middle_name'] = middle_name

        cardholder = stripe.issuing.Cardholder.create(**cardholder_data)
        
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

def create_virtual_card_for_user(user):
    logger.info(f"Creating virtual card for user: {user.email}")
    if not user.card_holder_id:
        logger.info("User does not have a cardholder ID. Creating a new cardholder.")
        ch_response = create_cardholder(
            name=f"{user.first_name} {user.last_name}",  # Use full name
            email=user.email,
            phone_number=user.phone_number,
            address_line1=user.address if user.address else "",
            city=user.location if user.location else "",
            state="",
            postal_code="",
            country="US"
        )
        if not ch_response.get("success"):
            return {"success": False, "error": "Failed to create cardholder."}
        user.card_holder_id = ch_response["cardholder"].id
        # TODO: persist the updated user in the database if necessary.
    return create_virtual_card(user.card_holder_id)