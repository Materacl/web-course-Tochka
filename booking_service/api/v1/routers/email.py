from fastapi import APIRouter, Depends
from fastapi_mail import MessageSchema
from sqlalchemy.orm import Session

from ..utils.email import send_notification
from ..utils.auth import get_current_active_user
from ..schemas import User
from ..crud.users import update_user_notifications
from ..database import get_db

router = APIRouter(
    prefix="/email",
    tags=["email"],
    responses={404: {"description": "Not found"}},
)


@router.post("/subscribe/")
async def subscribe(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    update_user_notifications(db, current_user.id, True)
    message = MessageSchema(
        subject="Subscription Confirmation",
        recipients=[current_user.email],
        body="You have successfully subscribed to notifications.",
        subtype="html"
    )
    await send_notification(message)
    return {"message": "Subscription successful"}


@router.post("/unsubscribe/")
async def subscribe(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    update_user_notifications(db, current_user.id, False)
    message = MessageSchema(
        subject="Unsubscribe Confirmation",
        recipients=[current_user.email],
        body="You have successfully unsubscribed from notifications.",
        subtype="html"
    )
    await send_notification(message)
    return {"message": "Unsubscribe successful"}
