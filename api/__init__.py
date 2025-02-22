from flask import Blueprint

# Create the main api blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')
