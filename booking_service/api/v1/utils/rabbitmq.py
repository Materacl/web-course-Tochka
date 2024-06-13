import logging
import aio_pika
import os
import asyncio
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

async def publish_message(queue, subject, recipients, body, subtype="html"):
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue(queue, durable=True)
            message = {
                "subject": subject,
                "recipients": recipients,
                "body": body,
                "subtype": subtype
            }
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=queue,
            )
        logger.info(f"Message published to queue {queue}: {message}")
    except Exception as e:
        logger.error(f"Error publishing message to queue {queue}: {e}")
