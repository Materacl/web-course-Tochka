from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import CinemaHall
from app.crud import get_cinema_hall, get_cinema_halls

router = APIRouter(
    prefix="/cinema_halls",
    tags=["cinema_halls"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{cinema_hall_id}", response_model=CinemaHall)
def read_cinema_hall(cinema_hall_id: int, db: Session = Depends(get_db)):
    return get_cinema_hall(db, cinema_hall_id)


@router.get("/", response_model=List[CinemaHall])
def read_cinema_halls(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_cinema_halls(db, skip=skip, limit=limit)
