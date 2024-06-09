from sqlalchemy.orm import Session
from .models import Session as SessionModel, SessionStatus
from .crud.sessions import update_session_status


def update_session(db: Session):
    sessions = db.query(SessionModel).all()

    for session in sessions:
        update_session_status(db, session.id)
    db.commit()
