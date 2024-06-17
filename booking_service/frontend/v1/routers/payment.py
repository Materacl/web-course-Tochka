import logging
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse
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


@router.get("/{booking_id}/pay", summary="Redirect to Stripe Checkout", tags=["payment"])
async def pay_booking(request: Request, booking_id: int):
    """
    Redirect to Stripe Checkout for a specific booking.

    Args:
        request (Request): The request object.
        booking_id (int): The ID of the booking.

    Returns:
        RedirectResponse: Redirects to the Stripe Checkout Session URL.

    Raises:
        HTTPException: If an error occurs while creating the Checkout Session.
    """
    logger.info(f"Creating Checkout Session for booking_id: {booking_id}")
    try:
        token = request.cookies.get("access_token")
        headers = {"Authorization": token}
        async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
            response = await client.post("/payments/create-checkout-session", json={"booking_id": booking_id})
            if response.status_code != status.HTTP_201_CREATED:
                logger.error(f"Error creating Checkout Session: {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error creating Checkout Session")
            checkout_url = response.json()["checkout_url"]
    except Exception as e:
        logger.error(f"Error redirecting to Checkout Session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error redirecting to Checkout Session")

    return RedirectResponse(url=checkout_url)
