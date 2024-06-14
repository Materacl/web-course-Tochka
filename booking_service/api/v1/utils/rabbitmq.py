import logging
import aio_pika
import os
import asyncio
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

async def publish_message(queue: str, subject: str, recipients: list, body: str, subtype: str = "html"):
    """
    Publish a message to the specified RabbitMQ queue.

    Args:
        queue (str): The name of the RabbitMQ queue.
        subject (str): The subject of the message.
        recipients (list): A list of recipient email addresses.
        body (str): The body of the message.
        subtype (str): The subtype of the message, default is "html".

    Raises:
        Exception: If there is an error while publishing the message.
    """
    try:
        # Establish a connection to RabbitMQ
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            # Create a communication channel
            channel = await connection.channel()
            
            # Declare a queue
            await channel.declare_queue(queue, durable=True)
            
            # Prepare the message payload
            message = {
                "subject": subject,
                "recipients": recipients,
                "body": body,
                "subtype": subtype
            }
            
            # Publish the message to the queue
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
