from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging

import uvicorn

from v1 import router
from v1.middleware import AuthMiddleware
from v1.config import settings

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """
    Create and configure an instance of the FastAPI application.

    Returns:
        app (FastAPI): The configured FastAPI application.
    """
    # Create the main FastAPI app instance
    app = FastAPI(title="HomeCinemaVR Frontend")

    # Mount the static files directory
    app.mount(
        "/static",
        StaticFiles(directory="v1/static"),
        name="static",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.CORS_ORIGINS],  # Update this with the allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add authentication middleware
    app.add_middleware(AuthMiddleware)

    # Include the main router
    app.include_router(router)

    # Add a simple error handler
    @app.exception_handler(Exception)
    async def custom_exception_handler(request: Request, exc: Exception):
        logger.error(f"An error occurred: {exc}")
        return JSONResponse(
            status_code=500,
            content={"message": "An internal server error occurred."},
        )

    return app


# Create an instance of the FastAPI application
app = create_app()
