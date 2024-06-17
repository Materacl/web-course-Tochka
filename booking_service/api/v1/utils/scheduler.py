from datetime import timedelta, datetime
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

from .tasks import update_session, set_main_admin
from ..database import get_db

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = BackgroundScheduler()


@scheduler.scheduled_job('interval', seconds=15)
def scheduled_update_session():
    """
    Scheduled job to update sessions every 15 seconds.
    """
    logger.info("Running scheduled session update job")
    try:
        db = next(get_db())
        update_session(db)
        logger.info("Scheduled session update job completed successfully")
    except Exception as e:
        logger.error(f"Error in scheduled session update job: {e}")
    finally:
        db.close()


@scheduler.scheduled_job('interval', seconds=400)
def scheduled_update_payments():
    """
    Scheduled job to update outdated payments every 400 seconds.
    """
    logger.info("Running scheduled session payments update job")
    try:
        db = next(get_db())
        update_session(db)
        logger.info("Scheduled payments update job completed successfully")
    except Exception as e:
        logger.error(f"Error in scheduled payments update job: {e}")
    finally:
        db.close()


def set_main_admin_job():
    """
    One-time job to set the main admin.
    """
    logger.info("Running one-time set main admin job")
    try:
        db = next(get_db())
        set_main_admin(db)
        logger.info("One-time set main admin job completed successfully")
    except Exception as e:
        logger.error(f"Error in one-time set main admin job: {e}")
    finally:
        db.close()


# Schedule one-time job to run 1 minute from now
one_time_run = datetime.now() + timedelta(minutes=1)
scheduler.add_job(set_main_admin_job, DateTrigger(run_date=one_time_run))
