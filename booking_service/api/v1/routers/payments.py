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
from ..crud.payments import create_payment, update_payment_status, get_payment, get_payments
from ..crud.bookings import get_booking
from ..crud.sessions import get_session

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


@router.post("/create-checkout-session", response_model=dict, status_code=status.HTTP_201_CREATED,
             summary="Create a Stripe Checkout Session")
async def create_checkout_session(
        payment: PaymentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Create a Stripe Checkout Session.

    Args:
        payment (PaymentCreate): The payment creation data.
        db (Session): The database session.
        current_user (User): The current active user.

    Returns:
        Any: The created Stripe Checkout Session URL.
    """
    try:
        db_booking = get_booking(db, payment.booking_id)
        if db_booking.payments:
            for current_payment in db_booking.payments:
                if current_payment.status in [PaymentStatus.PENDING, PaymentStatus.COMPLETED]:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="Payment with this booking_id already exist.")
        db_session = get_session(db, db_booking.session_id)
        if not db_session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Session for this payment is not found.")
        amount = int(db_session.price * len(db_booking.reservations) * 100)

        # Create a Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"Booking {payment.booking_id}",
                    },
                    'unit_amount': amount,  # Stripe expects the amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{os.getenv('FRONTEND_URL')}/sessions/{db_booking.session_id}",
            cancel_url=f"{os.getenv('FRONTEND_URL')}/sessions/{db_booking.session_id}",
            metadata={"booking_id": payment.booking_id}
        )

        # Save the Payment information in the database
        payment.id = session["id"]
        db_payment = create_payment(db, payment, amount)
        logger.info(f"Checkout Session created: {session['id']} for Booking ID: {db_payment.booking_id}")

        return {"checkout_url": session.url}
    except Exception as e:
        logger.error(f"Error creating Checkout Session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating Checkout Session")


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

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        logger.info(f"Checkout Session was successful: {session['id']}")

        # Update payment status in the database
        payment_id = session["id"]
        if payment_id:
            db_payment = update_payment_status(db, payment_id, PaymentStatus.COMPLETED)
            if db_payment:
                logger.info(f"Payment status updated to COMPLETED for payment ID: {payment_id}")
            else:
                logger.error(f"Payment not found for payment ID: {payment_id}")

    return JSONResponse({"status": "success"})
