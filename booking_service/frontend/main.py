from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers import auth, admin, booking
from app.models import Film, Booking

app = FastAPI()

# Mount static files for CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Include your routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(booking.router)


# Example frontend route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/films", response_class=HTMLResponse)
async def read_films(request: Request, db: Session = Depends(get_db)):
    films = db.query(Film).all()
    return templates.TemplateResponse("films.html", {"request": request, "films": films})


@app.get("/bookings", response_class=HTMLResponse)
async def read_bookings(request: Request, db: Session = Depends(get_db)):
    bookings = db.query(Booking).all()
    return templates.TemplateResponse("bookings.html", {"request": request, "bookings": bookings})


@app.post("/bookings", response_class=HTMLResponse)
async def create_booking(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    session_id = form.get("session_id")
    user_id = form.get("user_id")
    new_booking = Booking(session_id=session_id, user_id=user_id, status="pending")
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return templates.TemplateResponse("bookings.html", {"request": request, "bookings": db.query(Booking).all()})
