import pika
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from typing import List

app = FastAPI()


# Email Sending Functionality
def send_email(recipient: str, subject: str, body: str):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'your_email@example.com'
    msg['To'] = recipient

    try:
        with smtplib.SMTP('smtp.example.com') as server:
            server.login('your_email@example.com', 'your_password')
            server.sendmail('your_email@example.com', [recipient], msg.as_string())
        print(f'Email sent to {recipient}')
    except Exception as e:
        print(f'Failed to send email: {e}')
        raise HTTPException(status_code=500, detail="Failed to send email")


# MQ Listener Setup
def mq_listener():
    def callback(ch, method, properties, body):
        message = body.decode()
        print(f"Received {message}")
        try:
            recipient, subject, body = message.split('|')
            send_email(recipient, subject, body)
        except Exception as e:
            print(f'Error processing message: {e}')

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='email_queue')
    channel.basic_consume(queue='email_queue', on_message_callback=callback, auto_ack=True)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


# Background Job for Reminders
def reminder_job():
    # This is a placeholder function. Replace with actual reservation checking logic.
    upcoming_reservations = [
        {'email': 'user1@example.com', 'time': datetime.datetime.now() + datetime.timedelta(hours=2)},
        {'email': 'user2@example.com', 'time': datetime.datetime.now() + datetime.timedelta(days=1)}
    ]
    now = datetime.datetime.now()
    for reservation in upcoming_reservations:
        if now + datetime.timedelta(hours=1) >= reservation['time']:
            send_email(reservation['email'], 'Reservation Reminder', 'Your reservation is coming up soon.')


scheduler = BackgroundScheduler()
scheduler.add_job(reminder_job, 'interval', minutes=60)
scheduler.start()


# FastAPI Models
class RegistrationRequest(BaseModel):
    email: str


@app.post("/register")
async def register(request: RegistrationRequest):
    try:
        send_email(request.email, 'Email Confirmation', 'Please confirm your email.')
        return {"message": "Confirmation email sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Start the MQ listener in a separate thread
import threading

mq_thread = threading.Thread(target=mq_listener, daemon=True)
mq_thread.start()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
