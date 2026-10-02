from .settings import *

DEBUG = False
ALLOWED_HOSTS = ["example.ir"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "asl_db",
        "USER": "asl_user",
        "PASSWORD": "123456",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
