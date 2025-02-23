import os
from flask import Flask, jsonify, request, render_template
import stripe
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Initialize Stripe with your secret key
    api_key = os.getenv('STRIPE_SECRET_KEY')
    if not api_key:
        raise ValueError("Stripe API key not found in environment")
    stripe.api_key = api_key

    @app.route('/')
    def index():
        return render_template('index.html', stripe_public_key=os.getenv('STRIPE_PUBLIC_KEY'))

    @app.route('/create-payment-intent', methods=['POST'])
    def create_payment():
        try:
            # Create a PaymentIntent with the amount
            payment_intent = stripe.PaymentIntent.create(
                amount=int(199.99*100),  # Amount in cents (e.g., $19.99)
                currency='usd',
                payment_method_types=['card'],
                metadata={'integration_check': 'accept_a_payment'},
            )
            return jsonify({'clientSecret': payment_intent.client_secret})
        except Exception as e:
            print(e)
            return jsonify(error=str(e)), 403

    @app.route('/webhook', methods=['POST'])
    def webhook():
        event = None
        payload = request.data

        try:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
        except ValueError as e:
            return jsonify({'error': 'Invalid payload'}), 400

        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            print('Payment succeeded:', payment_intent.id)
        
        return jsonify({'status': 'success'})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=4000)
