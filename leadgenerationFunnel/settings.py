from pathlib import Path
import os
import environ
import dj_database_url


# Initialize environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))  # Load from .env at root

# Django Basic Settings
SECRET_KEY = env("DJANGO_SECRET_KEY", default='insecure-secret')
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

# Directories
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
MEDIA_DIR = BASE_DIR / "media"

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'leads',
    # 'senttemplate',
    'django.contrib.sites',
    'django_q',
    # 'django_celery_beat',
]

SITE_ID = 1

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'leadgenerationFunnel.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

WSGI_APPLICATION = 'leadgenerationFunnel.wsgi.application'

# # Database
# DATABASES = {
#         'default': dj_database_url.config(
#             default=env('DATABASE_URL')  # Render se milega
#         )
#     }

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'OnboardingUsers',
        'USER': 'Sherlocksauto',
        'PASSWORD': 'Sherlocks@8072',
        'HOST': 'aspire.herosite.pro',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': "CurrentSchema=DjangoAuth",  # Django tables apne schema me
        },
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'mssql',
#         'NAME': 'OnboardingUsers',
#         'USER': 'Sherlocksauto',
#         'PASSWORD': 'Sherlocks@8072',
#         'HOST': 'aspire.herosite.pro',
#         'PORT': '1433',
#         'OPTIONS': {
#             'driver': 'ODBC Driver 17 for SQL Server',  # Windows pe 17 ya 18
#             'extra_params': 'CurrentSchema=DjangoAuth',  # agar schema chahiye
#         },
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }





Q_CLUSTER = {
    'name': 'whatsapp-daily-sender',
    'workers': 4,
    'timeout': 90,
    'retry': 90,
    'queue_limit': 1000,
    'bulk': 1000,
    'orm': 'default',
}
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [STATIC_DIR]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = MEDIA_DIR

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# Celery settings


# WhatsApp API credentials
META_ACCESS_TOKEN = env('META_ACCESS_TOKEN')
META_PHONE_NUMBER_ID = env('META_PHONE_NUMBER_ID')
META_WABA_ID = env('META_WABA_ID')

META_VERIFY_TOKEN = env('META_VERIFY_TOKEN')

MEDIA_ID = env('media_id')
# THUMBNAIL_ID = env('THUMBNAIL_ID')


