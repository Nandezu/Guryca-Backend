import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Načtení proměnných z .env souboru
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-h!xpc8nnawpijntcf+9+q6d4d-o)3(%e&71fx5*w=)l8#@)z2l')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    os.environ.get('RENDER_EXTERNAL_HOSTNAME'),
    'localhost',
    '127.0.0.1',
    '192.168.0.106',
    'app-tdh1.onrender.com'
]
SITE_ID = 1

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
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

# Upravená konfigurace Jazzminu
JAZZMIN_SETTINGS = {
    "site_title": "Nande Admin",
    "site_header": "Nande",
    "site_brand": "Nande",
    "welcome_sign": "Vítejte v Nande Admin",
    "copyright": "Nandezu Inc",
    "search_model": ["auth.User", "auth.Group"],
    "user_avatar": None,
    
    # Top Menu
    "topmenu_links": [
        {"name": "Domů",  "url": "admin:index", "permissions": ["auth.view_user"]},
    ],
    
    # UI Tweaks
    "show_sidebar": True,
    "navigation_expanded": True,
    
    # Barvy a styl
    "theme": "default",
    "dark_mode_theme": "darkly",
}

AUTH_USER_MODEL = 'user.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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

# Upravená konfigurace pro statické soubory
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

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

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = 'noreply@nandezu.com'

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

PASSWORD_RESET_TIMEOUT = 3600

EMAIL_TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates', 'emails')

if os.environ.get('NANDEZU_ENV') == 'production':
    EXPO_SCHEME = 'nandefrond'
    PASSWORD_RESET_URL = f'{EXPO_SCHEME}://reset-password'
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_REFERRER_POLICY = 'same-origin'
else:
    EXPO_DEV_URL = 'exp://192.168.0.106:8081'
    PASSWORD_RESET_URL = f'{EXPO_DEV_URL}/--/reset-password'
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_ALLOW_ALL_ORIGINS = True

# Konfigurace pro in-app nákupy
SUBSCRIPTION_PRODUCTS = {
    'ios': {
        'BASIC_MONTHLY': 'com.nandezu.basic_monthly',
        'PRO_MONTHLY': 'com.nandezu.promonthly',
        'PREMIUM_MONTHLY': 'com.nandezu.premiummonthly',
        'BASIC_ANNUAL': 'com.nandezu.basicannual',
        'PRO_ANNUAL': 'com.nandezu.proannual',
        'PREMIUM_ANNUAL': 'com.nandezu.premiumannual',
    },
    'android': {
        'BASIC_MONTHLY': 'basic.monthly',
        'PRO_MONTHLY': 'pro.monthly',
        'PREMIUM_MONTHLY': 'premium.monthly',
        'BASIC_ANNUAL': 'basic.annual',
        'PRO_ANNUAL': 'pro.annual',
        'PREMIUM_ANNUAL': 'premium.annual',
    }
}

SUBSCRIPTION_MAPPING = {
    'com.nandezu.basic_monthly': ('basic', 30),
    'com.nandezu.promonthly': ('pro', 30),
    'com.nandezu.premiummonthly': ('premium', 30),
    'com.nandezu.basicannual': ('basic', 365),
    'com.nandezu.proannual': ('pro', 365),
    'com.nandezu.premiumannual': ('premium', 365),
    'basic.monthly': ('basic', 30),
    'pro.monthly': ('pro', 30),
    'premium.monthly': ('premium', 30),
    'basic.annual': ('basic', 365),
    'pro.annual': ('pro', 365),
    'premium.annual': ('premium', 365),
}

VERIFY_PURCHASES = os.environ.get('NANDEZU_ENV') == 'production' or os.environ.get('VERIFY_PURCHASES', 'False') == 'True'

# Apple App Store konfigurace
APPLE_BUNDLE_ID = os.environ.get('APPLE_BUNDLE_ID', 'com.nandezu.nandefrond')
APPLE_SHARED_SECRET = os.environ.get('APPLE_SHARED_SECRET', '588ae1e916b24e2a957e2ed3faa5714c')

# Google Play konfigurace
GOOGLE_SERVICE_ACCOUNT_JSON = os.path.join(BASE_DIR, 'secrets', 'service_account.json')
GOOGLE_PACKAGE_NAME = os.environ.get('GOOGLE_PACKAGE_NAME', 'com.nandezu.nandefrond')

# Webhooky pro notifikace o nákupech
APPLE_WEBHOOK_URL = os.environ.get('APPLE_WEBHOOK_URL')
GOOGLE_WEBHOOK_URL = os.environ.get('GOOGLE_WEBHOOK_URL')