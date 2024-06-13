import os
import json
import time
import logging
import asyncio
import aio_pika
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# Fetch environment variables
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_PORT = int(os.getenv("MAIL_PORT"))
MAIL_SERVER = os.getenv("MAIL_SERVER")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration for FastMail
conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER
)

async def send_email(message):
    fm = FastMail(conf)
    await fm.send_message(message)
    logger.info(f"Email sent to {message.recipients}")

async def callback(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            raw_message = message.body.decode()
            logger.info(f"Received raw message: {raw_message}")
            message_body = json.loads(raw_message)
            message_schema = MessageSchema(
                subject=message_body["subject"],
                recipients=message_body["recipients"],
                body=message_body["body"],
                subtype=message_body["subtype"]
            )
            await send_email(message_schema)
            logger.info(f"Processed message: {message_body}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {e}")
        except Exception as e:
            logger.error(f"Failed to process message: {e}")

async def main():
    while True:
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=1)
                queue = await channel.declare_queue('booking_notifications', durable=True)
                await queue.consume(callback)

                logger.info("Waiting for messages. To exit press CTRL+C")
                await asyncio.Future()  # Run forever
        except aio_pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Connection to RabbitMQ failed, retrying in 5 seconds... Error: {e}")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker shut down gracefully.")
