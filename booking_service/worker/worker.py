import os
import json
import time
import pika
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# Fetch environment variables
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_PORT = int(os.getenv("MAIL_PORT"))
MAIL_SERVER = os.getenv("MAIL_SERVER")

# Configuration for FastMail
conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER
)

def callback(ch, method, properties, body):
    message = json.loads(body)
    message_schema = MessageSchema(
        subject=message["subject"],
        recipients=message["recipients"],
        body=message["body"],
        subtype=message["subtype"]
    )
    fm = FastMail(conf)
    fm.send_message(message_schema)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    while True:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            channel.queue_declare(queue='email')

            channel.basic_consume(queue='email', on_message_callback=callback, auto_ack=True)
            print('Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection to RabbitMQ failed, retrying in 5 seconds... Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    start_worker()
