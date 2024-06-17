from sqlalchemy.orm import Session
from ..models import Payment, PaymentStatus
from ..schemas import PaymentCreate


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


def update_payment_status(db: Session, payment_id: str, new_status: PaymentStatus) -> Payment:
    """
    Update the status of a payment.

    Args:
        db (Session): The database session.
        payment_id (int): The ID of the payment to update.
        new_status (PaymentStatus): The new status to set.

    Returns:
        Payment: The updated payment record.
    """
    db_payment = get_payment(db, payment_id)
    db_payment.status = new_status
    db.commit()
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
