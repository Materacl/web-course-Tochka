from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from ..config import settings
import httpx

router = APIRouter(
    prefix="/bookings"
)
templates = Jinja2Templates(directory="frontend/templates")


@router.get("/")
async def read_bookings(request: Request):
    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.get("/bookings/current_user/", params={"skip": 0, "limit": 10})
        if response.status_code != 200:
            bookings = []
        else:
            bookings = response.json()

        for booking in bookings:
            response = await client.get(f"/sessions/{booking.get('session_id')}")
            booking["session"] = response.json()

    return templates.TemplateResponse("bookings.html", {
        "request": request,
        "bookings": bookings,
    })
