from typing import Optional, List
import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..models import Seat, Booking, Reservation, ReservationStatus, SeatStatus, BookingStatus
from ..schemas import ReservationCreate
from .seats import update_seat_status

# Initialize logger
logger = logging.getLogger(__name__)

def create_reservation(db: Session, reservation: ReservationCreate) -> Reservation:
    """
    Create a new reservation for a seat.

    Args:
        db (Session): The database session.
        reservation (ReservationCreate): The reservation creation schema.

    Returns:
        Reservation: The created reservation.

    Raises:
        HTTPException: If the seat is already reserved.
    """
    logger.info(f"Creating a reservation for seat_id: {reservation.seat_id}")
    seat = db.query(Seat).filter(Seat.id == reservation.seat_id).one()
    if seat.status != SeatStatus.AVAILABLE:
        logger.error(f"Seat with id {reservation.seat_id} is already reserved")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seat is already reserved")

    db_reservation = Reservation(**reservation.dict())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    logger.info(f"Reservation created with id {db_reservation.id}")

    if db_reservation.booking.session.auto_booking:
        update_reservation_status(db, db_reservation.id, ReservationStatus.CONFIRMED)
    return db_reservation

def delete_reservation(db: Session, reservation_id: int) -> Reservation:
    """
    Delete a reservation by its ID.

    Args:
        db (Session): The database session.
        reservation_id (int): The ID of the reservation to delete.

    Returns:
        Reservation: The deleted reservation.
    """
    logger.info(f"Deleting reservation with id {reservation_id}")
    db_reservation = get_reservation(db, reservation_id)

    db.delete(db_reservation)
    db.commit()
    logger.info(f"Reservation with id {reservation_id} deleted")
    return db_reservation

def update_reservation_status(db: Session, reservation_id: int, new_status: ReservationStatus) -> Reservation:
    """
    Update the status of a reservation.

    Args:
        db (Session): The database session.
        reservation_id (int): The ID of the reservation to update.
        new_status (ReservationStatus): The new status of the reservation.

    Returns:
        Reservation: The updated reservation.

    Raises:
        HTTPException: If the new status is pending or if the reservation is canceled.
    """
    logger.info(f"Updating status of reservation id {reservation_id} to {new_status}")
    db_reservation = get_reservation(db, reservation_id)

    if new_status == ReservationStatus.PENDING:
        logger.error("Cannot change status to pending")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change status to pending")

    if db_reservation.status == ReservationStatus.CANCELED and new_status != ReservationStatus.CANCELED:
        logger.error("Cannot change status of canceled reservation")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change status of canceled reservation")

    if db_reservation.status == ReservationStatus.PENDING and new_status == ReservationStatus.CONFIRMED:
        update_seat_status(db, db_reservation.seat_id, SeatStatus.RESERVED)
    elif db_reservation.status == ReservationStatus.CONFIRMED and new_status == ReservationStatus.CANCELED:
        update_seat_status(db, db_reservation.seat_id, SeatStatus.AVAILABLE)

    db_reservation.status = new_status
    db.commit()
    logger.info(f"Status of reservation id {reservation_id} updated to {new_status}")
    return db_reservation

def get_reservation(db: Session, reservation_id: int) -> Reservation:
    """
    Retrieve a reservation by its ID.

    Args:
        db (Session): The database session.
        reservation_id (int): The ID of the reservation to retrieve.

    Returns:
        Reservation: The retrieved reservation.

    Raises:
        HTTPException: If the reservation is not found.
    """
    logger.info(f"Retrieving reservation with id {reservation_id}")
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not db_reservation:
        logger.error(f"Reservation with id {reservation_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    return db_reservation

def get_reservations(db: Session, skip: Optional[int] = None, limit: Optional[int] = None,
                     user_id: Optional[int] = None, booking_id: Optional[int] = None,
                     seat_id: Optional[int] = None, reservation_status: Optional[ReservationStatus] = None) -> List[Reservation]:
    """
    Retrieve a list of reservations with optional filters.

    Args:
        db (Session): The database session.
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.
        user_id (Optional[int]): Filter by user ID.
        booking_id (Optional[int]): Filter by booking ID.
        seat_id (Optional[int]): Filter by seat ID.
        reservation_status (Optional[ReservationStatus]): Filter by reservation status.

    Returns:
        List[Reservation]: A list of reservations.
    """
    logger.info(f"Retrieving reservations with filters - skip: {skip}, limit: {limit}, user_id: {user_id}, booking_id: {booking_id}, seat_id: {seat_id}, reservation_status: {reservation_status}")
    query = db.query(Reservation)

    if user_id is not None:
        query = query.filter(Reservation.booking.has(Booking.user_id == user_id))

    if booking_id is not None:
        query = query.filter(Reservation.booking_id == booking_id)

    if seat_id is not None:
        query = query.filter(Reservation.seat_id == seat_id)

    if reservation_status is not None:
        query = query.filter(Reservation.status == reservation_status)

    if limit is not None:
        query = query.limit(limit)

    if skip is not None:
        query = query.offset(skip)

    reservations = query.all()
    logger.info(f"Retrieved {len(reservations)} reservations")
    return reservations
