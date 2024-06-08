from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..models import Film, Seat, Booking, Reservation, ReservationStatus, SeatStatus
from ..schemas import ReservationCreate

from .seats import update_seat_status


def create_reservation(db: Session, reservation: ReservationCreate):
    seat = db.query(Seat).filter(Seat.id == reservation.seat_id).one()
    if seat.status != SeatStatus.AVAILABLE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seat is already reserved")
    db_reservation = Reservation(**reservation.dict())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


def delete_reservation(db: Session, reservation_id: int):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    db.delete(db_reservation)
    db.commit()
    return db_reservation


def update_reservation_status(db: Session, reservation_id: int, new_status: ReservationStatus):
    db_reservation = get_reservation(db, reservation_id)

    if new_status == ReservationStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot change status of confirmed or canceled reservation to pending")

    db_reservation.status = new_status
    if new_status == ReservationStatus.CONFIRMED:
        update_seat_status(db, db_reservation.seat_id, SeatStatus.RESERVED)
    elif new_status == ReservationStatus.CANCELED:
        update_seat_status(db, db_reservation.seat_id, SeatStatus.CANCELED)

    db.commit()

    return db_reservation


def get_reservation(db: Session, reservation_id: int):
    db_reservation = db.query(Film).filter(Film.id == reservation_id).first()
    if not db_reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()


def get_reservations(db: Session,
                     skip: Optional[int] = None, limit: Optional[int] = None,
                     user_id: Optional[int] = None, session_id: Optional[int] = None,
                     reservation_status: Optional[ReservationStatus] = None):
    query = db.query(Reservation)

    if user_id is not None:
        query = query.filter(Reservation.booking.has(Booking.user_id == user_id))

    if session_id is not None:
        query = query.filter(Reservation.booking.has(Booking.session_id == session_id))

    if reservation_status is not None:
        query = query.filter(Reservation.status == reservation_status)

    if limit is not None:
        query = query.limit(limit)

    if skip is not None:
        query = query.offset(skip)

    return query.all()
