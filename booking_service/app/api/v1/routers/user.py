from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..database import get_db
from ..utils.auth import get_current_active_user
from ..schemas import User
from ..crud.users import update_user_nickname

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.put("/change_nickname/{new_nickname}", response_model=User)
async def change_nickname(new_nickname: str,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_active_user)):
    return update_user_nickname(db, current_user.id, new_nickname)
