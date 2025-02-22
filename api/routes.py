from flask import Blueprint, jsonify, request
from . import api_bp
from .cardCreation import create_cardholder, create_virtual_card, get_virtual_card, create_test_card

# Create a specific blueprint for card-related operations
card_bp = Blueprint('cards', __name__)

@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "API is running"})

@card_bp.route('/create-cardholder', methods=['POST'])
def create_cardholder_endpoint():
    """Endpoint to create a new cardholder"""
    data = request.json
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
    return jsonify(result)

@card_bp.route('/create-virtual-card', methods=['POST'])
def create_virtual_card_endpoint():
    """Endpoint to create a new virtual card"""
    data = request.json
    cardholder_id = data.get('cardholder_id')
    if not cardholder_id:
        return jsonify({"success": False, "error": "cardholder_id is required"})
    
    result = create_virtual_card(cardholder_id)
    return jsonify(result)

@card_bp.route('/virtual-card/<card_id>', methods=['GET'])
def get_virtual_card_endpoint(card_id):
    """Endpoint to get virtual card details"""
    result = get_virtual_card(card_id)
    return jsonify(result)

@api_bp.route('/test-card', methods=['GET'])
def test_card_endpoint():
    """Endpoint to create a test card"""
    return jsonify(create_test_card())

# Register the card blueprint with the main API blueprint
api_bp.register_blueprint(card_bp, url_prefix='/cards')
