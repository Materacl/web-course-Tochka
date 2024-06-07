from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas import BookingCreate, Booking
from ..crud import create_booking, get_booking, get_bookings, update_booking_status, delete_booking, get_user_bookings
from ..models import User
from ..utils.auth import get_current_user, get_current_active_user

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=Booking)
def create_new_booking(booking: BookingCreate,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_active_user)):
    return create_booking(db=db, booking=booking, user_id=current_user.id)


@router.get("/{booking_id}", response_model=Booking)
def read_booking(booking_id: int, db: Session = Depends(get_db)):
    return get_booking(db, booking_id)


@router.get("/", response_model=List[Booking])
def read_bookings(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    print(1)
    return get_bookings(db, skip=skip, limit=limit)


@router.get("/{booking_id}/status", response_model=Booking)
def read_booking_status(booking_id: int, db: Session = Depends(get_db)):
    db_booking = get_booking(db, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking


@router.get("/current_user/", response_model=List[Booking])
def read_bookings_current_user(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
        skip: int = 0, limit: int = 10):
    return get_user_bookings(db, current_user.id, skip=skip, limit=limit)


@router.delete("/{booking_id}", response_model=Booking)
def cancel_existing_booking(booking_id: int,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_active_user)):
    db_booking = get_booking(db, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if db_booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this booking")

    return delete_booking(db, booking_id=booking_id)
