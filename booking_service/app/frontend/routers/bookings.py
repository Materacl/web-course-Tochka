from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from ..config import settings
import httpx

router = APIRouter(
    prefix="/bookings"
)
templates = Jinja2Templates(directory="frontend/templates")


@router.post("/create", response_class=RedirectResponse)
async def create_booking(
        request: Request,
        session_id: int = Form(...),
        seat_ids: str = Form(...),
):
    if not request.state.email:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")

    seat_ids = list(map(int, seat_ids.split(',')))
    if len(seat_ids) < 1:
        raise HTTPException(status_code=403, detail="No seats selected")

    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post("/bookings/", json={"session_id": session_id})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error adding booking")
        booking = response.json()
        for seat_id in seat_ids:
            response = await client.post("/reservations/", json={"booking_id": booking["id"], "seat_id": seat_id})
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error adding reservation")

    return RedirectResponse(url=f"/sessions/{session_id}", status_code=303)


@router.get("/{booking_id}")
async def read_booking(request: Request, booking_id: int):
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


@router.post("/{booking_id}/{new_status}")
async def change_booking_status(request: Request, booking_id: int, new_status: str):
    if new_status not in ["confirmed", "canceled"]:
        raise HTTPException(status_code=403, detail="Incorrect booking status")

    if request.state.is_admin:
        token = request.cookies.get("access_token")
        headers = {"Authorization": token}
        async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
            response = await client.post(f"/bookings/{booking_id}/{new_status}")
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error changing status of booking")
            booking = response.json()
    elif request.state.email and new_status == "canceled":
        token = request.cookies.get("access_token")
        headers = {"Authorization": token}
        async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
            response = await client.get(f"/bookings/{booking_id}")
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error getting booking")
            if response.json()["user_id"] != request.state.user_id:
                raise HTTPException(status_code=403, detail="Not authorized to perform this action")

            response = await client.post(f"/bookings/{booking_id}")
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error canceling booking")
            booking = response.json()
    else:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")

    return RedirectResponse(url=f"/sessions/{booking['session_id']}", status_code=303)
