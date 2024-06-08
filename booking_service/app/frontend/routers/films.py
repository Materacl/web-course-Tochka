from fastapi import APIRouter, Request, HTTPException, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.responses import RedirectResponse

from ..config import settings
import httpx

router = APIRouter(
    prefix="/films"
)
templates = Jinja2Templates(directory="frontend/templates")


@router.get("/")
async def read_films(request: Request):
    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.get("/films/",
                                    params={"skip": 0, "limit": 10})
        if response.status_code != 200:
            films = []
        else:
            films = response.json()
    return templates.TemplateResponse("films.html", {"request": request, "films": films})


@router.get("/{film_id}")
async def read_film(request: Request, film_id: int):
    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.get(f"/films/{film_id}")
        if response.status_code != 200:
            film = None
            sessions = None
        else:
            film = response.json()
            if film["status"] == "not_available":
                film = None
                sessions = None
            else:
                film = add_capacity_to_sessions(film)
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

    return RedirectResponse(url="/films", status_code=303)


def add_capacity_to_sessions(film):
    for session in film.get("sessions", []):
        session["capacity"] = len(session["seats"])
    return film
