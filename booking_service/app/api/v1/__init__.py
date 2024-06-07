from fastapi import APIRouter
from .routers import admin, booking, email, auth, reservations, films, sessions, cinema_halls
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix="/api/v1"
)

router.include_router(auth.router)
router.include_router(admin.router)
router.include_router(films.router)
router.include_router(sessions.router)
router.include_router(cinema_halls.router)
router.include_router(booking.router)
router.include_router(reservations.router)
router.include_router(email.router)


@router.get("/")
def read_root():
    return RedirectResponse(url="/docs")
