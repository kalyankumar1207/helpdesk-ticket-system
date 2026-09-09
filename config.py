import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, "helpdesk.db")

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "helpdesk-development-secret"
)