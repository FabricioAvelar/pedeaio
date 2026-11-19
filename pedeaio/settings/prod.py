from .base import *

import dj_database_url


DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", cast=Csv())

DATABASES = {
    "default": dj_database_url.parse(config("DATABASE_URL"), conn_max_age=600)
}

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # mantenha aqui o que você já usa para os estáticos (whitenoise)
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Só ativa o armazenamento externo se o bucket estiver configurado
if config("S3_BUCKET_NAME", default=""):
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": config("S3_BUCKET_NAME"),
            "access_key": config("S3_ACCESS_KEY"),
            "secret_key": config("S3_SECRET_KEY"),
            "endpoint_url": config("S3_ENDPOINT_URL"),
            "region_name": config("S3_REGION", default="auto"),
            "querystring_auth": False,   # links públicos, sem assinatura temporária
            "default_acl": None,
            "file_overwrite": False,
        },
    }

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]