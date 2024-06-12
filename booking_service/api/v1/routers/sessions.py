from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SessionStatus
from ..schemas import SessionCreate, Session, User
from ..crud.sessions import create_session, get_sessions, get_session, delete_session, update_session_status, update_session_price
from ..utils.auth import get_current_active_admin

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=Session, status_code=status.HTTP_201_CREATED, summary="Create a new session", tags=["sessions"])
async def create_new_session(
    session: SessionCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
) -> Session:
    """
    Create a new session.

    Args:
        session (SessionCreate): The session creation data.
        db (Session): The database session.
        current_admin (User): The current active admin.

    Returns:
        Session: The created session.
    """
    return create_session(db=db, session=session)

@router.delete("/{session_id}/delete", response_model=Session, status_code=status.HTTP_200_OK, summary="Delete a session", tags=["sessions"])
async def delete_session_from_db(
    session_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
) -> Session:
    """
    Delete a session by ID.

    Args:
        session_id (int): The ID of the session to delete.
        db (Session): The database session.
        current_admin (User): The current active admin.

    Returns:
        Session: The deleted session.
    """
    return delete_session(db, session_id)

@router.post("/{session_id}/status/{new_status}", response_model=Session, status_code=status.HTTP_200_OK, summary="Set session status", tags=["sessions"])
async def set_session_status(
    session_id: int,
    new_status: SessionStatus,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
) -> Session:
    """
    Set the status of a session.

    Args:
        session_id (int): The ID of the session.
        new_status (SessionStatus): The new status to set.
        db (Session): The database session.
        current_admin (User): The current active admin.

    Returns:
        Session: The updated session with the new status.
    """
    return update_session_status(db, session_id, new_status)

@router.post("/{session_id}/price/{new_price}", response_model=Session, status_code=status.HTTP_200_OK, summary="Set session price", tags=["sessions"])
async def set_session_price(
    session_id: int,
    new_price: float,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
) -> Session:
    """
    Set the price of a session.

    Args:
        session_id (int): The ID of the session.
        new_price (float): The new price to set.
        db (Session): The database session.
        current_admin (User): The current active admin.

    Returns:
        Session: The updated session with the new price.
    """
    return update_session_price(db, session_id, new_price)

@router.get("/{session_id}", response_model=Session, status_code=status.HTTP_200_OK, summary="Get a session by ID", tags=["sessions"])
async def read_session(
    session_id: int,
    db: Session = Depends(get_db)
) -> Session:
    """
    Get a session by its ID.

    Args:
        session_id (int): The ID of the session to retrieve.
        db (Session): The database session.

    Returns:
        Session: The session with the given ID.
    """
    return get_session(db, session_id)

@router.get("/", response_model=List[Session], status_code=status.HTTP_200_OK, summary="Get sessions with optional filters", tags=["sessions"])
async def read_sessions(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    film_id: Optional[int] = None,
    session_status: Optional[SessionStatus] = None,
    db: Session = Depends(get_db)
) -> List[Session]:
    """
    Get a list of sessions with optional filters.

    Args:
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.
        film_id (Optional[int]): Filter by film ID.
        session_status (Optional[SessionStatus]): Filter by session status.
        db (Session): The database session.

    Returns:
        List[Session]: A list of sessions.
    """
    return get_sessions(db, skip=skip, limit=limit, film_id=film_id, session_status=session_status)