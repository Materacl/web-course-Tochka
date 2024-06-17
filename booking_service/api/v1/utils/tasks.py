from sqlalchemy.orm import Session
import logging

from ..config import settings
from ..models import Session as SessionModel, Payment
from ..crud.sessions import update_session_status
from ..crud.payments import update_payment_status
from ..crud.users import grant_user_admin

# Initialize logger
logger = logging.getLogger(__name__)


def update_session(db: Session):
    """
    Update the status of all sessions.

    Args:
        db (Session): The database session.
    """
    logger.info("Starting session update task")
    try:
        sessions = db.query(SessionModel).all()
        for session in sessions:
            update_session_status(db, session.id)
        db.commit()
        logger.info("Session update task completed successfully")
    except Exception as e:
        logger.error(f"Error during session update task: {e}")
        db.rollback()
    finally:
        db.close()


def update_payments(db: Session):
    """
    Update the status of all payments.

    Args:
        db (Session): The database session.
    """
    logger.info("Starting payments update task")
    try:
        payments = db.query(Payment).all()
        for payment in payments:
            update_payment_status(db, payment.id)
        db.commit()
        logger.info("Payment update task completed successfully")
    except Exception as e:
        logger.error(f"Error during payment update task: {e}")
        db.rollback()
    finally:
        db.close()


def set_main_admin(db: Session):
    """
    Grant admin privileges to the main admin user.

    Args:
        db (Session): The database session.
    """
    logger.info(f"Setting main admin: {settings.MAIN_ADMIN}")
    try:
        grant_user_admin(db, settings.MAIN_ADMIN)
        db.commit()
        logger.info("Main admin privileges granted successfully")
    except Exception as e:
        logger.error(f"Error during setting main admin: {e}")
        db.rollback()
    finally:
        db.close()
