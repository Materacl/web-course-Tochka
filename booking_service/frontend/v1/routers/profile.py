from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, Form, UploadFile, File, Query
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.responses import RedirectResponse

from ..config import settings
import httpx

router = APIRouter(
    prefix="/profile"
)
templates = Jinja2Templates(directory="v1/templates")


@router.get("/")
async def read_profile(request: Request):
    if not request.state.email:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    return templates.TemplateResponse("profile.html", {"request": request})


@router.post("/change_nickname/")
async def change_nickname(request: Request,
                          new_nickname: str = Form(...)):
    if not request.state.email:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    
    token = request.cookies.get("access_token")
    headers = {"Authorization": token}
    async with httpx.AsyncClient(base_url=settings.API_URL, headers=headers) as client:
        response = await client.put(f"/user/change_nickname/{new_nickname}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error changing nickname")
    return RedirectResponse(url="/auth/logout", status_code=303)
