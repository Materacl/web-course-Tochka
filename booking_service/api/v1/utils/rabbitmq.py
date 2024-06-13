import pika
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

def publish_message(queue, message):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
    )
    connection.close()
