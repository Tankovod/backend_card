import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

SECRET_AUTH = os.environ.get("SECRET_AUTH")

DOMAIN = os.environ.get("DOMAIN")

PAYMENT_USER = os.environ.get("PAYMENT_USER")
PAYMENT_PASSWORD = os.environ.get("PAYMENT_PASSWORD")

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

STATIC_URL = f"{DOMAIN}static/img/"
