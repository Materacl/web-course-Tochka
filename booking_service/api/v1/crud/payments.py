import logging
from typing import Optional, List

from sqlalchemy.orm import Session
from ..models import Payment, PaymentStatus
from ..schemas import PaymentCreate

logger = logging.getLogger(__name__)


def create_payment(db: Session, payment_data: PaymentCreate, amount: int) -> Payment:
    """
    Create a new payment record in the database.

    Args:
        db (Session): The database session.
        payment_data (PaymentCreate): The payment creation data.

    Returns:
        Payment: The created payment record.
    """
    db_payment = Payment(
        id=payment_data.id,
        booking_id=payment_data.booking_id,
        amount=amount,
        status=PaymentStatus.PENDING
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


from datetime import datetime, timedelta, timezone


def update_payment_status(db: Session, payment_id: str, new_status: Optional[PaymentStatus] = None) -> Payment:
    """
    Update the status of a payment. If no status is provided, set the status to FAILED if the payment timestamp was more than 10 minutes ago.

    Args:
        db (Session): The database session.
        payment_id (str): The ID of the payment to update.
        new_status (PaymentStatus, optional): The new status to set. Defaults to None.

    Returns:
        Payment: The updated payment record.
    """
    db_payment = get_payment(db, payment_id)
    if new_status:
        db_payment.status = new_status
    else:
        if db_payment.status is PaymentStatus.PENDING and db_payment.timestamp < datetime.now(timezone.utc) - timedelta(minutes=10):
            db_payment.status = PaymentStatus.FAILED

    db.commit()
    db.refresh(db_payment)
    return db_payment


def get_payment(db: Session, payment_id: str) -> Payment:
    """
    Retrieve a payment record by ID.

    Args:
        db (Session): The database session.
        payment_id (int): The ID of the payment to retrieve.

    Returns:
        Payment: The retrieved payment record.

    Raises:
        Exception: If the payment is not found.
    """
    db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if db_payment is None:
        raise Exception("Payment not found")
    return db_payment


def get_payments(db: Session, skip: Optional[int] = None, limit: Optional[int] = None,
                 booking_id: Optional[int] = None) -> List[Payment]:
    """
    Retrieve a list of payments with optional filters.

    Args:
        db (Session): The database session.
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.
        payment_id (int): The ID of the payment to retrieve.

    Returns:
        List[Payment]: A list of payments.
    """
    logger.info(
        f"Retrieving payments with filters - skip: {skip}, limit: {limit}, booking_id: {booking_id}")
    query = db.query(Payment)

    if booking_id is not None:
        query = query.filter(Payment.booking_id == booking_id)

    if skip is not None:
        query = query.offset(skip)

    if limit is not None:
        query = query.limit(limit)

    payments = query.all()
    logger.info(f"Retrieved {len(payments)} payments")
    return payments
