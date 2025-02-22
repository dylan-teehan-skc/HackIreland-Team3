from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from ..models import User, Group, VirtualCard, CardMember, RealCard
from ..auth import require_auth
from .. import db

group_routes = Blueprint('group_routes', __name__)

@group_routes.route('/groups', methods=['POST'])
@require_auth
def create_group():
    """Create a new group and associated virtual card"""
    data = request.get_json()
    current_user = request.user  # Set by require_auth decorator
    
    # Check if user has a real card
    if not current_user.real_card:
        return jsonify({'error': 'You must add a real card before creating a group'}), 400
    
    try:
        # Create the group
        new_group = Group(
            name=data['name'],
            admin_id=current_user.id
        )
        db.session.add(new_group)
        db.session.flush()  # Get the group ID
        
        # Create associated virtual card
        virtual_card = VirtualCard(
            virtual_card_id=f"V-{new_group.id}",  # Simple virtual card ID format
            group_id=new_group.id
        )
        db.session.add(virtual_card)
        
        # Add admin as first member
        member = CardMember(
            card_id=virtual_card.id,
            user_id=current_user.id
        )
        db.session.add(member)
        
        db.session.commit()
        return jsonify({
            'message': 'Group created successfully',
            'group_id': new_group.id,
            'virtual_card_id': virtual_card.virtual_card_id
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Group creation failed'}), 400

@group_routes.route('/groups/<int:group_id>/join', methods=['POST'])
@require_auth
def join_group():
    """Join an existing group"""
    current_user = request.user
    group_id = request.view_args['group_id']
    
    # Check if user has a real card
    if not current_user.real_card:
        return jsonify({'error': 'You must add a real card before joining a group'}), 400
    
    try:
        # Check if group exists
        group = Group.query.get(group_id)
        if not group:
            return jsonify({'error': 'Group not found'}), 404
            
        # Check if user is already a member
        existing_membership = CardMember.query.join(VirtualCard).filter(
            VirtualCard.group_id == group_id,
            CardMember.user_id == current_user.id
        ).first()
        
        if existing_membership:
            return jsonify({'error': 'Already a member of this group'}), 400
            
        # Add user as member
        virtual_card = VirtualCard.query.filter_by(group_id=group_id).first()
        member = CardMember(
            card_id=virtual_card.id,
            user_id=current_user.id
        )
        db.session.add(member)
        db.session.commit()
        
        return jsonify({'message': 'Successfully joined group'}), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Failed to join group'}), 400

@group_routes.route('/groups/<int:group_id>/members', methods=['GET'])
@require_auth
def get_group_members(group_id):
    """Get all members of a group"""
    try:
        # Check if group exists and user is a member
        group = Group.query.get(group_id)
        if not group:
            return jsonify({'error': 'Group not found'}), 404
            
        # Get all members
        members = User.query.join(CardMember).join(VirtualCard).filter(
            VirtualCard.group_id == group_id
        ).all()
        
        return jsonify({
            'members': [{
                'id': member.id,
                'name': member.name,
                'email': member.email,
                'is_admin': member.id == group.admin_id
            } for member in members]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@group_routes.route('/user/groups', methods=['GET'])
@require_auth
def get_user_groups():
    """Get all groups a user is a member of"""
    current_user = request.user
    
    try:
        # Get all groups user is a member of
        groups = Group.query.join(VirtualCard).join(CardMember).filter(
            CardMember.user_id == current_user.id
        ).all()
        
        return jsonify({
            'groups': [{
                'id': group.id,
                'name': group.name,
                'is_admin': group.admin_id == current_user.id,
                'virtual_card_id': group.virtual_card.virtual_card_id
            } for group in groups]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
