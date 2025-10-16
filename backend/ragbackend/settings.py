import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
from utils import read_version
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Loading Configuration values
SECRET_KEY = os.getenv('SECRET_KEY', None)
ACCESS_TOKEN_LIFETIME_MIN = int(os.getenv('ACCESS_TOKEN_LIFETIME_MIN', 5))
REFRESH_TOKEN_LIFETIME_DAY = int(os.getenv('REFRESH_TOKEN_LIFETIME_DAY', 1))
ENABLE_DATABASE_TYPE = os.getenv('ENABLE_DATABASE_TYPE', 'Test')
DEBUG = True if str(os.getenv("DEBUG", True)).title() == "True" else False
USE_FAKE_LLM = True if str(os.getenv("USE_FAKE_LLM", True)).title() == "True" else False

DEFAULT_LLM_PROVIDER=os.getenv('DEFAULT_LLM_PROVIDER')
MISTRAL_MODEL_NAME = os.getenv('MISTRAL_MODEL_NAME')
LLAMA_MODEL_NAME = os.getenv('LLAMA_MODEL_NAME')
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE"))
DEFAULT_TOP_P = float(os.getenv("DEFAULT_TOP_P"))
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS"))
DEFAULT_N_CTX = int(os.getenv("DEFAULT_N_CTX"))
DEFAULT_N_GPU_LAYERS= int(os.getenv('DEFAULT_N_GPU_LAYERS'))
DEFAULT_N_BATCH=int(os.getenv('DEFAULT_N_BATCH'))
DEFAULT_F16_KV= True if os.getenv('DEFAULT_F16_KV').lower() == 'true' else False

DEFAULT_MIN_SIM = float(os.getenv('DEFAULT_MIN_SIM'))
DEFAULT_N_THREADS = int(os.getenv('DEFAULT_N_THREADS'))
DEFAULT_RETRIEVAL_K = int(os.getenv('DEFAULT_RETRIEVAL_K'))
DEFAULT_RETRIVER_K_MULTIPLIER = int(os.getenv('DEFAULT_RETRIVER_K_MULTIPLIER'))
DEFAULT_MMR_LAMBDA_PARAM = float(os.getenv("DEFAULT_MMR_LAMBDA_PARAM"))
DEFAULT_STREAMING = True if os.getenv('DEFAULT_STREAMING').lower() == 'true' else False

EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME')
EMBEDDING_MODEL_WEIGHT  = int(os.getenv("EMBEDDING_MODEL_WEIGHT"))
DEFAULT_CHUNK_SIZE  = int(os.getenv("DEFAULT_CHUNK_SIZE"))
DEFAULT_OVERLAP_SIZE  = int(os.getenv("DEFAULT_OVERLAP_SIZE"))


SUPABASE_DB_HOST  = os.getenv("SUPABASE_DB_HOST")
SUPABASE_DB_PORT  = int(os.getenv("SUPABASE_DB_PORT"))
SUPABASE_DB_USER  = os.getenv("SUPABASE_DB_USER")
SUPABASE_DB_PASSWORD  = os.getenv("SUPABASE_DB_PASSWORD")
SUPABASE_DB_NAME  = os.getenv("SUPABASE_DB_NAME")


DB_NAME = os.getenv("DB_NAME","")
DB_USER = os.getenv("DB_USER","")
DB_PASSWORD = os.getenv("DB_PASSWORD","")
DB_HOST = os.getenv("DB_HOST","")
DB_PORT = int(os.getenv("DB_PORT",1234))
VERSION=read_version()

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'drf_spectacular',
    
    'api',
    'project_management',
    'drf_api_logger',

    
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'drf_api_logger.middleware.api_logger_middleware.APILoggerMiddleware',

]

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}


# CORS configuration for a React frontend running on localhost:3000
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8010",
    "http://106.209.219.152:5173"
]
CORS_ALLOW_CREDENTIALS = True

# Additional JWT settings (optional, but good practice)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(ACCESS_TOKEN_LIFETIME_MIN)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(REFRESH_TOKEN_LIFETIME_DAY)),
}

ROOT_URLCONF = 'ragbackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ragbackend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

if ENABLE_DATABASE_TYPE.lower() == 'test':
    print('Test Database')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif ENABLE_DATABASE_TYPE.lower() == "supabase":
    print('Supabase Database')
    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.getenv('SUPABASE_DB_NAME'),
                'USER': os.getenv('SUPABASE_DB_USER'),
                'PASSWORD': os.getenv('SUPABASE_DB_PASSWORD'),
                'HOST': os.getenv('SUPABASE_DB_HOST'),   # looks like xyz.supabase.co
                'PORT': os.getenv('SUPABASE_DB_PORT', '5432'),
            }
            }
else:
    print('prod Database')
    DATABASES = {
        'default': {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": "localhost",
            "PORT": DB_PORT,
        }
    }



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

SPECTACULAR_SETTINGS = {
    'TITLE': 'ixora-RAG',
    'DESCRIPTION': 'GenAi Rag Application',
    'VERSION': VERSION,
    # Other settings
}

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'


TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Optional: Enable database storage for logs
DRF_API_LOGGER_DATABASE = True
# Optional: Configure slow API detection and data masking
# DRF_API_LOGGER_SLOW_API_ABOVE = 500  # Log as slow if above 500ms
DRF_API_LOGGER_EXCLUDE_KEYS = ['password', 'secret', 'token']