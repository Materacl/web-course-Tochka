from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, Form, UploadFile, File, Query
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.responses import RedirectResponse

from ..config import settings
import httpx

router = APIRouter(
    prefix="/sessions"
)
templates = Jinja2Templates(directory="frontend/templates")


class SessionCreate(BaseModel):
    film_id: int
    datetime: str
    price: float
    capacity: int


@router.get("/{session_id}")
async def read_session(request: Request, session_id: int):
    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.get(f"/sessions/{session_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching session")
        session = response.json()
    return templates.TemplateResponse("session.html", {"request": request, "session": session})


@router.post("/create_session", response_class=RedirectResponse)
async def create_session(
        request: Request,
        film_id: int = Form(...),
        date: str = Form(...),
        time: str = Form(...),
        price: float = Form(...),
        capacity: int = Form(...),
):
    if not request["state"]["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")

    datetime_str = f"{date}T{time}:00.000Z"

    new_session = SessionCreate(
        film_id=film_id,
        datetime=datetime_str,
        price=price,
        capacity=capacity
    )
    print(new_session.dict())
    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post("/sessions/", json=new_session.dict())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error adding session")

    return RedirectResponse(url=f"/films/{film_id}", status_code=303)
