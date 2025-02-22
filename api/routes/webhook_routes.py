from fastapi import APIRouter, Request, HTTPException, Depends
from api.config.settings import get_settings
import stripe
from api.database import get_db
from sqlalchemy.orm import Session
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
    if event.type == "issuing_authorization.created":
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
        # Handle completed transaction
        print(f"Processing transaction: {transaction.id}")
        # TODO: Implement your business logic here
        
    return {"status": "success"}
