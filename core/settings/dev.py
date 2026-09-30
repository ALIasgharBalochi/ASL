from pathlib import Path
from dotenv import load_dotenv
import os

from .settings import *

from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {
            "host": "smtp.gmail.com",
            "port": 587,
            "username": os.getenv("EMAIL_HOST_USER"),
            "password": os.getenv("EMAIL_HOST_PASSWORD"),
            "use_tls": True,
        },
    },
}

# Celery
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = None
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Tehran"
CELERY_ENABLE_UTC = True

CELERY_BEAT_SCHEDULE = {
    "weekly-report": {
        "task": "apps.reports.tasks.generate_periodic_report",
        "schedule": crontab(
            day_of_week="monday",
            hour=9,
            minute=0,
        ),
        "args": ("weekly",),
    },

    "monthly-report": {
        "task": "apps.reports.tasks.generate_periodic_report",
        "schedule": crontab(
            day_of_month="1",
            hour=9,
            minute=0,
        ),
        "args": ("monthly",),
    },
}