from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_mail import MessageSchema
from sqlalchemy.orm import Session
from typing import List, Optional, Any

from ..database import get_db
from ..schemas import BookingCreate, Booking
from ..crud.bookings import create_booking, get_booking, get_bookings, update_booking_status, delete_booking
from ..crud.users import get_user_by_id
from ..models import User, BookingStatus
from ..utils.auth import get_current_active_user, get_current_active_admin
from ..utils.email import send_notification

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=Booking, status_code=status.HTTP_201_CREATED, summary="Create a new booking", tags=["bookings"])
async def create_new_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Booking:
    """
    Create a new booking.

    Args:
        booking (BookingCreate): The booking creation data.
        db (Session): The database session.
        current_user (User): The current active user.

    Returns:
        Booking: The created booking.
    """
    return create_booking(db=db, booking=booking, user_id=current_user.id)


@router.delete("/{booking_id}/delete", response_model=Booking, status_code=status.HTTP_200_OK, summary="Delete a booking", tags=["bookings"])
async def delete_booking_from_db(
    booking_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
) -> Booking:
    """
    Delete a booking by ID.

    Args:
        booking_id (int): The ID of the booking to delete.
        db (Session): The database session.
        current_admin (User): The current active admin.

    Returns:
        Booking: The deleted booking.
    """
    return delete_booking(db, booking_id)


@router.post("/{booking_id}/{new_status}", response_model=Booking, status_code=status.HTTP_200_OK, summary="Set booking status", tags=["bookings"])
async def set_booking_status(
    booking_id: int,
    new_status: BookingStatus,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
) -> Booking:
    """
    Set the status of a booking.

    Args:
        booking_id (int): The ID of the booking.
        new_status (BookingStatus): The new status to set.
        db (Session): The database session.
        current_admin (User): The current active admin.

    Returns:
        Booking: The updated booking.
    """
    db_booking = update_booking_status(db, booking_id, new_status)
    db_user = get_user_by_id(db, db_booking.user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if db_user.notifications:
        message = MessageSchema(
            subject="Booking Status",
            recipients=[db_user.email],
            body=f"Booking status is changed to {new_status}. Check HomeCinemaVR!",
            subtype="html"
        )
        await send_notification(message)
    return db_booking


@router.post("/{booking_id}/cancel", response_model=Booking, status_code=status.HTTP_200_OK, summary="Cancel user booking", tags=["bookings"])
async def cancel_user_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Booking:
    """
    Cancel a user booking.

    Args:
        booking_id (int): The ID of the booking to cancel.
        db (Session): The database session.
        current_user (User): The current active user.

    Returns:
        Booking: The cancelled booking.

    Raises:
        HTTPException: If the user is not authorized to cancel the booking.
    """
    db_booking = get_booking(db, booking_id=booking_id)
    if db_booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this booking")

    return update_booking_status(db, booking_id, BookingStatus.CANCELED)


@router.get("/{booking_id}", response_model=Booking, status_code=status.HTTP_200_OK, summary="Read a booking", tags=["bookings"])
async def read_booking(booking_id: int, db: Session = Depends(get_db)) -> Booking:
    """
    Read a booking by ID.

    Args:
        booking_id (int): The ID of the booking to read.
        db (Session): The database session.

    Returns:
        Booking: The booking with the given ID.
    """
    return get_booking(db, booking_id)


@router.get("/", response_model=List[Booking], status_code=status.HTTP_200_OK, summary="Read multiple bookings", tags=["bookings"])
async def read_bookings(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    user_id: Optional[int] = None,
    session_id: Optional[int] = None,
    booking_status: Optional[BookingStatus] = None,
    db: Session = Depends(get_db)
) -> List[Booking]:
    """
    Read multiple bookings with optional filters.

    Args:
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.
        user_id (Optional[int]): Filter by user ID.
        session_id (Optional[int]): Filter by session ID.
        booking_status (Optional[BookingStatus]): Filter by booking status.
        db (Session): The database session.

    Returns:
        List[Booking]: A list of bookings.
    """
    return get_bookings(
        db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        session_id=session_id,
        booking_status=booking_status
    )
