from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..models import Session as SessionModel, Seat, SessionStatus, SeatStatus, FilmStatus, BookingStatus, Film
from ..schemas import SessionCreate

from .seats import update_seat_status
from .bookings import update_booking_status

STATUS_ORDER = {
    SessionStatus.UPCOMING: 1,
    SessionStatus.NOW_PLAYING: 2,
    SessionStatus.COMPLETED: 3,
    SessionStatus.CANCELED: 4
}


def create_session(db: Session, session: SessionCreate):
    db_film = db.query(Film).filter(Film.id == session.film_id).first()
    if not db_film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film not found")
    if db_film.status == FilmStatus.NOT_AVAILABLE:
        HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Film is not available")

    db_session = SessionModel(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    for seat_number in range(1, session.capacity + 1):
        seat = Seat(
            session_id=db_session.id,
        )
        db.add(seat)
    db.commit()

    return db_session


def delete_session(db: Session, session_id: int):
    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    db.delete(db_session)
    db.commit()
    return db_session


def handle_bookings_and_seats(db: Session, db_session: SessionModel, new_status: SessionStatus):
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


def update_session_status(db: Session, session_id: int, new_status: Optional[SessionStatus] = None):
    db_session = get_session(db, session_id)

    current_status = db_session.status

    if new_status is not None:
        if current_status == SessionStatus.COMPLETED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Cannot change status of a completed session")

        if new_status != SessionStatus.CANCELED:
            if STATUS_ORDER[new_status] != STATUS_ORDER[current_status] + 1:
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
    return db_session


def get_session(db: Session, session_id: int):
    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return db_session


def get_sessions(db: Session,
                 skip: Optional[int] = None, limit: Optional[int] = None,
                 film_id: Optional[int] = None, session_status: Optional[SessionStatus] = None):
    query = db.query(SessionModel)

    if film_id is not None:
        query = query.filter(SessionModel.film_id == film_id)

    if session_status is not None:
        query = query.filter(SessionModel.status == session_status)

    if limit is not None:
        query = query.limit(limit)

    if skip is not None:
        query = query.offset(skip)

    return query.all()
