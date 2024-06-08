from fastapi import FastAPI

from . import router
from fastapi.staticfiles import StaticFiles
from .middleware import AuthMiddleware

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
