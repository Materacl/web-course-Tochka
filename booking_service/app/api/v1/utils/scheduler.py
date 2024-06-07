# Example code for a scheduler using Celery or another task scheduler to handle auto-cancellations

from celery import Celery
from datetime import datetime, timedelta
from ..crud import get_unconfirmed_reservations, cancel_reservation

celery = Celery('tasks', broker='redis://localhost:6379/0')


@celery.task
def auto_cancel_unconfirmed_reservations():
    unconfirmed_reservations = get_unconfirmed_reservations()
    for reservation in unconfirmed_reservations:
        if reservation.deadline < datetime.utcnow():
            cancel_reservation(reservation_id=reservation.id)
