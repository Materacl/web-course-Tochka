import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil

from ..database import get_db
from ..models import FilmStatus
from ..schemas import FilmCreate, Film, User
from ..crud.films import get_films, get_film, create_film, delete_film, update_film_status
from ..utils.auth import get_current_active_admin

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "static"

router = APIRouter(
    prefix="/films",
    tags=["films"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Film, status_code=status.HTTP_201_CREATED, summary="Create a new film", tags=["films"])
async def create_new_film(
    film: FilmCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
) -> Film:
    """
    Create a new film.

    Args:
        film (FilmCreate): The film creation data.
        db (Session): The database session.
        current_admin (User): The current active admin.

    Returns:
        Film: The created film.
    """
    return create_film(db=db, film=film)

@router.post("/{film_id}/upload_image", response_model=Film, status_code=status.HTTP_200_OK, summary="Upload film image", tags=["films"])
async def upload_film_image(
    film_id: int, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
) -> Film:
    """
    Upload an image for a film.

    Args:
        film_id (int): The ID of the film.
        file (UploadFile): The image file to upload.
        db (Session): The database session.
        current_admin (User): The current active admin.

    Returns:
        Film: The updated film with the image URL.
    """
    db_film = get_film(db, film_id)
    if not db_film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film not found")

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

@router.delete("/{film_id}/delete", response_model=Film, status_code=status.HTTP_200_OK, summary="Delete a film", tags=["films"])
async def delete_film_from_db(
    film_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
) -> Film:
    """
    Delete a film by ID.

    Args:
        film_id (int): The ID of the film to delete.
        db (Session): The database session.
        current_admin (User): The current active admin.

    Returns:
        Film: The deleted film.
    """
    return delete_film(db, film_id)

@router.post("/{film_id}/status/{new_status}", response_model=Film, status_code=status.HTTP_200_OK, summary="Set film status", tags=["films"])
async def set_film_status(
    film_id: int,
    new_status: FilmStatus,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
) -> Film:
    """
    Set the status of a film.

    Args:
        film_id (int): The ID of the film.
        new_status (FilmStatus): The new status to set.
        db (Session): The database session.
        current_admin (User): The current active admin.

    Returns:
        Film: The updated film with the new status.
    """
    return update_film_status(db, film_id, new_status)

@router.get("/{film_id}", response_model=Film, status_code=status.HTTP_200_OK, summary="Get a film by ID", tags=["films"])
async def read_film(film_id: int, db: Session = Depends(get_db)) -> Film:
    """
    Get a film by its ID.

    Args:
        film_id (int): The ID of the film to retrieve.
        db (Session): The database session.

    Returns:
        Film: The film with the given ID.
    """
    return get_film(db, film_id)

@router.get("/", response_model=List[Film], status_code=status.HTTP_200_OK, summary="Get films with optional filters", tags=["films"])
async def read_films(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    film_status: Optional[FilmStatus] = None,
    db: Session = Depends(get_db)
) -> List[Film]:
    """
    Get a list of films with optional filters.

    Args:
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.
        film_status (Optional[FilmStatus]): Filter by film status.
        db (Session): The database session.

    Returns:
        List[Film]: A list of films.
    """
    return get_films(db, skip=skip, limit=limit, film_status=film_status)
