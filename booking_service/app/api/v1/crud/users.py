from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..models import User
from ..schemas import UserCreate


def create_user(db: Session, user: UserCreate):
    db_user = User(email=user.email, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_nickname(db: Session, user_id: int, new_nickname: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db_user.nickname = new_nickname
    db.commit()
    db.refresh(db_user)
    return db_user


def grant_user_admin(db: Session, email: str):
    db_user = get_user(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.is_admin = True
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, email: str):
    db_user = db.query(User).filter(User.email == email).first()
    return db_user
