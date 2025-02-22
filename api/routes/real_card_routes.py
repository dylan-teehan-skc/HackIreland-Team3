from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from ..models import User, RealCard
from ..auth import require_auth
from .. import db

real_card_routes = Blueprint('real_card_routes', __name__)

@real_card_routes.route('/real-cards', methods=['POST'])
@require_auth
def add_real_card():
    """Add a real card to user's account"""
    data = request.get_json()
    current_user = request.user
    
    # Check if user already has a real card
    if current_user.real_card:
        return jsonify({'error': 'User already has a real card registered'}), 400
    
    try:
        # Create new real card
        real_card = RealCard(
            card_number=data['card_number'],
            card_holder_name=data['card_holder_name'],
            expiry_date=data['expiry_date']
        )
        db.session.add(real_card)
        db.session.flush()  # Get the real card ID
        
        # Associate with user
        current_user.real_card_id = real_card.id
        db.session.commit()
        
        return jsonify({
            'message': 'Real card added successfully',
            'card_holder_name': real_card.card_holder_name
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Failed to add real card'}), 400

@real_card_routes.route('/real-cards', methods=['GET'])
@require_auth
def get_real_card():
    """Get user's real card information"""
    current_user = request.user
    
    if not current_user.real_card:
        return jsonify({'error': 'No real card found'}), 404
        
    return jsonify({
        'card_holder_name': current_user.real_card.card_holder_name,
        'card_number': '****' + current_user.real_card.card_number[-4:],  # Only show last 4 digits
        'expiry_date': current_user.real_card.expiry_date
    }), 200

@real_card_routes.route('/real-cards', methods=['DELETE'])
@require_auth
def remove_real_card():
    """Remove user's real card"""
    current_user = request.user
    
    if not current_user.real_card:
        return jsonify({'error': 'No real card found'}), 404
    
    try:
        # Check if user is part of any groups
        if current_user.card_memberships:
            return jsonify({
                'error': 'Cannot remove card while member of groups. Leave all groups first.'
            }), 400
        
        # Remove the real card
        db.session.delete(current_user.real_card)
        current_user.real_card_id = None
        db.session.commit()
        
        return jsonify({'message': 'Real card removed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
