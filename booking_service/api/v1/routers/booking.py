import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas import BookingCreate, Booking
from ..crud.bookings import create_booking, get_booking, get_bookings, update_booking_status, delete_booking
from ..crud.users import get_user_by_id
from ..models import User, BookingStatus
from ..utils.auth import get_current_active_user, get_current_active_admin
from ..utils.rabbitmq import publish_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logger.info(f"Creating a new booking for user: {current_user.email}")
    db_booking = create_booking(db=db, booking=booking, user_id=current_user.id)
    logger.info(f"Booking created with ID: {db_booking.id}")
    return db_booking

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
    logger.info(f"Admin {current_admin.email} attempting to delete booking with ID: {booking_id}")
    db_booking = delete_booking(db, booking_id)
    logger.info(f"Booking with ID: {booking_id} deleted")
    return db_booking

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
    logger.info(f"Admin {current_admin.email} setting status of booking ID {booking_id} to {new_status}")
    db_booking = update_booking_status(db, booking_id, new_status)
    db_user = get_user_by_id(db, db_booking.user_id)
    if not db_user:
        logger.error(f"User not found for booking ID {booking_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if db_user.notifications:
        await publish_message(
            'booking_notifications',
            subject="Booking Status Update",
            recipients=[db_user.email],
            body=f"Booking status changed to {new_status}.",
        )
    logger.info(f"Booking ID {booking_id} status updated to {new_status}")
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
    logger.info(f"User {current_user.email} attempting to cancel booking with ID {booking_id}")
    db_booking = get_booking(db, booking_id=booking_id)
    if db_booking.user_id != current_user.id and not current_user.is_admin:
        logger.warning(f"Unauthorized cancellation attempt by user {current_user.email} for booking ID {booking_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this booking")
    update_booking_status(db, booking_id, BookingStatus.CANCELED)

    if current_user.notifications:
        await publish_message(
            'booking_notifications',
            subject="Booking Cancellation",
            recipients=[current_user.email],
            body=f"Booking with ID {booking_id} cancelled.",
        )
    logger.info(f"Booking with ID {booking_id} cancelled")
    return db_booking

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
    logger.info(f"Fetching booking details for booking ID {booking_id}")
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
    logger.info("Fetching multiple bookings")
    return get_bookings(
        db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        session_id=session_id,
        booking_status=booking_status
    )
