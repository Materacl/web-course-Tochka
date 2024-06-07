from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["home"])
templates = Jinja2Templates(directory="frontend/templates")


@router.get("/")
def read_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
