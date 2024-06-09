from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..models import Seat, SeatStatus
from ..schemas import SeatCreate


def create_seat(db: Session, seat: SeatCreate):
    db_seat = Seat(**seat.dict())
    db.add(db_seat)
    db.commit()
    db.refresh(db_seat)
    return db_seat


def delete_seat(db: Session, seat_id: int):
    db_seat = db.query(Seat).filter(Seat.id == seat_id).first()
    db.delete(db_seat)
    db.commit()
    return db_seat


def update_seat_status(db: Session, seat_id: int, new_status: SeatStatus):
    db_seat = get_seat(db, seat_id)

    if db_seat.status != SeatStatus.CANCELED:
        if new_status == SeatStatus.AVAILABLE:
            db_seat.status = SeatStatus.AVAILABLE
        elif new_status == SeatStatus.RESERVED:
            if db_seat.status == SeatStatus.RESERVED:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seat is already reserved")
            db_seat.status = SeatStatus.RESERVED
        elif new_status == SeatStatus.CANCELED:
            db_seat.status = SeatStatus.CANCELED

    db.commit()

    return db_seat


def get_seat(db: Session, seat_id: int):
    db_seat = db.query(Seat).filter(Seat.id == seat_id).first()
    if not db_seat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found")
    return db_seat


def get_seats(db: Session,
              skip: Optional[int] = None, limit: Optional[int] = None,
              session_id: Optional[int] = None, reservation_id: Optional[int] = None,
              seat_status: Optional[SeatStatus] = None):
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
    return query.all()
