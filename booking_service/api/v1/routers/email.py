from fastapi import APIRouter, Depends, HTTPException, status
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

@router.post("/subscribe/", status_code=status.HTTP_200_OK, summary="Subscribe to email notifications", tags=["email"])
async def subscribe(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Subscribe the current user to email notifications.

    Args:
        db (Session): The database session.
        current_user (User): The current active user.

    Returns:
        dict: A success message.
    """
    try:
        update_user_notifications(db, current_user.id, True)
        message = MessageSchema(
            subject="Subscription Confirmation",
            recipients=[current_user.email],
            body="You have successfully subscribed to notifications.",
            subtype="html"
        )
        await send_notification(message)
        return {"message": "Subscription successful"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/unsubscribe/", status_code=status.HTTP_200_OK, summary="Unsubscribe from email notifications", tags=["email"])
async def unsubscribe(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Unsubscribe the current user from email notifications.

    Args:
        db (Session): The database session.
        current_user (User): The current active user.

    Returns:
        dict: A success message.
    """
    try:
        update_user_notifications(db, current_user.id, False)
        message = MessageSchema(
            subject="Unsubscribe Confirmation",
            recipients=[current_user.email],
            body="You have successfully unsubscribed from notifications.",
            subtype="html"
        )
        await send_notification(message)
        return {"message": "Unsubscribe successful"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    