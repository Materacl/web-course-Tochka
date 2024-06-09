from fastapi import APIRouter, Depends
from typing import List, Optional
from ..database import get_db
from ..models import SessionStatus
from ..schemas import SessionCreate, Session, User
from ..crud.sessions import create_session, get_sessions, get_session, delete_session, update_session_status, \
    update_session_price
from ..utils.auth import get_current_active_admin

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=Session)
async def create_new_session(session: SessionCreate,
                             db: Session = Depends(get_db),
                             current_admin: User = Depends(get_current_active_admin)):
    return create_session(db=db, session=session)


@router.delete("/{session_id}/delete", response_model=Session)
async def delete_session_from_db(session_id: int,
                                 db: Session = Depends(get_db),
                                 current_admin: User = Depends(get_current_active_admin)):
    return delete_session(db, session_id)


@router.post("/{session_id}/status/{new_status}", response_model=Session)
async def set_session_status(session_id: int,
                             new_status: SessionStatus,
                             db: Session = Depends(get_db),
                             current_admin: User = Depends(get_current_active_admin)):
    return update_session_status(db, session_id, new_status)


@router.post("/{session_id}/price/{new_price}", response_model=Session)
async def set_session_price(session_id: int,
                            new_price: float,
                            db: Session = Depends(get_db),
                            current_admin: User = Depends(get_current_active_admin)):
    return update_session_price(db, session_id, new_price)


@router.get("/{session_id}", response_model=Session)
async def read_session(session_id: int, db: Session = Depends(get_db)):
    return get_session(db, session_id)


@router.get("/", response_model=List[Session])
async def read_sessions(skip: Optional[int] = None, limit: Optional[int] = None,
                        film_id: Optional[int] = None, session_status: Optional[SessionStatus] = None,
                        db: Session = Depends(get_db)):
    return get_sessions(db, skip=skip, limit=limit,
                        film_id=film_id, session_status=session_status)
