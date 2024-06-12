from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from .routers import user, admin, booking, email, auth, reservations, films, sessions

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
router.include_router(booking.router)
router.include_router(reservations.router)
router.include_router(email.router)

@router.get("/")
def read_root():
    """
    Root endpoint that redirects to the API documentation.
    """
    return RedirectResponse(url="/docs")
