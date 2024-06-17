import logging
import stripe
import os
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from ..models import PaymentStatus

from ..database import get_db
from ..schemas import PaymentCreate, Payment
from ..utils.auth import get_current_active_user
from ..schemas import User
from ..crud.payments import create_payment, update_payment_status
from ..crud.bookings import get_booking

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create-payment-intent", response_model=JSONResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a Stripe Payment Intent")
async def create_payment_intent(
        payment: PaymentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> JSONResponse:
    """
    Create a Stripe Payment Intent.

    Args:
        payment (PaymentCreate): The payment creation data.
        db (Session): The database session.
        current_user (User): The current active user.

    Returns:
        Any: The created Stripe Payment Intent.
    """
    try:
        db_booking = get_booking(db, payment.booking_id)
        if db_booking.payment_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Payment with this booking_id already exist.")
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=int(payment.amount * 100),  # Stripe expects the amount in cents
            currency="usd",
            metadata={"integration_check": "accept_a_payment"},
        )

        # Save the Payment information in the database
        db_payment = create_payment(db, payment)
        logger.info(f"PaymentIntent created: {intent['id']} for Booking ID: {payment.booking_id}")

        return JSONResponse({"client_secret": intent['client_secret']})
    except Exception as e:
        logger.error(f"Error creating PaymentIntent: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating PaymentIntent")


@router.post("/webhook", status_code=status.HTTP_200_OK, summary="Handle Stripe Webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe Webhook events.

    Args:
        request (Request): The request object.
        db (Session): The database session.

    Returns:
        Any: The response to the webhook event.
    """
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {e}")
        return JSONResponse({"error": "Invalid payload"}, status_code=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid signature: {e}")
        return JSONResponse({"error": "Invalid signature"}, status_code=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        logger.info(f"PaymentIntent was successful: {payment_intent['id']}")

        # Update payment status in the database
        payment_id = payment_intent['metadata'].get('payment_id')
        if payment_id:
            db_payment = update_payment_status(db, payment_id, PaymentStatus.COMPLETED)
            if db_payment:
                logger.info(f"Payment status updated to COMPLETED for payment ID: {payment_id}")
            else:
                logger.error(f"Payment not found for payment ID: {payment_id}")

    return JSONResponse({"status": "success"})
