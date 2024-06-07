from fastapi import APIRouter, Depends
from typing import List
from ..database import get_db
from ..schemas import FilmCreate, Film, SessionCreate, Session, User, Reservation
from ..crud import get_films, get_film

router = APIRouter(
    prefix="/films",
    tags=["films"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{film_id}", response_model=Film)
def read_film(film_id: int, db: Session = Depends(get_db)):
    return get_film(db, film_id)


@router.get("/", response_model=List[Film])
def read_films(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_films(db, skip=skip, limit=limit)
