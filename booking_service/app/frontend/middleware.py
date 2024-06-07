from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from jose import JWTError, jwt
from .config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get("access_token")
        if token:
            if token.startswith("Bearer "):
                token = token[len("Bearer "):]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                request.state.email = payload.get("sub")
                request.state.is_admin = payload.get("is_admin", False)
            except JWTError:
                request.state.email = None
                request.state.is_admin = False
        else:
            request.state.email = None
            request.state.is_admin = False
        response = await call_next(request)
        return response
