from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, Form, UploadFile, File, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.responses import RedirectResponse, HTMLResponse
import logging
import httpx

from ..config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/payment",
    tags=["payment"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="v1/templates")


@router.get("/{booking_id}/pay", response_class=HTMLResponse, summary="Show payment page")
async def show_payment_page(request: Request, booking_id: int):
    """
    Show the payment page for a booking.

    Args:
        request (Request): The request object.
        booking_id (int): The ID of the booking.

    Returns:
        TemplateResponse: The payment page.
    """
    try:
        token = request.cookies.get("access_token")
        headers = {"Authorization": token}
        async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
            response = await client.post(f"/payments/create-payment-intent", json={"booking_id": booking_id})
            if response.status_code != status.HTTP_200_OK:
                logger.error(f"Failed to fetch payment for booking_id: {booking_id}")
                raise HTTPException(status_code=response.status_code, detail="Error fetching payment for booking")
            intent = response.json()
            if not intent:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

        client_secret = intent['client_secret']
        response = await client.get(f"/bookings/{booking_id}")
        if response.status_code != status.HTTP_200_OK:
            logger.error("Failed to fetch booking details for booking_id: %s", booking_id)
            HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error fetching booking for this payment")
        db_booking = response.json()
        return templates.TemplateResponse("payment.html", {"request": request, "client_secret": client_secret,
                                                           "booking": db_booking})
    except Exception as e:
        logger.error(f"Error showing payment page: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error showing payment page")
