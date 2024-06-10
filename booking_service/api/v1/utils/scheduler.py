from datetime import timedelta, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

from .tasks import update_session, set_main_admin
from ..database import get_db

scheduler = BackgroundScheduler()


@scheduler.scheduled_job('interval', seconds=15)
def scheduled_update_session():
    db = next(get_db())
    update_session(db)


def set_main_admin_job():
    db = next(get_db())
    set_main_admin(db)


one_time_run = datetime.now() + timedelta(minutes=1)
scheduler.add_job(set_main_admin_job, DateTrigger(run_date=one_time_run))
