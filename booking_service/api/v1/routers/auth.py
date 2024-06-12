from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Any, Dict

from ..database import get_db
from ..schemas import UserCreate, User
from ..models import User as UserModel
from ..utils.auth import verify_password, get_password_hash
from ..utils.jwt import create_access_token
from ..config import settings
from ..crud.users import get_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED, summary="Register a new user", tags=["auth"])
async def register_user(user: UserCreate, db: Session = Depends(get_db)) -> User:
    """
    Register a new user.

    Args:
        user (UserCreate): The user registration data.
        db (Session): The database session.

    Returns:
        User: The registered user.

    Raises:
        HTTPException: If the email is already registered.
    """
    db_user = get_user(db, user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = UserModel(email=user.email, nickname="Anonym", hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/token", response_model=Dict[str, str], summary="Login for access token", tags=["auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Login for access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The login form data.
        db (Session): The database session.

    Returns:
        Dict[str, str]: The access token and token type.

    Raises:
        HTTPException: If the email or password is incorrect.
    """
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "id": user.id,
            "sub": user.email,
            "nickname": user.nickname,
            "is_admin": user.is_admin,
            "notifications": user.notifications
        }, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
