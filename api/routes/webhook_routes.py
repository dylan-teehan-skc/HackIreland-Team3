from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from api.config.settings import get_settings
import stripe
from api.database import get_db
from sqlalchemy.orm import Session
from api.models import User, Group, VirtualCard, CardMember, RealCard
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"]
)

@router.post("/stripeWebhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint for stripe webhooks, **not to be used directly!!**
    """
    logger.info("Received Stripe webhook request")
    
    # Get the raw request body
    payload = await request.body()
    payload_str = payload.decode('utf-8')
    sig_header = request.headers.get("stripe-signature")
    
    # Log request details
    logger.debug(f"Request content type: {request.headers.get('content-type')}")
    logger.debug(f"Payload (first 100 chars): {payload_str[:100]}...")
    
    logger.debug(f"Webhook Headers: {dict(request.headers)}")
    logger.debug(f"Stripe-Signature: {sig_header}")
    
    if not sig_header:
        logger.error("No stripe-signature header found")
        raise HTTPException(status_code=400, detail="No stripe-signature header")
    
    webhook_secret = get_settings().STRIPE_WEBHOOK_SECRET
    logger.debug(f"Using webhook secret: {webhook_secret[:6]}...")
    
    # Verify the secret is properly loaded
    if not webhook_secret:
        logger.error("Webhook secret is empty!")
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    # Log signature components
    if sig_header:
        sig_parts = sig_header.split(',')
        logger.debug(f"Signature parts: {len(sig_parts)}")
        for part in sig_parts:
            logger.debug(f"Signature part: {part[:10]}...")
    
    try:
        # Verify the webhook signature
        logger.debug("Attempting to construct Stripe event")
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        logger.info(f"Successfully verified Stripe webhook signature. Event type: {event.type}")
    except ValueError as e:
        logger.error(f"Invalid payload error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Signature verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")

    # Handle the event
    if event.type == "issuing_authorization.request":
        authorization = event.data.object
        # Example logic: Approve if the amount is less than a threshold
        approval_threshold = 10_000_000_000_000  # Amount in smallest currency unit (e.g., cents)
        is_approved = authorization.pending_request['amount'] < approval_threshold
        
        # Respond to the webhook with approval or decline
        response = JSONResponse(
            status_code=200,
            content={"approved": is_approved}
        )
        # Add Stripe API version header
        response.headers["Stripe-Version"] = stripe.api_version
        response.headers["Content-Type"] = "application/json"
        return response

    elif event.type == "issuing_authorization.created":
        authorization = event.data.object
        # Handle virtual card transaction authorization
        print(f"Processing authorization for card: {authorization.card.id}")
        # TODO: Implement your business logic here
        # For example:
        # - Log the transaction
        # - Update transaction records
        # - Send notifications

    elif event.type == "issuing_transaction.created":
        transaction = event.data.object
        logger.info(f"Processing transaction: {transaction.id}")
        
        try:
            # Get the virtual card ID from the transaction
            virtual_card_id = transaction.card
            
            # Find the virtual card in our database
            virtual_card = db.query(VirtualCard).filter(VirtualCard.virtual_card_id == virtual_card_id).first()
            if not virtual_card:
                logger.error(f"Virtual card {virtual_card_id} not found in database")
                raise HTTPException(status_code=404, detail="Virtual card not found")
            
            # Get the group associated with the virtual card
            group = virtual_card.group
            if not group:
                logger.error(f"No group found for virtual card {virtual_card_id}")
                raise HTTPException(status_code=404, detail="Group not found")
            
            # Get all users in the group through the virtual card's card_members
            group_members = [member.user for member in virtual_card.card_members]
            
            if not group_members:
                logger.error(f"No group members with real cards found for group {group.id}")
                raise HTTPException(status_code=400, detail="No group members with real cards found")
            
            # Calculate split amount (handle both positive and negative amounts)
            transaction_amount = abs(transaction.amount)  # Amount in smallest currency unit (cents)
            split_amount = transaction_amount // len(group_members)  # Integer division
            remainder = transaction_amount % len(group_members)  # Handle any remainder
            
            logger.info(f"Splitting transaction {transaction.id} amount {transaction_amount} among {len(group_members)} members")
            
            # Create payments to each member's real card
            for i, member in enumerate(group_members):
                # Add remainder to first member's payment to handle any rounding
                payment_amount = split_amount + (remainder if i == 0 else 0)
                
                try:
                    # First create a PaymentMethod with the card details
                    payment_method = stripe.PaymentMethod.create(
                        type='card',
                        card={
                            'number': member.real_card.card_number,
                            'exp_month': int(member.real_card.expiry_date.split('/')[0]),
                            'exp_year': int(member.real_card.expiry_date.split('/')[1]),
                            'name': member.real_card.card_holder_name,
                            'cvc': member.real_card.cvc
                        }
                    )
                    print(payment_method)
                    print(payment_method.id)

                    # Create a PaymentIntent and attach the PaymentMethod
                    payment_intent = stripe.PaymentIntent.create(
                        amount=payment_amount,  # amount in cents
                        currency='eur',
                        payment_method=payment_method.id,
                        confirm=True,  # Confirm the payment immediately
                        description=f'Split payment for transaction {transaction.id}',
                        metadata={
                            'transaction_id': transaction.id,
                            'user_id': member.id
                        }
                    )
                    
                    logger.info(f"Successfully charged user {member.id} amount {payment_amount}")

                    
                except stripe.error.StripeError as e:
                    logger.error(f"Failed to create payment for user {member.id}: {str(e)}")
                    # Continue processing other payments even if one fails
                    continue
            
        except Exception as e:
            logger.error(f"Error processing transaction {transaction.id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing transaction: {str(e)}")
    
    return {"status": "success"}
