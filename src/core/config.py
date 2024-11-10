import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_IP = os.environ.get("CLIENT_IP")
CLIENT_PORT = os.environ.get("CLIENT_PORT")

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

DB_USER_TEST = os.environ.get("DB_USER_TEST")
DB_PASSWORD_TEST = os.environ.get("DB_PASSWORD_TEST")
DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DATABASE_URL_TEST = \
    f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASSWORD_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}"

REDIS_PORT = os.environ.get("REDIS_PORT")

SECRET_KEY = os.environ.get("SECRET_KEY")

ADMIN_SECRET_KEY = os.environ.get("ADMIN_SECRET_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

SENTRY_DNS = os.environ.get("SENTRY_DNS")

SMTP_USER_EMAIL = os.environ.get("SMTP_USER_EMAIL")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"  # Default value
)

METRICS_URL = os.environ.get("METRICS_URL")
