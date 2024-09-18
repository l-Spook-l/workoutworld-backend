from dotenv import load_dotenv
import os


load_dotenv()

CLIENT_IP = os.environ.get("CLIENT_IP")
CLIENT_PORT = os.environ.get("CLIENT_PORT")

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

DB_USER_TEST = os.environ.get("DB_USER_TEST")
DB_PASSWORD_TEST = os.environ.get("DB_PASSWORD_TEST")
DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")

SECRET_KEY = os.environ.get("SECRET_KEY")

SMTP_USER_EMAIL = os.environ.get("SMTP_USER_EMAIL")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
