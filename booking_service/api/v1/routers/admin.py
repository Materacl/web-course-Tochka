from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from ..database import get_db
from ..models import User as UserModel
from ..schemas import User
from ..utils.auth import get_current_active_admin
from ..crud.users import grant_user_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_current_active_admin)]
)

@router.put("/users/{user_email}/set_admin", response_model=User, status_code=status.HTTP_200_OK)
async def set_user_admin(user_email: str, db: Session = Depends(get_db)) -> Any:
    """
    Grant admin privileges to a user.

    Args:
        user_email (str): The email of the user to grant admin privileges to.
        db (Session): The database session.

    Returns:
        User: The updated user with admin privileges.
    """
    return grant_user_admin(db, user_email)
