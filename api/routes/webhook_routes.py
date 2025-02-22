from fastapi import APIRouter, Request, HTTPException, Depends
from api.config.settings import get_settings
import stripe
from api.database import get_db
from sqlalchemy.orm import Session
import json

router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"]
)

@router.post("/stripeWebhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint for stripe webhooks, **not to be used directly!!**
    """
    # Get the raw request body
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        # Verify the webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, get_settings().STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

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
