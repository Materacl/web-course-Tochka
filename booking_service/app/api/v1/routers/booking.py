from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas import BookingCreate, Booking
from ..crud.bookings import create_booking, get_booking, get_bookings, update_booking_status, delete_booking
from ..models import User, BookingStatus
from ..utils.auth import get_current_active_user, get_current_active_admin

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


@router.delete("/{booking_id}/delete", response_model=Booking)
def delete_booking_from_db(booking_id: int,
                           db: Session = Depends(get_db),
                           current_admin: User = Depends(get_current_active_admin)):
    return delete_booking(db, booking_id)


@router.post("/{booking_id}/{new_status}", response_model=Booking)
def set_booking_status(booking_id: int,
                       new_status: BookingStatus,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_active_admin)):
    return update_booking_status(db, booking_id, new_status)


@router.post("/{booking_id}", response_model=Booking)
def cancel_user_booking(booking_id: int,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_active_user)):
    db_booking = get_booking(db, booking_id=booking_id)
    if db_booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this booking")

    return update_booking_status(db, booking_id, BookingStatus.CANCELED)


@router.get("/{booking_id}", response_model=Booking)
def read_booking(booking_id: int, db: Session = Depends(get_db)):
    return get_booking(db, booking_id)


@router.get("/", response_model=List[Booking])
def read_bookings(skip: Optional[int] = None, limit: Optional[int] = None,
                  user_id: Optional[int] = None, session_id: Optional[int] = None,
                  booking_status: Optional[BookingStatus] = None,
                  db: Session = Depends(get_db)):
    return get_bookings(db,
                        skip=skip, limit=limit,
                        user_id=user_id, session_id=session_id, booking_status=booking_status)
