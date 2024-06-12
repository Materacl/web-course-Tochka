from fastapi import APIRouter

from .routers import home, films, bookings, auth, sessions, profile

# Initialize the main router
router = APIRouter()

# Include individual routers with prefixes and tags
router.include_router(home.router)
router.include_router(auth.router)
router.include_router(profile.router)
router.include_router(films.router)
router.include_router(sessions.router)
router.include_router(bookings.router)
