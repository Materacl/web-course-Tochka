from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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


@router.put("/users/{user_id}/set_admin", response_model=User)
def set_user_admin(email: str, db: Session = Depends(get_db)):
    return grant_user_admin(db, email)
