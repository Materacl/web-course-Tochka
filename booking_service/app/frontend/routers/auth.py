# frontend/routers/auth.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
import httpx

router = APIRouter()
templates = Jinja2Templates(directory="app/frontend/templates")


@router.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def post_register(request: Request, email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://127.0.0.1:8000/api/v1/auth/register",
                                     json={"email": email, "password": password})
    if response.status_code == 200:
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    return templates.TemplateResponse("register.html", {"request": request, "error": "Registration failed"})


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def post_login(request: Request, email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://127.0.0.1:8000/api/v1/auth/token",
                                     data={"username": email, "password": password})
    if response.status_code == 200:
        token = response.json()["access_token"]
        response = RedirectResponse(url="/", status_code=HTTP_302_FOUND)
        response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Login failed"})
