from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..models import Session as SessionModel, Booking, Reservation, BookingStatus, ReservationStatus, SessionStatus
from ..schemas import BookingCreate

from .reservations import update_reservation_status


def create_booking(db: Session, booking: BookingCreate, user_id: int):
    db_session = db.query(SessionModel).filter(SessionModel.id == booking.session_id).first()
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if db_session.status != SessionStatus.UPCOMING:
        HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                      detail="Cannot create booking for a session that is not upcoming")
    db_booking = Booking(**booking.dict(), user_id=user_id)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def delete_booking(db: Session, booking_id: int):
    db_booking = db.query(SessionModel).filter(SessionModel.id == booking_id).first()
    db.delete(db_booking)
    db.commit()
    return db_booking


def update_booking_status(db: Session, booking_id: int, new_status: BookingStatus):
    db_booking = get_booking(db, booking_id)

    if new_status == BookingStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot change status of confirmed or canceled booking to pending")
    db_booking.status = new_status
    if new_status == BookingStatus.CONFIRMED:
        for reservation in db_booking.reservations:
            update_reservation_status(db, reservation.id, ReservationStatus.CONFIRMED)
    elif new_status == BookingStatus.CANCELED:
        for reservation in db_booking.reservations:
            update_reservation_status(db, reservation.id, ReservationStatus.CANCELED)

    db.commit()
    return db_booking


def get_booking(db: Session, booking_id: int):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return db_booking


def get_bookings(db: Session,
                 skip: Optional[int] = None, limit: Optional[int] = None,
                 user_id: Optional[int] = None, session_id: Optional[int] = None,
                 booking_status: Optional[BookingStatus] = None):
    query = db.query(Booking)

    if user_id is not None:
        query = query.filter(Booking.user_id == user_id)

    if session_id is not None:
        query = query.filter(Booking.session_id == session_id)

    if booking_status is not None:
        query = query.filter(Booking.status == booking_status)

    if limit is not None:
        query = query.limit(limit)

    if skip is not None:
        query = query.offset(skip)

    return query.all()
