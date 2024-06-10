from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import ReservationCreate, Reservation
from ..crud.reservations import create_reservation, delete_reservation, get_reservation, get_reservations, \
    update_reservation_status
from ..models import User, ReservationStatus
from ..utils.auth import get_current_user, get_current_active_admin

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=Reservation)
async def create_new_reservation(reservation: ReservationCreate,
                                 db: Session = Depends(get_db),
                                 current_user: User = Depends(get_current_user)):
    return create_reservation(db=db, reservation=reservation)


@router.delete("/{reservation_id}/delete", response_model=Reservation)
async def delete_booking_from_db(reservation_id: int,
                                 db: Session = Depends(get_db),
                                 current_admin: User = Depends(get_current_active_admin)):
    return delete_reservation(db, reservation_id)


@router.post("/{reservation_id}/{new_status}", response_model=Reservation)
async def set_booking_status(booking_id: int,
                             new_status: ReservationStatus,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_active_admin)):
    return update_reservation_status(db, booking_id, new_status)


@router.delete("/{reservation_id}", response_model=Reservation)
async def cancel_user_reservation(reservation_id: int,
                                  db: Session = Depends(get_db),
                                  current_user: User = Depends(get_current_user)):
    db_reservation = get_reservation(db, reservation_id=reservation_id)
    if db_reservation.booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this reservation")

    return update_reservation_status(db, reservation_id, ReservationStatus.CANCELED)


@router.get("/{reservation_id}", response_model=Reservation)
async def read_reservations(reservation_id: int = 0, db: Session = Depends(get_db)):
    return get_reservation(db, reservation_id)


@router.get("/", response_model=List[Reservation])
async def read_reservations(skip: int = 0, limit: int = 10,
                            db: Session = Depends(get_db)):
    return get_reservations(db, skip=skip, limit=limit)
