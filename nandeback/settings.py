import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-h!xpc8nnawpijntcf+9+q6d4d-o)3(%e&71fx5*w=)l8#@)z2l'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.0.106']
SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'user',
    'shop',
    'tryon',
    'storages',
    'django_filters',
]

AUTH_USER_MODEL = 'user.CustomUser'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nandeback.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nandeback.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# AWS S3 settings
AWS_ACCESS_KEY_ID = 'AKIA6GBMEM6GOI77EB6R'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'usersnandezu'
AWS_S3_REGION_NAME = 'us-east-1'  # Změňte na vaši region
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True

# Nastavení pro ukládání souborů do S3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# URL pro média a statické soubory
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
STATIC_URL = '/static/'

# Lokální média (pro vývoj)
MEDIA_ROOT = BASE_DIR / 'media'

# Email settings for SendGrid
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = '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'
DEFAULT_FROM_EMAIL = 'noreply@nandezu.com'  # Nahraďte vaší e-mailovou adresou

# SendGrid API Key
SENDGRID_API_KEY = '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'

# Password reset settings
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour in seconds

# Email template settings
EMAIL_TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates', 'emails')

# Nastavení pro reset hesla
if os.environ.get('NANDEZU_ENV') == 'production':
    EXPO_SCHEME = 'nandefrond'
    PASSWORD_RESET_URL = f'{EXPO_SCHEME}://reset-password'
else:
    EXPO_DEV_URL = 'exp://192.168.0.106:8081'
    PASSWORD_RESET_URL = f'{EXPO_DEV_URL}/--/reset-password'