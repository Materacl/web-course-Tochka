from fastapi import APIRouter

from .routers import home, films, bookings, reservations, auth, sessions

router = APIRouter()

router.include_router(home.router)
router.include_router(auth.router)
router.include_router(films.router)
router.include_router(sessions.router)
router.include_router(bookings.router)
router.include_router(reservations.router)
