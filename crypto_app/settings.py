from pathlib import Path
from decouple import config
from django.contrib.auth import get_user_model


BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True #Set to false after deploying 

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'custom_auth.apps.CustomAuthConfig',
    'social_django',
    'rest_framework',
    'drf_spectacular',
    'django_recaptcha',
    'widget_tweaks' # я даже блять не знаю что это
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

ROOT_URLCONF = 'crypto_app.urls'

WSGI_APPLICATION = 'crypto_app.wsgi.application'

AUTH_USER_MODEL = 'custom_auth.User'
 
#django secret key, recaptcha keys, google oauth2 keys, all these are taken from env file using config
SECRET_KEY = config('SECRET_KEY')
RECAPTCHA_PUBLIC_KEY = config('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = config('RECAPTCHA_PRIVATE_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('GOOGLE_OAUTH2_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('GOOGLE_OAUTH2_CLIENT_SECRET')

#Oauth2 settings 
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']

#user profile settings (it is mainly used for Oauth2)
AUTHENTICATION_BACKENDS = [ 
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/home/' # Перенаправляем на home после успешного логина
LOGOUT_REDIRECT_URL = '/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Папка templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',  # Для OAuth2
                'social_django.context_processors.login_redirect',  # Для OAuth2
            ],
        },
    },
]


#DB settings
#DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT are taken from env file using config
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'custom_auth.pipeline.check_existing_user_by_email',  #используем функцию из pypeline.py для проверки существующего пользователя по email
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

# Настройки логирования
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
LANGUAGE_CODE = 'en-us' #в гайде было написано про en-us, по этому не будем ставить en-uk
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/' 
STATICFILES_DIRS = [BASE_DIR / 'static']  # Папка static в корне проекта, оттуда подтягивается css и javascript 
STATIC_ROOT = BASE_DIR / "staticfiles" # Для collectstatic (возможно позже понадобится)


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

