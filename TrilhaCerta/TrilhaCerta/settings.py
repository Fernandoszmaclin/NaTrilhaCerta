"""Configurações do projeto TrilhaCerta."""

from pathlib import Path
import os

from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(path: Path, *, override: bool = False) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and (override or key not in os.environ):
            os.environ[key] = value


def _env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {'1', 'true', 'yes', 'on'}


def _env_list(name: str, default: str = '') -> list[str]:
    raw = os.environ.get(name, default)
    return [item.strip() for item in raw.split(',') if item.strip()]


# Carrega .env (se python-dotenv estiver instalado) — opcional, não falha se ausente.
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(BASE_DIR.parent / '.env')
    load_dotenv(BASE_DIR / '.env', override=True)
except Exception:
    _load_env_file(BASE_DIR.parent / '.env')
    _load_env_file(BASE_DIR / '.env', override=True)


# Segredos vêm SEMPRE do ambiente em produção.
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-only-change-me-in-production',
)

DEBUG = _env_bool('DJANGO_DEBUG', False)

# Falha segura: nunca rodar produção com a SECRET_KEY de desenvolvimento.
if not DEBUG and 'insecure' in SECRET_KEY:
    raise ImproperlyConfigured(
        'DJANGO_SECRET_KEY precisa ser definida no ambiente para rodar em produção.'
    )

ALLOWED_HOSTS = _env_list('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost')

# Configurações de segurança HTTP
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True

# Produção (HTTPS obrigatório): cookies só trafegam cifrados e o site é
# redirecionado para HTTPS. Sem isso, sessão/CSRF vazam em Wi-Fi aberto.
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = _env_bool('DJANGO_SSL_REDIRECT', True)
    # 30 dias; suba para 31536000 (1 ano) após confirmar que todo o site roda em HTTPS.
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_HSTS_SECONDS', 2592000))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # Necessário atrás de proxy/load balancer que termina o TLS (ex.: nginx, Railway, Render).
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',
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

ROOT_URLCONF = 'TrilhaCerta.urls'

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

WSGI_APPLICATION = 'TrilhaCerta.wsgi.application'


# Database — credenciais via ambiente, fallback ao SQLite local quando DB_ENGINE='sqlite'.
_DB_ENGINE = os.environ.get('DB_ENGINE', 'postgresql').lower()

if _DB_ENGINE == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'trilhacerta_db'),
            'USER': os.environ.get('DB_USER', 'trilhacerta_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# Static & media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

CRISPY_TEMPLATE_PACK = "bootstrap5"

# Permite JS ler cookie CSRF para AJAX
CSRF_COOKIE_HTTPONLY = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login redirect
LOGIN_URL = '/'

# Sessões
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 2592000
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
# False: só grava a sessão quando ela muda (True geraria um write no banco a cada request).
SESSION_SAVE_EVERY_REQUEST = False


# Cache — o rate limiting (views._rate_limited) depende de um cache COMPARTILHADO
# entre os workers. Com LocMem cada processo do gunicorn tem contador próprio,
# multiplicando o limite efetivo pelo nº de workers.
#   - REDIS_URL definida  → Redis (recomendado em produção; requer pacote 'redis').
#   - produção sem Redis  → cache no banco (rode: manage.py createcachetable).
#   - desenvolvimento     → LocMem (processo único do runserver, suficiente).
_REDIS_URL = os.environ.get('REDIS_URL', '')

if _REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': _REDIS_URL,
        }
    }
elif not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'django_cache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }


# Webhook do gateway de pagamento — segredo HMAC para validação de assinatura.
PAYMENT_WEBHOOK_SECRET = os.environ.get('PAYMENT_WEBHOOK_SECRET', '')


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'core': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}
