from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ReservationCreate, Reservation
from app.crud import create_reservation, get_reservation, get_reservations, update_reservation_status
from app.models import User
from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=Reservation)
def create_new_reservation(reservation: ReservationCreate,
                           db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    return create_reservation(db=db, reservation=reservation, user_id=current_user.id)


@router.get("/{reservation_id}", response_model=Reservation)
def read_reservations(reservation_id: int = 0, db: Session = Depends(get_db)):
    return get_reservation(db, reservation_id)


@router.get("/", response_model=List[Reservation])
def read_reservations(skip: int = 0, limit: int = 10,
                            db: Session = Depends(get_db)):
    return get_reservations(db, skip=skip, limit=limit)


@router.get("/{reservation_id}/status", response_model=Reservation)
def read_reservation_status(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = get_reservation(db, reservation_id=reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return db_reservation


@router.delete("/{reservation_id}", response_model=Reservation)
def cancel_existing_reservation(reservation_id: int,
                                db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    db_reservation = get_reservation(db, reservation_id=reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if db_reservation.booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this reservation")

    return update_reservation_status(db, reservation_id=reservation_id, status="canceled")
