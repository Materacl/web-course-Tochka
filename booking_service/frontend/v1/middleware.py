from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from jose import JWTError, jwt
from .config import settings
import logging

# Initialize logger
logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle authentication using JWT tokens.
    
    This middleware extracts the JWT token from the request cookies,
    decodes it, and attaches user information to the request state.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        token = request.cookies.get("access_token")
        if token:
            if token.startswith("Bearer "):
                token = token[len("Bearer "):]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                request.state.user_id = payload.get("id")
                request.state.email = payload.get("sub")
                request.state.nickname = payload.get("nickname", "")
                request.state.is_admin = payload.get("is_admin", False)
                request.state.notifications = payload.get("notifications", False)
            except JWTError as e:
                logger.warning(f"JWT Error: {e}")
                request.state.user_id = None
                request.state.email = None
                request.state.nickname = ""
                request.state.is_admin = False
        else:
            request.state.user_id = None
            request.state.email = None
            request.state.nickname = ""
            request.state.is_admin = False
        
        response = await call_next(request)
        return response
