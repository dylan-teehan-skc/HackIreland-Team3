from flask import Blueprint, jsonify, request
import os
from . import api_bp
from stripe_utils import create_cardholder, create_virtual_card, get_virtual_card
import stripe

# Create a specific blueprint for card-related operations
card_bp = Blueprint('cards', __name__)

# Configure Stripe with your secret key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_51QvI5hG3Gk8hJB4vXcNCEMt78KSxvnY2f39CVnn50f9B5jHDw3w5PIfcMoJkBKJKrIECwC405nWJ7ImQ2gK4z1Jd00sKGAtR43')


@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "API is running"})


@card_bp.route('/cardholders', methods=['POST'])
def create_cardholder_endpoint():
    """Create a new cardholder for issuing virtual cards"""
    data = request.get_json()
    
    result = create_cardholder(
        name=data.get('name'),
        email=data.get('email'),
        phone_number=data.get('phone_number'),
        address_line1=data.get('address_line1'),
        city=data.get('city'),
        state=data.get('state'),
        postal_code=data.get('postal_code'),
        country=data.get('country', 'US')
    )
    
    if not result['success']:
        return jsonify(result), 400
    return jsonify(result)

@card_bp.route('/virtual-cards', methods=['POST'])
def create_virtual_card_endpoint():
    """Create a new virtual card for a cardholder"""
    data = request.get_json()
    
    result = create_virtual_card(cardholder_id=data.get('cardholder_id'))
    
    if not result['success']:
        return jsonify(result), 400
    return jsonify(result)

@card_bp.route('/virtual-cards/<card_id>', methods=['GET'])
def get_virtual_card_endpoint(card_id):
    """Retrieve a virtual card's details"""
    result = get_virtual_card(card_id=card_id)
    
    if not result['success']:
        return jsonify(result), 400
    return jsonify(result)

@card_bp.route('/test-card', methods=['POST'])
def create_test_card():
    """Create a test virtual card with example values"""
    # First create a cardholder with example values
    cardholder_result = create_cardholder(
        name='John Doe',
        email='john.doe@example.com',
        phone_number='+1234567890',
        address_line1='123 Main St',
        city='San Francisco',
        state='CA',
        postal_code='94105',
        country='US'
    )
    
    if not cardholder_result['success']:
        return jsonify(cardholder_result), 400
        
    # Create a virtual card for the cardholder
    card_result = create_virtual_card(cardholder_id=cardholder_result['cardholder']['id'])
    
    if not card_result['success']:
        return jsonify(card_result), 400
        
    return jsonify({
        'success': True,
        'cardholder': cardholder_result['cardholder'],
        'card': card_result['card']
    })

# Register the card blueprint with the main API blueprint
api_bp.register_blueprint(card_bp)
