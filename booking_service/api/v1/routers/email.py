from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils.auth import get_current_active_user
from ..schemas import User
from ..crud.users import update_user_notifications
from ..utils.rabbitmq import publish_message

router = APIRouter(
    prefix="/email",
    tags=["email"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/subscribe/",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Subscribe to Email Notifications",
    description="Subscribe the current user to email notifications.",
    tags=["email"],
    responses={
        status.HTTP_200_OK: {
            "description": "Subscription successful.",
            "content": {
                "application/json": {
                    "example": {"message": "Subscription successful"}
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "An error occurred while updating the user notifications.",
            "content": {
                "application/json": {
                    "example": {"detail": "An error occurred"}
                }
            }
        }
    },
)
async def subscribe(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Subscribe the current user to email notifications.

    Args:
        db (Session): Database session.
        current_user (User): The current active user.

    Returns:
        dict: A message indicating the subscription was successful.

    Raises:
        HTTPException: If there is an error updating the user notifications.
    """
    try:
        update_user_notifications(db, current_user.id, True)
        await publish_message('email_notifications', f"subscribe:{current_user.email}")
        return {"message": "Subscription successful"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post(
    "/unsubscribe/",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Unsubscribe from Email Notifications",
    description="Unsubscribe the current user from email notifications.",
    tags=["email"],
    responses={
        status.HTTP_200_OK: {
            "description": "Unsubscription successful.",
            "content": {
                "application/json": {
                    "example": {"message": "Unsubscribe successful"}
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "An error occurred while updating the user notifications.",
            "content": {
                "application/json": {
                    "example": {"detail": "An error occurred"}
                }
            }
        }
    },
)
async def unsubscribe(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Unsubscribe the current user from email notifications.

    Args:
        db (Session): Database session.
        current_user (User): The current active user.

    Returns:
        dict: A message indicating the unsubscription was successful.

    Raises:
        HTTPException: If there is an error updating the user notifications.
    """
    try:
        update_user_notifications(db, current_user.id, False)
        await publish_message('email_notifications', f"unsubscribe:{current_user.email}")
        return {"message": "Unsubscribe successful"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
