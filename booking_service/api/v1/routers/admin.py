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

@router.put("/users/{user_id}/set_admin", response_model=User, status_code=status.HTTP_200_OK)
async def set_user_admin(user_id: int, db: Session = Depends(get_db)) -> Any:
    """
    Grant admin privileges to a user.

    Args:
        user_id (int): The ID of the user to grant admin privileges to.
        db (Session): The database session.

    Returns:
        User: The updated user with admin privileges.

    Raises:
        HTTPException: If the user is not found.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    grant_user_admin(db, user.email)
    return user
