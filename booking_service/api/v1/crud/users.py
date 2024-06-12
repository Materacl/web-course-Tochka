from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status
import logging

from ..models import User
from ..schemas import UserCreate

# Initialize logger
logger = logging.getLogger(__name__)

def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user.

    Args:
        db (Session): The database session.
        user (UserCreate): The user creation schema.

    Returns:
        User: The created user.
    """
    logger.info(f"Creating a new user with email: {user.email}")
    db_user = User(email=user.email, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User created with id {db_user.id}")
    return db_user

def update_user_nickname(db: Session, user_id: int, new_nickname: str) -> User:
    """
    Update a user's nickname.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to update.
        new_nickname (str): The new nickname for the user.

    Returns:
        User: The updated user.

    Raises:
        HTTPException: If the user is not found.
    """
    logger.info(f"Updating nickname for user id {user_id}")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.error(f"User with id {user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db_user.nickname = new_nickname
    db.commit()
    db.refresh(db_user)
    logger.info(f"Nickname for user id {user_id} updated to {new_nickname}")
    return db_user

def update_user_notifications(db: Session, user_id: int, new_notifications: bool) -> User:
    """
    Update a user's notification settings.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to update.
        new_notifications (bool): The new notification setting for the user.

    Returns:
        User: The updated user.

    Raises:
        HTTPException: If the user is not found.
    """
    logger.info(f"Updating notifications for user id {user_id}")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.error(f"User with id {user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db_user.notifications = new_notifications
    db.commit()
    db.refresh(db_user)
    logger.info(f"Notifications for user id {user_id} updated to {new_notifications}")
    return db_user

def grant_user_admin(db: Session, email: str) -> User:
    """
    Grant admin privileges to a user.

    Args:
        db (Session): The database session.
        email (str): The email of the user to update.

    Returns:
        User: The updated user.

    Raises:
        HTTPException: If the user is not found.
    """
    logger.info(f"Granting admin privileges to user with email {email}")
    db_user = get_user(db, email)
    if not db_user:
        logger.error(f"User with email {email} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db_user.is_admin = True
    db.commit()
    db.refresh(db_user)
    logger.info(f"Admin privileges granted to user with email {email}")
    return db_user

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieve a user by their ID.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to retrieve.

    Returns:
        Optional[User]: The retrieved user, or None if not found.
    """
    logger.info(f"Retrieving user with id {user_id}")
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        logger.info(f"User with id {user_id} found")
    else:
        logger.info(f"User with id {user_id} not found")
    return db_user

def get_user(db: Session, email: str) -> Optional[User]:
    """
    Retrieve a user by their email.

    Args:
        db (Session): The database session.
        email (str): The email of the user to retrieve.

    Returns:
        Optional[User]: The retrieved user, or None if not found.
    """
    logger.info(f"Retrieving user with email {email}")
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        logger.info(f"User with email {email} found")
    else:
        logger.info(f"User with email {email} not found")
    return db_user
