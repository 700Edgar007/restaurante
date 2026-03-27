
"""
Django settings for restaurante_fidelizacion project.
Configurado para despliegue en Render 🚀 + AWS S3 ☁️
"""

from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key
import dj_database_url

# ==============================
# 📁 RUTAS DEL PROYECTO
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================
# 🔐 SEGURIDAD
# ==============================
SECRET_KEY = os.environ.get("SECRET_KEY") or get_random_secret_key()
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# ==============================
# 📦 APLICACIONES INSTALADAS
# ==============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps del proyecto
    'carta',
    'clientes',
    'pedidos',

    # Librerías externas
    'django_recaptcha',
    'storages',  # 🔥 AWS S3
]


# ==============================
# ⚙️ MIDDLEWARE
# ==============================
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


# ==============================
# 🌐 CONFIGURACIÓN GENERAL
# ==============================
ROOT_URLCONF = 'restaurante_fidelizacion.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'carta.context_processors.carrito_resumen',
            ],
        },
    },
]

WSGI_APPLICATION = 'restaurante_fidelizacion.wsgi.application'


# ==============================
# 🗄️ BASE DE DATOS
# ==============================
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}


# ==============================
# 🔑 VALIDACIÓN DE CONTRASEÑAS
# ==============================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
]


# ==============================
# 🌍 INTERNACIONALIZACIÓN
# ==============================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ==============================
# 📁 ARCHIVOS ESTÁTICOS
# ==============================
STATIC_URL = 'static/'

if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ==============================
# 📁 ARCHIVOS MEDIA (AWS S3)
# ==============================

# ******************************
# ******************************
# 🔥 AWS S3 CONFIG (IMÁGENES)
# ******************************
# ******************************

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

AWS_STORAGE_BUCKET_NAME = "tu-bucket-restaurante"
AWS_S3_REGION_NAME = "us-east-2"

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

# ******************************
# ******************************
# 🚀 FIN AWS
# ******************************
# ******************************


# ==============================
# 🔐 LOGIN / LOGOUT
# ==============================
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'


# ==============================
# 🔢 PRIMARY KEY
# ==============================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================
# 🔐 RECAPTCHA
# ==============================
RECAPTCHA_PUBLIC_KEY = os.environ.get(
    'RECAPTCHA_PUBLIC_KEY',
    '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
)

RECAPTCHA_PRIVATE_KEY = os.environ.get(
    'RECAPTCHA_PRIVATE_KEY',
    '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
)


# ==============================
# 🍽️ API EXTERNA
# ==============================
SPOONACULAR_API_KEY = os.environ.get('SPOONACULAR_API_KEY', '').strip()


# ==============================
# 📧 EMAIL
# ==============================
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in {'1','true','yes','on'}

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '').strip()
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '').strip()

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER).strip()


# ==============================
# 🔕 IGNORAR ERROR DE RECAPTCHA
# ==============================
SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']


# ==============================