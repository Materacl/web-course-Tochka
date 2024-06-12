from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..utils.auth import get_current_active_user
from ..schemas import User
from ..crud.users import update_user_nickname

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

@router.put("/change_nickname/{new_nickname}", response_model=User, status_code=status.HTTP_200_OK, summary="Change user nickname", tags=["user"])
async def change_nickname(
    new_nickname: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Change the nickname of the current user.

    Args:
        new_nickname (str): The new nickname to set.
        db (Session): The database session.
        current_user (User): The current active user.

    Returns:
        User: The updated user with the new nickname.
    """
    return update_user_nickname(db, current_user.id, new_nickname)