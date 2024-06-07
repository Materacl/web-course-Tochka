from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import BookingCreate, Booking
from app.crud import create_booking, get_booking, get_bookings, update_booking_status, delete_booking
from app.models import User
from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=Booking)
def create_new_booking(booking: BookingCreate,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    return create_booking(db=db, booking=booking)


@router.get("/{booking_id}", response_model=Booking)
def read_booking(booking_id: int, db: Session = Depends(get_db)):
    return get_booking(db, booking_id)


@router.get("/", response_model=List[Booking])
def read_bookings(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_bookings(db, skip=skip, limit=limit)


@router.get("/{booking_id}/status", response_model=Booking)
def read_booking_status(booking_id: int, db: Session = Depends(get_db)):
    db_booking = get_booking(db, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking


@router.delete("/{booking_id}", response_model=Booking)
def cancel_existing_booking(booking_id: int,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    db_booking = get_booking(db, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if db_booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this booking")

    return delete_booking(db, booking_id=booking_id)
