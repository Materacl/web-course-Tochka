from typing import Optional, List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status
import logging

from ..models import Session as SessionModel, Booking, Reservation, BookingStatus, ReservationStatus, SessionStatus
from ..schemas import BookingCreate

from .reservations import update_reservation_status, get_reservations

# Initialize logger
logger = logging.getLogger(__name__)

def create_booking(db: Session, booking: BookingCreate, user_id: int) -> Booking:
    """
    Create a new booking for a session.

    Args:
        db (Session): The database session.
        booking (BookingCreate): The booking creation schema.
        user_id (int): The ID of the user creating the booking.

    Returns:
        Booking: The created booking.

    Raises:
        HTTPException: If the session is not found or if the session status is not upcoming.
    """
    logger.info(f"Creating booking for session_id: {booking.session_id} and user_id: {user_id}")
    db_session = db.query(SessionModel).filter(SessionModel.id == booking.session_id).first()
    if not db_session:
        logger.error(f"Session with id {booking.session_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if db_session.status != SessionStatus.UPCOMING:
        logger.error(f"Cannot create booking for a session that is not upcoming. Session ID: {booking.session_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot create booking for a session that is not upcoming")

    db_booking = Booking(**booking.dict(), user_id=user_id)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    logger.info(f"Booking created with id {db_booking.id}")
    if db_session.auto_booking:
        update_booking_status(db, db_booking.id, BookingStatus.CONFIRMED)
    return db_booking

def delete_booking(db: Session, booking_id: int) -> Booking:
    """
    Delete a booking by its ID.

    Args:
        db (Session): The database session.
        booking_id (int): The ID of the booking to delete.

    Returns:
        Booking: The deleted booking.
    """
    logger.info(f"Deleting booking with id {booking_id}")
    db_booking = get_booking(db, booking_id)

    db.delete(db_booking)
    db.commit()
    logger.info(f"Booking with id {booking_id} deleted")
    return db_booking

def update_booking_status(db: Session, booking_id: int, new_status: BookingStatus) -> Booking:
    """
    Update the status of a booking.

    Args:
        db (Session): The database session.
        booking_id (int): The ID of the booking to update.
        new_status (BookingStatus): The new status of the booking.

    Returns:
        Booking: The updated booking.

    Raises:
        HTTPException: If the new status is pending or the booking is not found.
    """
    logger.info(f"Updating status of booking id {booking_id} to {new_status}")
    db_booking = get_booking(db, booking_id)
    if not db_booking:
        logger.error(f"Booking with id {booking_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if new_status == BookingStatus.PENDING:
        logger.error(f"Cannot change status of confirmed or canceled booking to pending. Booking ID: {booking_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot change status of confirmed or canceled booking to pending")
    
    db_booking.status = new_status
    if new_status == BookingStatus.CONFIRMED:
        for reservation in db_booking.reservations:
            update_reservation_status(db, reservation.id, ReservationStatus.CONFIRMED)
            canceled_reservations = get_reservations(db, seat_id=reservation.seat_id, reservation_status=ReservationStatus.PENDING)
            for canceled_reservation in canceled_reservations:
                update_booking_status(db, canceled_reservation.booking_id, BookingStatus.CANCELED)
    elif new_status == BookingStatus.CANCELED:
        for reservation in db_booking.reservations:
            update_reservation_status(db, reservation.id, ReservationStatus.CANCELED)

    db.commit()
    logger.info(f"Status of booking id {booking_id} updated to {new_status}")
    return db_booking

def get_booking(db: Session, booking_id: int) -> Booking:
    """
    Retrieve a booking by its ID.

    Args:
        db (Session): The database session.
        booking_id (int): The ID of the booking to retrieve.

    Returns:
        Booking: The retrieved booking.

    Raises:
        HTTPException: If the booking is not found.
    """
    logger.info(f"Retrieving booking with id {booking_id}")
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        logger.error(f"Booking with id {booking_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return db_booking

def get_bookings(db: Session, skip: Optional[int] = None, limit: Optional[int] = None,
                 user_id: Optional[int] = None, session_id: Optional[int] = None,
                 booking_status: Optional[BookingStatus] = None) -> List[Booking]:
    """
    Retrieve a list of bookings with optional filters.

    Args:
        db (Session): The database session.
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.
        user_id (Optional[int]): Filter by user ID.
        session_id (Optional[int]): Filter by session ID.
        booking_status (Optional[BookingStatus]): Filter by booking status.

    Returns:
        List[Booking]: A list of bookings.
    """
    logger.info(f"Retrieving bookings with filters - skip: {skip}, limit: {limit}, user_id: {user_id}, session_id: {session_id}, booking_status: {booking_status}")
    query = db.query(Booking)

    if user_id is not None:
        query = query.filter(Booking.user_id == user_id)

    if session_id is not None:
        query = query.filter(Booking.session_id == session_id)

    if booking_status is not None:
        query = query.filter(Booking.status == booking_status)

    if skip is not None:
        query = query.offset(skip)

    if limit is not None:
        query = query.limit(limit)

    bookings = query.all()
    logger.info(f"Retrieved {len(bookings)} bookings")
    return bookings
