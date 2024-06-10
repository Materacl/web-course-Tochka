from sqlalchemy.orm import Session
from ..config import settings
from ..models import Session as SessionModel
from ..crud.sessions import update_session_status
from ..crud.users import grant_user_admin


def update_session(db: Session):
    sessions = db.query(SessionModel).all()

    for session in sessions:
        update_session_status(db, session.id)
    db.commit()


def set_main_admin(db: Session):
    grant_user_admin(db, settings.MAIN_ADMIN)
    db.commit()
