from datetime import datetime
from pathlib import Path
import shutil
import logging

from fastapi import APIRouter, Request, HTTPException, Form, UploadFile, File, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel

from ..config import settings
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/films",
    tags=["films"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="v1/templates")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "static"

@router.get("/{page}/{limit}", response_class=HTMLResponse, summary="Get films list", tags=["films"])
async def read_films(request: Request, page: int = 1, limit: int = 12):
    """
    Get a list of films with pagination.

    Args:
        request (Request): The request object.
        page (int): The current page number.
        limit (int): The number of films per page.

    Returns:
        TemplateResponse: The films list page.
    """
    logger.info(f"Fetching films for page {page} with limit {limit}")
    skip = (page - 1) * limit
    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.get("/films/", params={"skip": skip, "limit": limit})
        if response.status_code != status.HTTP_200_OK:
            logger.error(f"Failed to fetch films: {response.status_code}")
            films = []
            total_films = 0
        else:
            films = response.json()
            response = await client.get("/films/")
            total_films = len(response.json())

    return templates.TemplateResponse("films.html", {
        "request": request,
        "films": films,
        "page": page,
        "limit": limit,
        "total_films": total_films
    })


@router.get("/{film_id}", response_class=HTMLResponse, summary="Get film details", tags=["films"])
async def read_film(request: Request, film_id: int):
    """
    Get details of a specific film by ID.

    Args:
        request (Request): The request object.
        film_id (int): The ID of the film.

    Returns:
        TemplateResponse: The film details page.
    """
    logger.info(f"Fetching details for film_id {film_id}")
    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.get(f"/films/{film_id}")
        if response.status_code != status.HTTP_200_OK:
            logger.error(f"Failed to fetch film details: {response.status_code}")
            film = None
        else:
            film = response.json()
            if film["status"] == "not_available":
                film = None
            else:
                film = format_sessions(film)
    return templates.TemplateResponse("film.html", {"request": request, "film": film})


class FilmCreate(BaseModel):
    title: str
    description: str
    duration: int
    status: str


@router.post("/add_film", response_class=RedirectResponse, summary="Add a new film", tags=["films"])
async def add_film(
        request: Request,
        title: str = Form(...),
        description: str = Form(...),
        image: UploadFile = File(...),
        duration: int = Form(...),
        film_status: str = Form(...),
):
    """
    Add a new film.

    Args:
        request (Request): The request object.
        title (str): The title of the film.
        description (str): The description of the film.
        image (UploadFile): The image file for the film.
        duration (int): The duration of the film in minutes.
        film_status (str): The status of the film.

    Returns:
        RedirectResponse: Redirects to the films list page on success.

    Raises:
        HTTPException: If the user is not authorized or an error occurs.
    """
    logger.info(f"Attempting to add a new film: {title}")
    if not request.state.is_admin:
        logger.warning("Unauthorized add film attempt")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")

    new_film = FilmCreate(
        title=title,
        description=description,
        duration=duration,
        status=film_status
    )

    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post("/films/", json=new_film.dict())
        if response.status_code != status.HTTP_201_CREATED:
            logger.error(f"Failed to add film: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error adding film")

        film_id = response.json()["id"]
        files = {"file": (image.filename, image.file, image.content_type)}
        response = await client.post(f"/films/{film_id}/upload_image", files=files)
        if response.status_code != status.HTTP_200_OK:
            logger.error(f"Failed to upload image for film: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error adding image to film")
        
        # Create the directory if it doesn't exist
        file_location = f"images/films/{film_id}_{image.filename}"
        file_location = STATIC_DIR / file_location
        file_location.parent.mkdir(parents=True, exist_ok=True)

        # Save the file
        with file_location.open("wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        logger.info(f"Image {image.filename} saved to {file_location}")

    logger.info(f"Successfully added film: {title}")
    return RedirectResponse(url="/films/1/12", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{film_id}/update_status", response_class=RedirectResponse, summary="Update film status", tags=["films"])
async def update_film_status(
        request: Request,
        film_id: int,
        new_status: str = Form(...),
):
    """
    Update the status of a film.

    Args:
        request (Request): The request object.
        film_id (int): The ID of the film.
        new_status (str): The new status to set for the film.

    Returns:
        RedirectResponse: Redirects to the films list page on success.

    Raises:
        HTTPException: If the user is not authorized or an error occurs.
    """
    logger.info(f"Attempting to update status of film_id {film_id} to {new_status}")
    if not request.state.is_admin:
        logger.warning("Unauthorized status update attempt")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")

    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post(f"/films/{film_id}/status/{new_status}")
        if response.status_code != status.HTTP_200_OK:
            logger.error(f"Failed to update status for film_id {film_id}: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error changing film status")

    logger.info(f"Successfully updated status of film_id {film_id} to {new_status}")
    return RedirectResponse(url="/films/1/12", status_code=status.HTTP_303_SEE_OTHER)


def format_sessions(film):
    """
    Format session details within a film.

    Args:
        film (dict): The film data.

    Returns:
        dict: The film data with formatted session details.
    """
    logger.info(f"Formatting sessions for film_id {film.get('id')}")
    for session in film.get("sessions", []):
        dt_object = datetime.fromisoformat(session["datetime"])
        session["datetime"] = dt_object.strftime("%B %d, %Y %H:%M:%S")
        session["reserved_seats"] = len([seat for seat in session["seats"] if seat["status"] == "reserved"])
    return film
