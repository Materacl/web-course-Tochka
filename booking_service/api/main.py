import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from v1 import router as api_v1_router
from v1.utils.scheduler import scheduler
from v1.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """
    Create and configure an instance of the FastAPI application.

    Returns:
        app (FastAPI): The configured FastAPI application.
    """
    app = FastAPI(title="HomCinemaVR API")

    # List of allowed origins for CORS. This can be configured via environment variables.
    origins = settings.CORS_ORIGINS.split(",")  # assuming CORS_ORIGINS is a comma-separated string

    # Ensure all requests are redirected to HTTPS
    app.add_middleware(HTTPSRedirectMiddleware)

    # Optionally, add TrustedHostMiddleware if you want to restrict host headers
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["homecinemavr.3005537-hf76571.twc1.net",
                                                             "*.homecinemavr.3005537-hf76571.twc1.net"])

    # Add CORS middleware to the FastAPI app to handle cross-origin requests.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API v1 router
    app.include_router(api_v1_router)

    @app.on_event("startup")
    async def startup_event():
        """
        Event handler that runs on application startup. 
        Starts the scheduler if it's not already running.
        """
        app.root_path = "https://homecinemavr.3005537-hf76571.twc1.net"
        if not scheduler.running:
            scheduler.start()
        logger.info("Scheduler started")

    @app.on_event("shutdown")
    async def shutdown_event():
        """
        Event handler that runs on application shutdown.
        Shuts down the scheduler if it's running.
        """
        if scheduler.running:
            scheduler.shutdown()
        logger.info("Scheduler stopped")

    return app

# Create an instance of the FastAPI application
app = create_app()
