from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
import httpx

router = APIRouter(
    prefix="/sessions"
)
templates = Jinja2Templates(directory="frontend/templates")


@router.get("/")
async def read_films(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/sessions/",
                                    params={"skip": 0, "limit": 10})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching sessions")
        sessions = response.json()
    return templates.TemplateResponse("films.html", {"request": request, "sessions": sessions})
