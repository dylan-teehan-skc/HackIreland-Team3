from flask import Blueprint, jsonify, request
from api.subscription_parser import load_data, preprocess_data, find_subscriptions
import json
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from .cardCreation import create_cardholder, create_virtual_card, get_virtual_card, create_test_card

# Create a specific blueprint for card-related operations
card_bp = Blueprint('cards', __name__)
api_bp = Blueprint('api', __name__)

# Set up logging
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()

class UploadedFile(db.Model):
    __tablename__ = 'uploaded_files'
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String, nullable=False)

    def __init__(self, file_path):
        self.file_path = file_path

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logger.error("No file part in the request")
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save the file to a temporary location
        file_id = str(UploadedFile.query.count() + 1)  # Simple ID generation
        file_path = f"temp_{file_id}.xlsx"
        file.save(file_path)

        # Store file metadata in the database
        new_file = UploadedFile(file_path=file_path)
        db.session.add(new_file)
        db.session.commit()

        logger.info(f"File uploaded successfully with ID {new_file.id}")
        return jsonify({"message": "File uploaded successfully", "file_id": new_file.id}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500

@api_bp.route('/subscriptions/<int:file_id>', methods=['GET'])
def get_subscriptions(file_id):
    try:
        uploaded_file = UploadedFile.query.get(file_id)
        if not uploaded_file:
            logger.error(f"File ID {file_id} not found")
            return jsonify({"error": "File ID not found"}), 404

        df = load_data(uploaded_file.file_path)
        
        if "Money Out" not in df.columns:
            logger.error("The 'Money Out' column is missing from the data")
            return jsonify({"error": "The 'Money Out' column is missing from the data."}), 400

        df = preprocess_data(df)
        if df.empty:
            logger.warning("No data to process")
            return jsonify({"error": "No data to process."}), 400

        subscriptions_json = find_subscriptions(df)
        logger.info(f"Subscriptions retrieved for file ID {file_id}")
        return jsonify(json.loads(subscriptions_json))
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error"}), 500

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