from pathlib import Path

from .util import load_env

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent

LOCAL_SETTINGS = load_env(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#9)q!_i3@pr-^3oda(e^3$x!kq3b4f33#5l@+=+&vuz+p6gb3g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'passkey_example.apps.AppAdminConfig',
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'passkeys',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'passkey_example.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'passkey_example' / 'templates'],
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

WSGI_APPLICATION = 'passkey_example.wsgi.application'

STATIC_URL = '/static/'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

LOGIN_URL = "/auth/login"

AUTHENTICATION_BACKENDS = ['passkeys.backend.PasskeyModelBackend']

FIDO_SERVER_ID = LOCAL_SETTINGS['DJANGO_PASSKEY_HOST']  # Server rp id for FIDO2, it the full domain of your project

FIDO_SERVER_NAME = "DjangoPasskeysExampleApp"

KEY_ATTACHMENT = None  # Set None to allow all authenticator attachment

CSRF_TRUSTED_ORIGINS = [
    "https://" + LOCAL_SETTINGS['DJANGO_PASSKEY_HOST']
]
