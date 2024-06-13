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
    prefix="/sessions",
    tags=["sessions"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="v1/templates")


class SessionCreate(BaseModel):
    film_id: int
    datetime: str
    price: float
    capacity: int
    auto_booking: bool


@router.get("/{session_id}", response_class=HTMLResponse, summary="Get session details", tags=["sessions"])
async def read_session(request: Request, session_id: int):
    """
    Get details of a specific session by ID.

    Args:
        request (Request): The request object.
        session_id (int): The ID of the session.

    Returns:
        TemplateResponse: The session details page.

    Raises:
        HTTPException: If an error occurs while fetching the session details.
    """
    logger.info(f"Fetching session details for session_id: {session_id}")
    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.get(f"/sessions/{session_id}")
        if response.status_code != status.HTTP_200_OK:
            logger.error(f"Error fetching session details: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Error fetching session")
        session = response.json()
        session = format_session(session)
        response = await client.get(f"/films/{session['film_id']}")
        film = response.json()
    return templates.TemplateResponse("session.html", {"request": request, "session": session, "film": film})


@router.post("/create_session", response_class=RedirectResponse, summary="Create a new session", tags=["sessions"])
async def create_session(
    request: Request,
    film_id: int = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    price: float = Form(...),
    capacity: int = Form(...),
    auto_booking: bool = Form(False),
):
    """
    Create a new session.

    Args:
        request (Request): The request object.
        film_id (int): The ID of the film for the session.
        date (str): The date of the session.
        time (str): The time of the session.
        price (float): The price of the session.
        capacity (int): The capacity of the session.
        auto_booking (bool): Whether auto booking is enabled.

    Returns:
        RedirectResponse: Redirects to the film's page on success.

    Raises:
        HTTPException: If the user is not authorized or an error occurs while creating the session.
    """
    if not request.state.is_admin:
        logger.warning(f"Unauthorized attempt to create session by user: {request.state.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")

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
    logger.info(f"Creating a new session for film_id: {film_id}")
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post("/sessions/", json=new_session.dict())
        if response.status_code != status.HTTP_201_CREATED:
            logger.error(f"Error creating session: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Error adding session")

    return RedirectResponse(url=f"/films/{film_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{session_id}/status/{new_status}", response_class=RedirectResponse, summary="Change session status", tags=["sessions"])
async def change_session_status(request: Request, session_id: int, new_status: str):
    """
    Change the status of a session.

    Args:
        request (Request): The request object.
        session_id (int): The ID of the session.
        new_status (str): The new status to set for the session.

    Returns:
        RedirectResponse: Redirects to the film's page on success.

    Raises:
        HTTPException: If the user is not authorized or an error occurs while changing the session status.
    """
    if not request.state.is_admin:
        logger.warning(f"Unauthorized attempt to change session status by user: {request.state.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")

    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    logger.info(f"Changing session status for session_id: {session_id} to new_status: {new_status}")
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post(f"/sessions/{session_id}/status/{new_status}")
        if response.status_code != status.HTTP_200_OK:
            logger.error(f"Error changing session status: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Error changing status of session")
        session = response.json()

    return RedirectResponse(url=f"/films/{session['film_id']}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/change_session_price", response_class=RedirectResponse, summary="Change session price", tags=["sessions"])
async def change_session_price(request: Request,
                               session_id: int = Form(...),
                               new_price: float = Form(...)):
    """
    Change the price of a session.

    Args:
        request (Request): The request object.
        session_id (int): The ID of the session.
        new_price (float): The new price to set for the session.

    Returns:
        RedirectResponse: Redirects to the session's page on success.

    Raises:
        HTTPException: If the user is not authorized or an error occurs while changing the session price.
    """
    if not request.state.is_admin:
        logger.warning(f"Unauthorized attempt to change session price by user: {request.state.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")

    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    logger.info(f"Changing session price for session_id: {session_id} to new_price: {new_price}")
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post(f"/sessions/{session_id}/price/{new_price}")
        if response.status_code != status.HTTP_200_OK:
            logger.error(f"Error changing session price: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Error changing status of session")
        session = response.json()

    return RedirectResponse(url=f"/sessions/{session['id']}", status_code=status.HTTP_303_SEE_OTHER)


def format_session(session):
    """
    Format session details.

    Args:
        session (dict): The session data.

    Returns:
        dict: The formatted session data.
    """
    dt_object = datetime.fromisoformat(session["datetime"])
    session["datetime"] = dt_object.strftime("%B %d, %Y %H:%M:%S")
    session["reserved_seats"] = len([seat for seat in session["seats"] if seat["status"] == "reserved"])
    for i, seat in enumerate(session["seats"], start=1):
        seat["number"] = i
    return session
