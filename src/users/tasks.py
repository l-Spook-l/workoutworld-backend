import smtplib
from email.message import EmailMessage
from src.core.config import SMTP_USER_EMAIL, SMTP_PASSWORD
from src.core.celery import celery_app


@celery_app.task
def send_message_to_admin(name: str, email: str, user_message: str):
    sender = SMTP_USER_EMAIL
    recipient = SMTP_USER_EMAIL
    password = SMTP_PASSWORD
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = "User send email"
    message.set_content(f"This user {name}, his email {email}, send  message :{user_message}")

    with smtplib.SMTP_SSL(host="smtp.gmail.com", port=465) as server:
        server.login(user=sender, password=password)
        server.send_message(message)
