import logging
from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
import httpx
from ..config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="v1/templates")


@router.get("/register", response_class=HTMLResponse, summary="Register page", tags=["auth"])
async def get_register(request: Request):
    """
    Render the registration page.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: The rendered registration page.
    """
    logger.info("Rendering the registration page")
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", summary="Register a new user", tags=["auth"])
async def post_register(request: Request, email: str = Form(...), password: str = Form(...)):
    """
    Handle user registration.

    Args:
        request (Request): The request object.
        email (str): The user's email.
        password (str): The user's password.

    Returns:
        RedirectResponse: Redirects to the login page on success.
        HTMLResponse: Renders the registration page with an error message on failure.
    """
    logger.info("Received registration request for email: %s", email)
    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.post("/auth/register", json={"email": email, "password": password})
    if response.status_code == 201:
        logger.info("User registered successfully with email: %s", email)
        return RedirectResponse(url="/auth/login", status_code=HTTP_302_FOUND)
    logger.error("Registration failed for email: %s", email)
    return templates.TemplateResponse("register.html", {"request": request, "error": "Registration failed"})


@router.get("/login", response_class=HTMLResponse, summary="Login page", tags=["auth"])
async def get_login(request: Request):
    """
    Render the login page.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: The rendered login page.
    """
    logger.info("Rendering the login page")
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", summary="User login", tags=["auth"])
async def post_login(request: Request, email: str = Form(...), password: str = Form(...)):
    """
    Handle user login.

    Args:
        request (Request): The request object.
        email (str): The user's email.
        password (str): The user's password.

    Returns:
        RedirectResponse: Redirects to the home page on success with a set cookie.
        HTMLResponse: Renders the login page with an error message on failure.
    """
    logger.info("Received login request for email: %s", email)
    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.post("/auth/token", data={"username": email, "password": password})
    if response.status_code == 200:
        token = response.json()["access_token"]
        logger.info("User logged in successfully with email: %s", email)
        redirect_response = RedirectResponse(url="/", status_code=HTTP_302_FOUND)
        redirect_response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True, secure=False)
        return redirect_response
    logger.error("Login failed for email: %s", email)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Login failed"})


@router.get("/logout", summary="User logout", tags=["auth"])
async def logout(request: Request):
    """
    Handle user logout.

    Args:
        request (Request): The request object.

    Returns:
        RedirectResponse: Redirects to the home page and clears the access token cookie.
    """
    logger.info("User logged out")
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response
