import json
import os

import dj_database_url

from .base import *

ALLOWED_HOSTS = ["*"]
DEBUG = False

SECRET_KEY = "django-insecure-1xmckgda3_ktt$4h6-k2rz1lvtx3j-&x&5==(uzk(qp6@&t_51"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        default=f"postgres://{get_config("DB_USER")}:{get_config("DB_PASSWORD")}@{get_config("DB_HOST")}/{get_config("DB_NAME")}"
    )
}

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SOCIAL_AUTH_FACEBOOK_KEY = get_config("SOCIAL_AUTH_FACEBOOK_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = get_config("SOCIAL_AUTH_FACEBOOK_SECRET")
