from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from api.config.settings import get_settings
import stripe
from api.database import get_db
from sqlalchemy.orm import Session
from api.models import User, Group, VirtualCard, CardMember, RealCard, GroupMemberRatio
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
        logger.info(f"Processing authorization for card: {authorization.card.id}")
        
        try:
            # Get the virtual card associated with this authorization
            virtual_card = db.query(VirtualCard).filter(VirtualCard.virtual_card_id == authorization.card.id).first()
            if not virtual_card:
                logger.error(f"No virtual card found for stripe card {authorization.card.id}")
                raise HTTPException(status_code=404, detail="Virtual card not found")
            
            # Get the group associated with this virtual card
            group = db.query(Group).filter(Group.id == virtual_card.group_id).first()
            if not group:
                logger.error(f"No group found for virtual card {virtual_card.id}")
                raise HTTPException(status_code=404, detail="Group not found")
            
            # Get all group members with real cards
            group_members = db.query(User).join(CardMember).filter(
                CardMember.card_id == virtual_card.id,  # Join through card_id
                User.real_card_id.isnot(None)
            ).all()
            
            if not group_members:
                logger.error(f"No group members with real cards found for group {group.id}")
                raise HTTPException(status_code=400, detail="No group members with real cards found")
            
            # Get the group ratios
            group_ratios = db.query(GroupMemberRatio).filter(
                GroupMemberRatio.group_id == group.id
            ).all()
            
            # If no ratios exist, calculate equal split
            if not group_ratios:
                split_percentage = 100.0 / len(group_members)
                group_ratios = [
                    GroupMemberRatio(
                        group_id=group.id,
                        user_id=member.id,
                        ratio_percentage=split_percentage
                    ) for member in group_members
                ]
                
            # Calculate payments based on ratios
            auth_amount = authorization.amount  # Amount in smallest currency unit (cents)
            remainder = auth_amount  # Keep track of remaining amount to handle rounding
            
            logger.info(f"Splitting authorization {authorization.id} amount {auth_amount} according to group ratios")
            
            # Create payments to each member's real card
            for i, member in enumerate(group_members):
                # Find the ratio for this member
                member_ratio = next((ratio for ratio in group_ratios if ratio.user_id == member.id), None)
                if not member_ratio:
                    logger.error(f"No ratio found for member {member.id}")
                    continue
                
                # Calculate payment amount based on ratio
                if i == len(group_members) - 1:
                    # Last member gets the remainder to avoid rounding issues
                    payment_amount = remainder
                else:
                    payment_amount = int((auth_amount * member_ratio.ratio_percentage) / 100)
                    remainder -= payment_amount
                
                try:
                    # Get the customer's payment method ID from their real card
                    if not member.real_card or not member.real_card.stripe_payment_method_id:
                        logger.error(f"No valid payment method found for user {member.id}")
                        raise HTTPException(status_code=400, detail=f"No valid payment method for user {member.id}")
                    
                    # Create a PaymentIntent with the specific payment method
                    payment_intent = stripe.PaymentIntent.create(
                        amount=payment_amount,  # amount in cents
                        currency=authorization.currency,  # Use same currency as authorization
                        customer=member.stripe_customer_id,
                        payment_method=member.real_card.stripe_payment_method_id,
                        payment_method_types=['card'],  # Explicitly only allow card payments
                        confirm=True,  # Confirm the payment immediately
                        off_session=True,  # Indicate this is a background payment
                        description=f'Split payment for authorization {authorization.id}',
                        metadata={
                            'authorization_id': authorization.id,
                            'user_id': member.id
                        }
                    )
                    
                    logger.info(f"Successfully charged user {member.id} amount {payment_amount} for authorization {authorization.id}")
                except Exception as e:
                    logger.error(f"Failed to create payment for user {member.id}: {str(e)}")
                    raise HTTPException(status_code=400, detail=str(e))
                    
        except Exception as e:
            logger.error(f"Error processing authorization {authorization.id}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    elif event.type == "issuing_transaction.created":
        transaction = event.data.object
        logger.info(f"Received transaction: {transaction.id}")
        # Transaction event is now just for logging since we process payments at authorization time
        
        # # try:
        # #     # Get the virtual card ID from the transaction
        # #     virtual_card_id = transaction.card
            
        # #     # Find the virtual card in our database
        # #     virtual_card = db.query(VirtualCard).filter(VirtualCard.virtual_card_id == virtual_card_id).first()
        # #     if not virtual_card:
        # #         logger.error(f"Virtual card {virtual_card_id} not found in database")
        # #         raise HTTPException(status_code=404, detail="Virtual card not found")
            
        # #     # Get the group associated with the virtual card
        # #     group = virtual_card.group
        # #     if not group:
        # #         logger.error(f"No group found for virtual card {virtual_card_id}")
        # #         raise HTTPException(status_code=404, detail="Group not found")
            
        # #     # Get all users in the group through the virtual card's card_members
        # #     group_members = [member.user for member in virtual_card.card_members]
            
        # #     if not group_members:
        # #         logger.error(f"No group members with real cards found for group {group.id}")
        # #         raise HTTPException(status_code=400, detail="No group members with real cards found")
            
        # #     # Calculate split amount (handle both positive and negative amounts)
        # #     transaction_amount = abs(transaction.amount)  # Amount in smallest currency unit (cents)
        # #     split_amount = transaction_amount // len(group_members)  # Integer division
        # #     remainder = transaction_amount % len(group_members)  # Handle any remainder
            
        # #     logger.info(f"Splitting transaction {transaction.id} amount {transaction_amount} among {len(group_members)} members")
            
        # #     # Create payments to each member's real card
        # #     for i, member in enumerate(group_members):
        # #         # Add remainder to first member's payment to handle any rounding
        # #         payment_amount = split_amount + (remainder if i == 0 else 0)
                
        # #         try:
        # #             # Get the customer's payment method ID from their real card
        # #             if not member.real_card or not member.real_card.stripe_payment_method_id:
        # #                 logger.error(f"No valid payment method found for user {member.id}")
        # #                 raise HTTPException(status_code=400, detail=f"No valid payment method for user {member.id}")
                    
        # #             # Create a PaymentIntent with the specific payment method
        # #             payment_intent = stripe.PaymentIntent.create(
        # #                 amount=payment_amount,  # amount in cents
        # #                 currency='eur',
        # #                 customer=member.stripe_customer_id,
        # #                 payment_method=member.real_card.stripe_payment_method_id,
        # #                 payment_method_types=['card'],  # Explicitly only allow card payments
        # #                 confirm=True,  # Confirm the payment immediately
        # #                 off_session=True,  # Indicate this is a background payment
        # #                 description=f'Split payment for transaction {transaction.id}',
        # #                 metadata={
        # #                     'transaction_id': transaction.id,
        # #                     'user_id': member.id
        # #                 }
        # #             )
                    
        # #             logger.info(f"Successfully charged user {member.id} amount {payment_amount}")

                    
        # #         except stripe.error.StripeError as e:
        # #             logger.error(f"Failed to create payment for user {member.id}: {str(e)}")
        # #             # Continue processing other payments even if one fails
        # #             continue
            
        # except Exception as e:
        #     logger.error(f"Error processing transaction {transaction.id}: {str(e)}")
        #     raise HTTPException(status_code=500, detail=f"Error processing transaction: {str(e)}")

    
    return {"status": "success"}
