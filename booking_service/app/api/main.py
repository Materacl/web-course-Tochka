from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .v1 import router as api_v1_router
from .v1.scheduler import scheduler


def create_app():
    app = FastAPI(title="My Project API")

    origins = [
        "http://localhost:8001",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router)

    @app.on_event("startup")
    def startup_event():
        if not scheduler.running:
            scheduler.start()

    @app.on_event("shutdown")
    def shutdown_event():
        scheduler.shutdown()

    return app


app = create_app()
