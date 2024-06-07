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
            booking["reservations_amount"] = len(booking["reservations"])

    return templates.TemplateResponse("bookings.html", {
        "request": request,
        "bookings": bookings,
    })


@router.get("/{booking_id}")
async def read_bookings(request: Request, booking_id: int):
    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.get(f"/bookings/{booking_id}")
        if response.status_code != 200:
            booking = None
        else:
            booking = response.json()
            response = await client.get(f"/sessions/{booking.get('session_id')}")
            booking["session"] = response.json()
            booking["reservations_amount"] = len(booking["reservations"])

    return templates.TemplateResponse("booking.html", {
        "request": request,
        "booking": booking
    })
