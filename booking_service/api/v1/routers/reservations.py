from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ReservationCreate, Reservation
from ..crud.reservations import create_reservation, delete_reservation, get_reservation, get_reservations, update_reservation_status
from ..models import User, ReservationStatus
from ..utils.auth import get_current_user, get_current_active_admin

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Reservation, status_code=status.HTTP_201_CREATED, summary="Create a new reservation", tags=["reservations"])
async def create_new_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Reservation:
    """
    Create a new reservation.

    Args:
        reservation (ReservationCreate): The reservation creation data.
        db (Session): The database session.
        current_user (User): The current active user.

    Returns:
        Reservation: The created reservation.
    """
    return create_reservation(db=db, reservation=reservation)

@router.delete("/{reservation_id}/delete", response_model=Reservation, status_code=status.HTTP_200_OK, summary="Delete a reservation", tags=["reservations"])
async def delete_reservation_from_db(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
) -> Reservation:
    """
    Delete a reservation by ID.

    Args:
        reservation_id (int): The ID of the reservation to delete.
        db (Session): The database session.
        current_admin (User): The current active admin.

    Returns:
        Reservation: The deleted reservation.
    """
    return delete_reservation(db, reservation_id)

@router.post("/{reservation_id}/status/{new_status}", response_model=Reservation, status_code=status.HTTP_200_OK, summary="Set reservation status", tags=["reservations"])
async def set_reservation_status(
    reservation_id: int,
    new_status: ReservationStatus,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
) -> Reservation:
    """
    Set the status of a reservation.

    Args:
        reservation_id (int): The ID of the reservation.
        new_status (ReservationStatus): The new status to set.
        db (Session): The database session.
        current_admin (User): The current active admin.

    Returns:
        Reservation: The updated reservation with the new status.
    """
    return update_reservation_status(db, reservation_id, new_status)

@router.delete("/{reservation_id}/cancel", response_model=Reservation, status_code=status.HTTP_200_OK, summary="Cancel user reservation", tags=["reservations"])
async def cancel_user_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Reservation:
    """
    Cancel a user reservation.

    Args:
        reservation_id (int): The ID of the reservation to cancel.
        db (Session): The database session.
        current_user (User): The current active user.

    Returns:
        Reservation: The cancelled reservation.

    Raises:
        HTTPException: If the user is not authorized to cancel the reservation.
    """
    db_reservation = get_reservation(db, reservation_id=reservation_id)
    if db_reservation.booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this reservation")

    return update_reservation_status(db, reservation_id, ReservationStatus.CANCELED)

@router.get("/{reservation_id}", response_model=Reservation, status_code=status.HTTP_200_OK, summary="Get a reservation by ID", tags=["reservations"])
async def read_reservation(
    reservation_id: int,
    db: Session = Depends(get_db)
) -> Reservation:
    """
    Get a reservation by its ID.

    Args:
        reservation_id (int): The ID of the reservation to retrieve.
        db (Session): The database session.

    Returns:
        Reservation: The reservation with the given ID.
    """
    return get_reservation(db, reservation_id)

@router.get("/", response_model=List[Reservation], status_code=status.HTTP_200_OK, summary="Get reservations with optional filters", tags=["reservations"])
async def read_reservations(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
) -> List[Reservation]:
    """
    Get a list of reservations with optional filters.

    Args:
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        db (Session): The database session.

    Returns:
        List[Reservation]: A list of reservations.
    """
    return get_reservations(db, skip=skip, limit=limit)