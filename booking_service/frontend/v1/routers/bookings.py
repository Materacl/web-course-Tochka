from fastapi import APIRouter, Request, HTTPException, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx

from ..config import settings

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="frontend/templates")

@router.post("/", response_class=RedirectResponse, summary="Create a new booking", tags=["bookings"])
async def create_booking(
    request: Request,
    session_id: int = Form(...),
    seat_ids: str = Form(...),
):
    """
    Create a new booking.

    Args:
        request (Request): The request object.
        session_id (int): The ID of the session to book.
        seat_ids (str): A comma-separated string of seat IDs.

    Returns:
        RedirectResponse: Redirects to the session page on success.

    Raises:
        HTTPException: If the user is not authorized or an error occurs.
    """
    if not request.state.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")

    seat_ids = list(map(int, seat_ids.split(',')))
    if len(seat_ids) < 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No seats selected")

    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post("/bookings/", json={"session_id": session_id})
        if response.status_code != status.HTTP_201_CREATED:
            raise HTTPException(status_code=response.status_code, detail="Error adding booking")
        booking = response.json()
        for seat_id in seat_ids:
            response = await client.post("/reservations/", json={"booking_id": booking["id"], "seat_id": seat_id})
            if response.status_code != status.HTTP_201_CREATED:
                raise HTTPException(status_code=response.status_code, detail="Error adding reservation")

    return RedirectResponse(url=f"/sessions/{session_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/{booking_id}", response_class=HTMLResponse, summary="Get booking details", tags=["bookings"])
async def read_booking(request: Request, booking_id: int):
    """
    Get booking details by ID.

    Args:
        request (Request): The request object.
        booking_id (int): The ID of the booking to retrieve.

    Returns:
        TemplateResponse: The booking details page.
    """
    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.get(f"/bookings/{booking_id}")
        if response.status_code != status.HTTP_200_OK:
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

@router.post("/{booking_id}/{new_status}", summary="Change booking status", tags=["bookings"])
async def change_booking_status(request: Request, booking_id: int, new_status: str):
    """
    Change the status of a booking.

    Args:
        request (Request): The request object.
        booking_id (int): The ID of the booking to change status.
        new_status (str): The new status to set (confirmed or canceled).

    Returns:
        RedirectResponse: Redirects to the session page on success.

    Raises:
        HTTPException: If the status is invalid or the user is not authorized.
    """
    if new_status not in ["confirmed", "canceled"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect booking status")

    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        if request.state.is_admin:
            response = await client.post(f"/bookings/{booking_id}/{new_status}")
            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(status_code=response.status_code, detail="Error changing status of booking")
            booking = response.json()
        elif request.state.email and new_status == "canceled":
            response = await client.get(f"/bookings/{booking_id}")
            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(status_code=response.status_code, detail="Error getting booking")
            if response.json()["user_id"] != request.state.user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")

            response = await client.post(f"/bookings/{booking_id}")
            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(status_code=response.status_code, detail="Error canceling booking")
            booking = response.json()
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")

    return RedirectResponse(url=f"/sessions/{booking['session_id']}", status_code=status.HTTP_303_SEE_OTHER)
