import stripe
import os
from typing import Dict, Optional

# Configure Stripe with your secret key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'your-test-key')

def create_cardholder(
    name: str,
    email: str,
    phone_number: str,
    address_line1: str,
    city: str,
    state: str,
    postal_code: str,
    country: str = 'US'
) -> Dict:
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
        return {"success": True, "cardholder": cardholder}
    except stripe.error.StripeError as e:
        return {"success": False, "error": str(e)}

def create_virtual_card(cardholder_id: str) -> Dict:
    """
    Create a new virtual card for a cardholder.
    
    Args:
        cardholder_id: The ID of the cardholder to create the card for
        
    Returns:
        Dict containing the created virtual card information or error details
    """
    try:
        card = stripe.issuing.Card.create(
            cardholder=cardholder_id,
            type='virtual',
            currency='usd',
            status='active'
        )
        return {"success": True, "card": card}
    except stripe.error.StripeError as e:
        return {"success": False, "error": str(e)}

def get_virtual_card(card_id: str) -> Dict:
    """
    Retrieve details of a specific virtual card.
    
    Args:
        card_id: The ID of the virtual card to retrieve
        
    Returns:
        Dict containing the virtual card information or error details
    """
    try:
        card = stripe.issuing.Card.retrieve(card_id)
        return {"success": True, "card": card}
    except stripe.error.StripeError as e:
        return {"success": False, "error": str(e)}
