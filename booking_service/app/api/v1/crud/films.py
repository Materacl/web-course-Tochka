from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..models import Film, FilmStatus, SessionStatus
from ..schemas import FilmCreate
from .sessions import update_session_status


def create_film(db: Session, film: FilmCreate):
    db_film = Film(**film.dict())
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    return db_film


def delete_film(db: Session, film_id: int):
    db_film = db.query(Film).filter(Film.id == film_id).first()
    db.delete(db_film)
    db.commit()
    return db_film


def update_film_status(db: Session, film_id: int, new_status: FilmStatus):
    db_film = get_film(db, film_id)

    db_film.status = new_status
    if new_status == FilmStatus.NOT_AVAILABLE:
        for session in db_film.sessions:
            update_session_status(db, session_id=session.id, new_status=SessionStatus.CANCELED)
    db.commit()

    return db_film


def get_film(db: Session, film_id: int):
    db_film = db.query(Film).filter(Film.id == film_id).first()
    if not db_film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film not found")
    return db_film


def get_films(db: Session,
              skip: Optional[int] = None, limit: Optional[int] = None,
              film_status: Optional[FilmStatus] = None):
    query = db.query(Film)

    if film_status is not None:
        query = query.filter(Film.status == film_status)

    if limit is not None:
        query = query.limit(limit)

    if skip is not None:
        query = query.offset(skip)
    return query.all()
