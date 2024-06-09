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
    auto_booking: bool


@router.get("/{session_id}")
async def read_session(request: Request, session_id: int):
    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.get(f"/sessions/{session_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching session")
        session = response.json()
        session = format_session(session)
        response = await client.get(f"/films/{session['film_id']}")
        film = response.json()
    return templates.TemplateResponse("session.html", {"request": request, "session": session, "film": film})


@router.post("/create_session", response_class=RedirectResponse)
async def create_session(
        request: Request,
        film_id: int = Form(...),
        date: str = Form(...),
        time: str = Form(...),
        price: float = Form(...),
        capacity: int = Form(...),
        auto_booking: bool = Form(False),
):
    if not request["state"]["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    print(auto_booking)

    datetime_str = f"{date}T{time}:00.000Z"

    new_session = SessionCreate(
        film_id=film_id,
        datetime=datetime_str,
        price=price,
        capacity=capacity,
        auto_booking=auto_booking
    )

    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post("/sessions/", json=new_session.dict())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error adding session")

    return RedirectResponse(url=f"/films/{film_id}", status_code=303)


@router.post("/{session_id}/status/{new_status}")
async def change_session_status(request: Request, session_id: int, new_status: str):
    if not request.state.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")

    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post(f"/sessions/{session_id}/status/{new_status}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error changing status of session")
        session = response.json()
        print(session)

    return RedirectResponse(url=f"/films/{session['film_id']}", status_code=303)


@router.post("/change_session_price")
async def change_session_price(request: Request,
                               session_id: int = Form(...),
                               new_price: float = Form(...)):
    if not request.state.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")

    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post(f"/sessions/{session_id}/price/{new_price}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error changing status of session")
        session = response.json()

    return RedirectResponse(url=f"/sessions/{session['id']}", status_code=303)


def format_session(session):
    dt_object = datetime.fromisoformat(session["datetime"])
    session["datetime"] = dt_object.strftime("%B %d, %Y %H:%M:%S")
    session["reserved_seats"] = len([seat for seat in session["seats"] if seat["status"] == "reserved"])
    i = 1
    for seat in session["seats"]:
        seat["number"] = i
        i += 1
    return session
