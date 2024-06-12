from typing import Optional, List
import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..models import Seat, SeatStatus
from ..schemas import SeatCreate

# Initialize logger
logger = logging.getLogger(__name__)

def create_seat(db: Session, seat: SeatCreate) -> Seat:
    """
    Create a new seat.

    Args:
        db (Session): The database session.
        seat (SeatCreate): The seat creation schema.

    Returns:
        Seat: The created seat.
    """
    logger.info(f"Creating a new seat for session_id: {seat.session_id}")
    db_seat = Seat(**seat.dict())
    db.add(db_seat)
    db.commit()
    db.refresh(db_seat)
    logger.info(f"Seat created with id {db_seat.id}")
    return db_seat

def delete_seat(db: Session, seat_id: int) -> Seat:
    """
    Delete a seat by its ID.

    Args:
        db (Session): The database session.
        seat_id (int): The ID of the seat to delete.

    Returns:
        Seat: The deleted seat.
    """
    logger.info(f"Deleting seat with id {seat_id}")
    db_seat = get_seat(db, seat_id)

    db.delete(db_seat)
    db.commit()
    logger.info(f"Seat with id {seat_id} deleted")
    return db_seat

def update_seat_status(db: Session, seat_id: int, new_status: SeatStatus) -> Seat:
    """
    Update the status of a seat.

    Args:
        db (Session): The database session.
        seat_id (int): The ID of the seat to update.
        new_status (SeatStatus): The new status of the seat.

    Returns:
        Seat: The updated seat.
    """
    logger.info(f"Updating status of seat id {seat_id} to {new_status}")
    db_seat = get_seat(db, seat_id)

    if db_seat.status != SeatStatus.CANCELED:
        db_seat.status = new_status

    db.commit()
    logger.info(f"Status of seat id {seat_id} updated to {new_status}")
    return db_seat

def get_seat(db: Session, seat_id: int) -> Seat:
    """
    Retrieve a seat by its ID.

    Args:
        db (Session): The database session.
        seat_id (int): The ID of the seat to retrieve.

    Returns:
        Seat: The retrieved seat.

    Raises:
        HTTPException: If the seat is not found.
    """
    logger.info(f"Retrieving seat with id {seat_id}")
    db_seat = db.query(Seat).filter(Seat.id == seat_id).first()
    if not db_seat:
        logger.error(f"Seat with id {seat_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found")
    return db_seat

def get_seats(db: Session, skip: Optional[int] = None, limit: Optional[int] = None,
              session_id: Optional[int] = None, reservation_id: Optional[int] = None,
              seat_status: Optional[SeatStatus] = None) -> List[Seat]:
    """
    Retrieve a list of seats with optional filters.

    Args:
        db (Session): The database session.
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.
        session_id (Optional[int]): Filter by session ID.
        reservation_id (Optional[int]): Filter by reservation ID.
        seat_status (Optional[SeatStatus]): Filter by seat status.

    Returns:
        List[Seat]: A list of seats.
    """
    logger.info(f"Retrieving seats with filters - skip: {skip}, limit: {limit}, session_id: {session_id}, reservation_id: {reservation_id}, seat_status: {seat_status}")
    query = db.query(Seat)

    if session_id is not None:
        query = query.filter(Seat.session_id == session_id)

    if reservation_id is not None:
        query = query.filter(Seat.reservation_id == reservation_id)

    if seat_status is not None:
        query = query.filter(Seat.status == seat_status)

    if limit is not None:
        query = query.limit(limit)

    if skip is not None:
        query = query.offset(skip)

    seats = query.all()
    logger.info(f"Retrieved {len(seats)} seats")
    return seats
