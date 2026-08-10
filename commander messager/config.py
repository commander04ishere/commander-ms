import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(file))

class Config:

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "dev-secret-change-me"
)

SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL"
)

SQLALCHEMY_TRACK_MODIFICATIONS = False
