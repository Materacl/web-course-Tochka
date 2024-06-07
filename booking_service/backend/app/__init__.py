from fastapi import FastAPI
from app.routers import admin, booking, email, auth, reservations, films, sessions, cinema_halls

app = FastAPI()

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(films.router)
app.include_router(sessions.router)
app.include_router(cinema_halls.router)
app.include_router(booking.router)
app.include_router(reservations.router)
app.include_router(email.router)
