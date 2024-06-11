import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import FilmStatus
from ..schemas import FilmCreate, Film, User
from ..crud.films import get_films, get_film, create_film, delete_film, update_film_status
from ..utils.auth import get_current_active_admin
import shutil

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "v1" / "static"

router = APIRouter(
    prefix="/films",
    tags=["films"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=Film)
async def create_new_film(film: FilmCreate,
                          db: Session = Depends(get_db),
                          current_admin: User = Depends(get_current_active_admin)):
    return create_film(db=db, film=film)


@router.post("/{film_id}/upload_image")
async def upload_film_image(film_id: int, file: UploadFile = File(...),
                            db: Session = Depends(get_db),
                            current_admin: User = Depends(get_current_active_admin)):
    db_film = get_film(db, film_id)

    # Create the directory if it doesn't exist
    file_location = f"images/films/{film_id}_{file.filename}"
    db_film.image_url = file_location
    file_location = STATIC_DIR / file_location
    file_location.parent.mkdir(parents=True, exist_ok=True)

    # Save the file
    with file_location.open("wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    db.commit()
    db.refresh(db_film)
    return db_film


@router.delete("/{film_id}/delete", response_model=Film)
async def delete_film_from_db(film_id: int,
                              db: Session = Depends(get_db),
                              current_admin: User = Depends(get_current_active_admin)):
    return delete_film(db, film_id)


@router.post("/{film_id}/{new_status}", response_model=Film)
async def set_film_status(film_id: int,
                          new_status: FilmStatus,
                          db: Session = Depends(get_db),
                          current_admin: User = Depends(get_current_active_admin)):
    return update_film_status(db, film_id, new_status)


@router.get("/{film_id}", response_model=Film)
async def read_film(film_id: int, db: Session = Depends(get_db)):
    return get_film(db, film_id)


@router.get("/", response_model=List[Film])
async def read_films(skip: Optional[int] = None, limit: Optional[int] = None,
                     film_status: Optional[FilmStatus] = None,
                     db: Session = Depends(get_db)):
    return get_films(db, skip=skip, limit=limit, film_status=film_status)
