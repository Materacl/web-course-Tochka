from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import update_session
from .database import get_db

scheduler = BackgroundScheduler()


@scheduler.scheduled_job('interval', seconds=15)
def scheduled_update_session():
    db = next(get_db())
    update_session(db)
