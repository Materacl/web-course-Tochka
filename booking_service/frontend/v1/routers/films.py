from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, Form, UploadFile, File, Query
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.responses import RedirectResponse

from ..config import settings
import httpx

router = APIRouter(
    prefix="/films"
)
templates = Jinja2Templates(directory="v1/templates")


@router.get("/{page}/{limit}")
async def read_films(request: Request, page: int = 1, limit: int = 12):
    skip = (page - 1) * limit
    limit = skip + 12
    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.get("/films/", params={"skip": skip, "limit": limit})
        if response.status_code != 200:
            films = []
            total_films = 0
        else:
            films = response.json()
            response = await client.get("/films/")
            total_films = len(response.json())

    return templates.TemplateResponse("films.html", {"request": request,
                                                     "films": films,
                                                     "page": page,
                                                     "limit": limit,
                                                     "total_films": total_films})


@router.get("/{film_id}")
async def read_film(request: Request, film_id: int):
    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.get(f"/films/{film_id}")
        if response.status_code != 200:
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


@router.post("/add_film", response_class=RedirectResponse)
async def add_film(
        request: Request,
        title: str = Form(...),
        description: str = Form(...),
        image: UploadFile = File(...),
        duration: int = Form(...),
        status: str = Form(...),
):
    if not request["state"]["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")

    new_film = FilmCreate(
        title=title,
        description=description,
        duration=duration,
        status=status
    )

    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post("/films/", json=new_film.dict())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error adding film")

        film_id = response.json()["id"]
        files = {"file": (image.filename, image.file, image.content_type)}
        response = await client.post(f"/films/{film_id}/upload_image", files=files)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error adding image to film")

    return RedirectResponse(url="/films/1/12", status_code=303)


@router.post("/{film_id}/update_status", response_class=RedirectResponse)
async def update_film_status(
        request: Request,
        film_id: int,
        new_status: str = Form(...),
):
    if not request["state"]["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")

    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post(f"/films/{film_id}/{new_status}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error changing film status")
    return RedirectResponse(url="/films/1/12", status_code=303)


def format_sessions(film):
    for session in film.get("sessions", []):
        dt_object = datetime.fromisoformat(session["datetime"])
        session["datetime"] = dt_object.strftime("%B %d, %Y %H:%M:%S")
        session["reserved_seats"] = len([seat for seat in session["seats"] if seat["status"] == "reserved"])
    return film
