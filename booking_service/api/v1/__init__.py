from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from .routers import bookings, user, admin, email, auth, reservations, films, sessions, payments

# Create an API Router with a prefix for versioning
router = APIRouter(
    prefix="/api/v1"
)

# Include various routers for different modules
router.include_router(auth.router)
router.include_router(user.router)
router.include_router(admin.router)
router.include_router(films.router)
router.include_router(sessions.router)
router.include_router(bookings.router)
router.include_router(reservations.router)
router.include_router(email.router)
router.include_router(payments.router)
