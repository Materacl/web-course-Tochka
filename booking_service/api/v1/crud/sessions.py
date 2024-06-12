from datetime import datetime, timedelta
from typing import Optional, List
import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..models import Session as SessionModel, Seat, SessionStatus, SeatStatus, FilmStatus, BookingStatus, Film
from ..schemas import SessionCreate
from .seats import update_seat_status
from .bookings import update_booking_status

# Initialize logger
logger = logging.getLogger(__name__)

STATUS_ORDER = {
    SessionStatus.UPCOMING: 1,
    SessionStatus.NOW_PLAYING: 2,
    SessionStatus.COMPLETED: 3,
    SessionStatus.CANCELED: 4
}

def create_session(db: Session, session: SessionCreate) -> SessionModel:
    """
    Create a new session.

    Args:
        db (Session): The database session.
        session (SessionCreate): The session creation schema.

    Returns:
        SessionModel: The created session.

    Raises:
        HTTPException: If the film is not found or if the film is not available.
    """
    logger.info(f"Creating a new session for film_id: {session.film_id}")
    db_film = db.query(Film).filter(Film.id == session.film_id).first()
    if not db_film:
        logger.error(f"Film with id {session.film_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film not found")
    if db_film.status == FilmStatus.NOT_AVAILABLE:
        logger.error(f"Film with id {session.film_id} is not available")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Film is not available")

    db_session = SessionModel(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    logger.info(f"Session created with id {db_session.id}")

    for seat_number in range(1, session.capacity + 1):
        seat = Seat(session_id=db_session.id)
        db.add(seat)
    db.commit()
    logger.info(f"{session.capacity} seats created for session id {db_session.id}")

    return db_session

def delete_session(db: Session, session_id: int) -> SessionModel:
    """
    Delete a session by its ID.

    Args:
        db (Session): The database session.
        session_id (int): The ID of the session to delete.

    Returns:
        SessionModel: The deleted session.
    """
    logger.info(f"Deleting session with id {session_id}")
    db_session = get_session(db, session_id)

    db.delete(db_session)
    db.commit()
    logger.info(f"Session with id {session_id} deleted")
    return db_session

def handle_bookings_and_seats(db: Session, db_session: SessionModel, new_status: SessionStatus):
    """
    Handle bookings and seats when the session status changes.

    Args:
        db (Session): The database session.
        db_session (SessionModel): The session model instance.
        new_status (SessionStatus): The new status of the session.
    """
    logger.info(f"Handling bookings and seats for session id {db_session.id} with new status {new_status}")
    if new_status in [SessionStatus.NOW_PLAYING, SessionStatus.COMPLETED]:
        for booking in db_session.bookings:
            if booking.status == BookingStatus.PENDING:
                update_booking_status(db, booking.id, BookingStatus.CANCELED)
        for seat in db_session.seats:
            update_seat_status(db, seat.id, SeatStatus.RESERVED)
    elif new_status == SessionStatus.CANCELED:
        for booking in db_session.bookings:
            update_booking_status(db, booking.id, BookingStatus.CANCELED)
        for seat in db_session.seats:
            update_seat_status(db, seat.id, SeatStatus.CANCELED)

def update_session_status(db: Session, session_id: int, new_status: Optional[SessionStatus] = None) -> SessionModel:
    """
    Update the status of a session.

    Args:
        db (Session): The database session.
        session_id (int): The ID of the session to update.
        new_status (Optional[SessionStatus]): The new status of the session.

    Returns:
        SessionModel: The updated session.

    Raises:
        HTTPException: If the session is completed or if the status transition is invalid.
    """
    logger.info(f"Updating status of session id {session_id} to {new_status}")
    db_session = get_session(db, session_id)

    current_status = db_session.status

    if new_status is not None:
        if current_status == SessionStatus.COMPLETED:
            logger.error(f"Cannot change status of a completed session id {session_id}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Cannot change status of a completed session")

        if new_status != SessionStatus.CANCELED:
            if STATUS_ORDER[new_status] != STATUS_ORDER[current_status] + 1:
                logger.error(f"Cannot change status of session id {session_id} to a non-next status")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Cannot change status of session to a non-next status")

        db_session.status = new_status
        handle_bookings_and_seats(db, db_session, new_status)
    else:
        if current_status != SessionStatus.CANCELED:
            now = datetime.utcnow()
            session_end_time = db_session.datetime + timedelta(minutes=db_session.film.duration)

            if db_session.datetime > now:
                db_session.status = SessionStatus.UPCOMING
            elif db_session.datetime <= now < session_end_time:
                db_session.status = SessionStatus.NOW_PLAYING
                handle_bookings_and_seats(db, db_session, SessionStatus.NOW_PLAYING)
            else:
                db_session.status = SessionStatus.COMPLETED
                handle_bookings_and_seats(db, db_session, SessionStatus.COMPLETED)

    db.commit()
    logger.info(f"Status of session id {session_id} updated to {db_session.status}")
    return db_session

def update_session_price(db: Session, session_id: int, new_price: float) -> SessionModel:
    """
    Update the price of a session.

    Args:
        db (Session): The database session.
        session_id (int): The ID of the session to update.
        new_price (float): The new price of the session.

    Returns:
        SessionModel: The updated session.
    """
    logger.info(f"Updating price of session id {session_id} to {new_price}")
    db_session = get_session(db, session_id)

    db_session.price = new_price

    db.commit()
    logger.info(f"Price of session id {session_id} updated to {new_price}")
    return db_session

def get_session(db: Session, session_id: int) -> SessionModel:
    """
    Retrieve a session by its ID.

    Args:
        db (Session): The database session.
        session_id (int): The ID of the session to retrieve.

    Returns:
        SessionModel: The retrieved session.

    Raises:
        HTTPException: If the session is not found.
    """
    logger.info(f"Retrieving session with id {session_id}")
    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not db_session:
        logger.error(f"Session with id {session_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return db_session

def get_sessions(db: Session, skip: Optional[int] = None, limit: Optional[int] = None,
                 film_id: Optional[int] = None, session_status: Optional[SessionStatus] = None) -> List[SessionModel]:
    """
    Retrieve a list of sessions with optional filters.

    Args:
        db (Session): The database session.
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.
        film_id (Optional[int]): Filter by film ID.
        session_status (Optional[SessionStatus]): Filter by session status.

    Returns:
        List[SessionModel]: A list of sessions.
    """
    logger.info(f"Retrieving sessions with filters - skip: {skip}, limit: {limit}, film_id: {film_id}, session_status: {session_status}")
    query = db.query(SessionModel)

    if film_id is not None:
        query = query.filter(SessionModel.film_id == film_id)

    if session_status is not None:
        query = query.filter(SessionModel.status == session_status)

    if limit is not None:
        query = query.limit(limit)

    if skip is not None:
        query = query.offset(skip)

    sessions = query.all()
    logger.info(f"Retrieved {len(sessions)} sessions")
    return sessions
