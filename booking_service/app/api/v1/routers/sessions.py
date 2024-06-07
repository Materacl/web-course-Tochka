from fastapi import APIRouter, Depends
from typing import List
from ..database import get_db
from ..schemas import SessionCreate, Session
from ..crud import create_session, get_sessions, get_session

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
    responses={404: {"description": "Not found"}}
)


@router.get("/{session_id}", response_model=Session)
def read_session(session_id: int, db: Session = Depends(get_db)):
    return get_session(db, session_id)


@router.get("/", response_model=List[Session])
def read_sessions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_sessions(db, skip=skip, limit=limit)
