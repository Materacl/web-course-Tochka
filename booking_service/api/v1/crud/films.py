from typing import Optional, List
import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..models import Film, FilmStatus, SessionStatus
from ..schemas import FilmCreate
from .sessions import update_session_status

# Initialize logger
logger = logging.getLogger(__name__)

def create_film(db: Session, film: FilmCreate) -> Film:
    """
    Create a new film.

    Args:
        db (Session): The database session.
        film (FilmCreate): The film creation schema.

    Returns:
        Film: The created film.
    """
    logger.info(f"Creating a new film with title: {film.title}")
    db_film = Film(**film.dict())
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    logger.info(f"Film created with id {db_film.id}")
    return db_film

def delete_film(db: Session, film_id: int) -> Film:
    """
    Delete a film by its ID.

    Args:
        db (Session): The database session.
        film_id (int): The ID of the film to delete.

    Returns:
        Film: The deleted film.
    """
    logger.info(f"Deleting film with id {film_id}")
    db_film = get_film(db, film_id)

    db.delete(db_film)
    db.commit()
    logger.info(f"Film with id {film_id} deleted")
    return db_film

def update_film_status(db: Session, film_id: int, new_status: FilmStatus) -> Film:
    """
    Update the status of a film.

    Args:
        db (Session): The database session.
        film_id (int): The ID of the film to update.
        new_status (FilmStatus): The new status of the film.

    Returns:
        Film: The updated film.
    """
    logger.info(f"Updating status of film id {film_id} to {new_status}")
    db_film = get_film(db, film_id)

    db_film.status = new_status
    if new_status == FilmStatus.NOT_AVAILABLE:
        for session in db_film.sessions:
            update_session_status(db, session_id=session.id, new_status=SessionStatus.CANCELED)
    db.commit()
    logger.info(f"Status of film id {film_id} updated to {new_status}")
    return db_film

def get_film(db: Session, film_id: int) -> Film:
    """
    Retrieve a film by its ID.

    Args:
        db (Session): The database session.
        film_id (int): The ID of the film to retrieve.

    Returns:
        Film: The retrieved film.

    Raises:
        HTTPException: If the film is not found.
    """
    logger.info(f"Retrieving film with id {film_id}")
    db_film = db.query(Film).filter(Film.id == film_id).first()
    if not db_film:
        logger.error(f"Film with id {film_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film not found")
    return db_film

def get_films(db: Session, skip: Optional[int] = None, limit: Optional[int] = None,
              film_status: Optional[FilmStatus] = None) -> List[Film]:
    """
    Retrieve a list of films with optional filters.

    Args:
        db (Session): The database session.
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.
        film_status (Optional[FilmStatus]): Filter by film status.

    Returns:
        List[Film]: A list of films.
    """
    logger.info(f"Retrieving films with filters - skip: {skip}, limit: {limit}, film_status: {film_status}")
    query = db.query(Film)

    if film_status is not None:
        query = query.filter(Film.status == film_status)

    if limit is not None:
        query = query.limit(limit)

    if skip is not None:
        query = query.offset(skip)

    films = query.all()
    logger.info(f"Retrieved {len(films)} films")
    return films
