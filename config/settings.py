import os
import sys
from pathlib import Path

# Попытка импорта dj_database_url (опционально для SQLite)
try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# Базовые пути
BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасность
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-me')

# DEBUG - исправлено (булево значение, не строка)
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,testserver').split(',') if h.strip()]
ALLOWED_HOSTS.append('https-github-com-paneledmaxim.onrender.com')
ALLOWED_HOSTS.append('nutrition-tracker-django.onrender.com')  # добавь свое имя, если переименуешь

# INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'diary',
    'recipes',
]

# MIDDLEWARE (WhiteNoise будет добавлен ниже, если установлен)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'config.middleware.ApiRequestLogMiddleware',
]

# WhiteNoise для статики (если установлен)
try:
    import whitenoise  # noqa: F401
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
except ImportError:
    pass

# URL конфигурация
ROOT_URLCONF = 'config.urls'

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'users.context_processors.incoming_friend_requests_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# База данных (PostgreSQL или SQLite)
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Валидация паролей
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

# Интернационализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Статические файлы
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise хранение (если используется)
if 'whitenoise.middleware.WhiteNoiseMiddleware' in MIDDLEWARE:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Медиа файлы
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Пользовательская модель
AUTH_USER_MODEL = 'users.CustomUser'

# Аутентификация
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Email (файловый для разработки)
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
DEFAULT_FROM_EMAIL = 'noreply@nutrition-tracker.local'

# Авто-поле
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Логи
LOGS_DIR = BASE_DIR / 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(EMAIL_FILE_PATH, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


if 'gunicorn' in sys.argv[0] or 'migrate' in sys.argv or 'runserver' in sys.argv:
    try:
        from django.contrib.auth import get_user_model
        from django.db import connection
        
        User = get_user_model()
        
        # Проверяем, что таблицы существуют
        if connection.introspection.table_names():
            # Создаем или обновляем админа
            admin, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'is_superuser': True,
                    'is_staff': True,
                    'is_active': True,
                }
            )
            # Устанавливаем пароль (в любом случае)
            admin.set_password('admin123')
            admin.save()
            
            if created:
                print("=" * 50)
                print(" SUPERUSER CREATED!")
                print("   Login: admin")
                print("   Password: admin123")
                print("=" * 50)
            else:
                print("ℹ Admin password reset to 'admin123'")
                
    except Exception as e:
        print(f" Could not setup superuser: {e}")