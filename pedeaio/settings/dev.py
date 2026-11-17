
from .base import *

# Configurações do ambiente de desenvolvimento
DEBUG = True

# Banco de dados local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
