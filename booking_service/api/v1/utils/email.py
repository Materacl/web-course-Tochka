from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi import HTTPException
from ..config import settings
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Configure email settings
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS
)

async def send_notification(message: MessageSchema):
    """
    Send an email notification.

    Args:
        message (MessageSchema): The message schema containing email details.

    Returns:
        bool: True if the email is sent successfully.

    Raises:
        HTTPException: If there is an error sending the email.
    """
    fm = FastMail(conf)
    try:
        logger.info(f"Sending email to {message.recipients}")
        await fm.send_message(message, template_name=None)
        logger.info("Email sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")
    