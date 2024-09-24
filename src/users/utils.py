from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from src.core.database import get_async_session
from email.message import EmailMessage
from dotenv import load_dotenv
import aiosmtplib
from src.core.config import SMTP_USER_EMAIL, SMTP_PASSWORD, CLIENT_IP, CLIENT_PORT

load_dotenv()


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def send_token_by_email(email, token):
    client_ip = f'http://{CLIENT_IP}:{CLIENT_PORT}'
    sender = SMTP_USER_EMAIL
    recipient = email
    password = SMTP_PASSWORD
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = "Password recovery"
    message.set_content(f"Hello, you have requested a password reset. Please follow the link to set a new password. "
                        f"If this wasn't you, please disregard this message {client_ip}/reset-password/"
                        f"{token}")

    await aiosmtplib.send(message, hostname="smtp.gmail.com", port=465, use_tls=True, username=sender,
                          password=password)
