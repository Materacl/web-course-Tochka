import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from ..config import settings

# Initialize logger
logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new access token.

    Args:
        data (Dict[str, Any]): The data to include in the token.
        expires_delta (Optional[timedelta]): The time delta for token expiration.

    Returns:
        str: The encoded JWT token.
    """
    logger.info("Creating access token")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info("Access token created")
    return encoded_jwt

def decode_access_token(token: str) -> Optional[str]:
    """
    Decode an access token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Optional[str]: The email (subject) from the token if valid, None otherwise.
    """
    logger.info("Decoding access token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.error("Token does not contain a subject")
            return None
        logger.info("Access token decoded successfully")
        return email
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        return None
    except jwt.JWTError as e:
        logger.error(f"Token decoding error: {e}")
        return None
    