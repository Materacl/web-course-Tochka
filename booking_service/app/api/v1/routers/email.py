from fastapi import APIRouter
from fastapi_mail import FastMail, MessageSchema
from ..config import settings
from ..utils.email import conf

router = APIRouter(
    prefix="/email",
    tags=["email"],
    responses={404: {"description": "Not found"}},
)


@router.post("/subscribe/")
async def subscribe(email: str):
    message = MessageSchema(
        subject="Subscription Confirmation",
        recipients=[email],
        body="You have successfully subscribed to notifications.",
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    return {"message": "Subscription successful"}
