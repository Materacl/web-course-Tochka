from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["home"])
templates = Jinja2Templates(directory="v1/templates")


@router.get("/", response_class=HTMLResponse, summary="Render the home page", tags=["home"])
def read_home(request: Request):
    """
    Render the home page.

    Args:
        request (Request): The request object.

    Returns:
        TemplateResponse: The rendered home page template.
    
    Raises:
        HTTPException: If an error occurs while rendering the template.
    """
    try:
        logger.info("Rendering home page")
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error("Error rendering home page: %s", e)
        raise HTTPException(status_code=500, detail="An error occurred while rendering the home page.") from e
