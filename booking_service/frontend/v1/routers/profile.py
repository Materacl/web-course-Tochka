from fastapi import APIRouter, Request, HTTPException, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse

from ..config import settings
import httpx

router = APIRouter(
    prefix="/profile",
    tags=["profile"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="v1/templates")

@router.get("/", response_class=HTMLResponse, summary="Render the profile page", tags=["profile"])
async def read_profile(request: Request):
    """
    Render the profile page for the logged-in user.

    Args:
        request (Request): The request object.

    Returns:
        TemplateResponse: The rendered profile page template.

    Raises:
        HTTPException: If the user is not authorized to access this page.
    """
    if not request.state.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    return templates.TemplateResponse("profile.html", {"request": request})

@router.post("/change_nickname/", response_class=RedirectResponse, summary="Change user nickname", tags=["profile"])
async def change_nickname(request: Request,
                          new_nickname: str = Form(...)):
    """
    Change the nickname of the logged-in user.

    Args:
        request (Request): The request object.
        new_nickname (str): The new nickname to set.

    Returns:
        RedirectResponse: Redirects to the logout page on success.

    Raises:
        HTTPException: If the user is not authorized or an error occurs while changing the nickname.
    """
    if not request.state.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    
    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.put(f"/user/change_nickname/{new_nickname}")
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code, detail="Error changing nickname")
    return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/subscribe/", response_class=RedirectResponse, summary="Subscribe to notifications", tags=["profile"])
async def subscribe(request: Request):
    """
    Subscribe to email notifications.

    Args:
        request (Request): The request object.

    Returns:
        RedirectResponse: Redirects to the profile page on success.

    Raises:
        HTTPException: If the user is not authorized or an error occurs while subscribing.
    """
    if not request.state.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    
    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post("/email/subscribe/", headers=headers)
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code, detail="Error subscribing to notifications")
    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/unsubscribe/", response_class=RedirectResponse, summary="Unsubscribe from notifications", tags=["profile"])
async def unsubscribe(request: Request):
    """
    Unsubscribe from email notifications.

    Args:
        request (Request): The request object.

    Returns:
        RedirectResponse: Redirects to the profile page on success.

    Raises:
        HTTPException: If the user is not authorized or an error occurs while unsubscribing.
    """
    if not request.state.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    
    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.post("/email/unsubscribe/", headers=headers)
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code, detail="Error unsubscribing from notifications")
    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
