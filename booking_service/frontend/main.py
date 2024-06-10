from fastapi import FastAPI

from v1 import router
from fastapi.staticfiles import StaticFiles
from v1.middleware import AuthMiddleware


def create_app():
    # Create the main FastAPI app instance
    app = FastAPI(title="HomeCinemaVR Frontend")

    # Mount the static files directory
    app.mount(
        "/static",
        StaticFiles(directory="v1/static"),
        name="static",
    )

    # Add authentication middleware
    app.add_middleware(AuthMiddleware)

    # Include the main router
    app.include_router(router)
    return app


app = create_app()
