from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, Request, Form, HTTPException, Depends, Cookie
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, User
import secrets

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Secret key for signing cookies
SECRET_KEY = "your-secret-key"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db), token: str = Cookie(None)):
    if token:
        user = db.query(User).filter(User.username == token).first()
        if user:
            return user
    return None


def create_token(username: str) -> str:
    return secrets.token_urlsafe()


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request, current_user: User = Depends(get_current_user)):
    username = current_user.username if current_user else ""
    return templates.TemplateResponse("index.jinja2", {"request": request, "title": "Homepage", "username": username})


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.jinja2", {"request": request, "title": "Login"})


@router.post("/login")
async def do_login(request: Request, username: str = Form(...), password: str = Form(...),
                   db: Session = Depends(get_db)):
    # Check if user exists and password is correct
    user = db.query(User).filter(User.username == username).first()
    if user is None or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create session token
    token = create_token(username)

    # Set cookie with token
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session_token", value=token, httponly=True)

    return response


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.jinja2", {"request": request, "title": "Register"})


@router.post("/register")
async def do_register(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...),
                      db: Session = Depends(get_db)):
    # Check if user already exists
    user = db.query(User).filter(User.username == username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Create new user
    new_user = User(username=username, email=email, password=password)
    db.add(new_user)
    db.commit()

    # Redirect to index page after successful registration
    return RedirectResponse(url="/", status_code=303)


@router.get("/logout")
async def logout(request: Request, current_user: User = Depends(get_current_user)):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_token")
    return response
