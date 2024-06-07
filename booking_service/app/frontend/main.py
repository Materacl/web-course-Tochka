from fastapi import APIRouter, FastAPI
from .routers import home, films, bookings, reservations, auth, sessions
from fastapi.staticfiles import StaticFiles
from .middleware import AuthMiddleware

# Create an APIRouter instance
router = APIRouter()

# Include individual routers from different modules
router.include_router(home.router)
router.include_router(auth.router)
router.include_router(films.router)
router.include_router(sessions.router)
router.include_router(bookings.router)
router.include_router(reservations.router)

# Create the main FastAPI app instance
app = FastAPI(title="HomeCinemaVR Frontend")

# Mount the static files directory
app.mount(
    "/static",
    StaticFiles(directory="frontend/static"),
    name="static",
)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Include the main router
app.include_router(router)
