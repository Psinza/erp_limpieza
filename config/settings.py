import os
from pathlib import Path
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-mantenimiento-erp-limpieza-sustituir-en-produccion'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Núcleo del Sistema (Debe ir primero para AUTH_USER_MODEL)
    'apps.core.apps.CoreConfig', 
    
    # Módulos Funcionales
    'apps.contabilidad',
    'apps.vendedores',
    'apps.compras',
    'apps.ventas',
    'apps.activos_fijos',
    'apps.ordenacion_pagos',
    'apps.comercializacion',
    'apps.produccion',
    'apps.logistica',
    'apps.facturacion',
    'apps.viaticos',
    'apps.transportes',
    'apps.tesoreria',
    'apps.inventarios.apps.InventariosConfig',
    'apps.administracion',
    'apps.rrhh',
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

ROOT_URLCONF = 'config.urls'

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
                'apps.administracion.context_processors.empresa_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-ve'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

# Modelo de Usuario Personalizado
AUTH_USER_MODEL = 'core.Usuario'

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ERP_CONFIG = {
    'EMPRESA_NOMBRE': 'Fábrica de Limpieza S.A.',
    'VERSION': '1.0.0'
}

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Configuración de Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

CELERY_BEAT_SCHEDULE = {
    'enviar-reporte-mensual-fin-mes': {
        'task': 'apps.contabilidad.tasks.enviar_reporte_mensual_task',
        'schedule': crontab(minute=55, hour=23, day_of_month='28-31'),
        'description': 'Ejecuta el envío del reporte financiero el último día de cada mes a las 23:55'
    },
}

# Configuración de Correo SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Cambiar por tu servidor (ej. smtp.mailtrap.io para pruebas)
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-correo@gmail.com'  # Tu dirección de correo
EMAIL_HOST_PASSWORD = 'tu-contrasena-de-aplicacion'  # Tu contraseña o token
DEFAULT_FROM_EMAIL = f"Sistema ERP <{EMAIL_HOST_USER}>"
SERVER_EMAIL = EMAIL_HOST_USER

CSRF_TRUSTED_ORIGINS = ['https://*.cloudshell.dev']

ALLOWED_HOSTS = ['erp-limpieza.onrender.com', 'localhost', '127.0.0.1', '.cloudshell.dev']
CSRF_TRUSTED_ORIGINS = ['https://erp-limpieza.onrender.com', 'https://*.cloudshell.dev']
