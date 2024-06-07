from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
import httpx

router = APIRouter(
    prefix="/films"
)
templates = Jinja2Templates(directory="frontend/templates")


@router.get("/")
async def read_films(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/films/",
                                    params={"skip": 0, "limit": 10})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching films")
        films = response.json()
    return templates.TemplateResponse("films.html", {"request": request, "films": films})
