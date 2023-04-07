from .base import *

DEBUG = True
IPS = "127.0.0.1"
ALLOWED_HOSTS = [IPS, "localhost"]

INSTALLED_APPS += [
    "debug_toolbar",
]

SECRET_KEY = "mysecret"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "instagram",
    }
}

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_FROM = "noreply@django.co"
INTERNAL_IPS = [IPS]

GRAPHENE["MIDDLEWARE"] = ["graphene_django.debug.DjangoDebugMiddleware"]
