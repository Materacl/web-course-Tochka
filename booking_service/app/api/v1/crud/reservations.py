from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..models import Seat, Booking, Reservation, ReservationStatus, SeatStatus, BookingStatus
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
    if db_reservation.booking.session.auto_booking:
        update_reservation_status(db, db_reservation.id, ReservationStatus.CONFIRMED)
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
                            detail="Can not change status to pending")

    if db_reservation.status == ReservationStatus.CANCELED and new_status != ReservationStatus.CANCELED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Can not change status of canceled reservation")

    if db_reservation.status == ReservationStatus.PENDING:
        if new_status == ReservationStatus.CONFIRMED:
            update_seat_status(db, db_reservation.seat_id, SeatStatus.RESERVED)
    elif db_reservation.status == ReservationStatus.CONFIRMED:
        if new_status == ReservationStatus.CANCELED:
            update_seat_status(db, db_reservation.seat_id, SeatStatus.AVAILABLE)

    db_reservation.status = new_status
    db.commit()

    return db_reservation


def get_reservation(db: Session, reservation_id: int):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not db_reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()


def get_reservations(db: Session,
                     skip: Optional[int] = None, limit: Optional[int] = None,
                     user_id: Optional[int] = None, booking_id: Optional[int] = None,
                     seat_id: Optional[int] = None, reservation_status: Optional[ReservationStatus] = None):
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

    return query.all()
