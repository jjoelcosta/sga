from pathlib import Path
import os
import logging
from logging.handlers import RotatingFileHandler

BASE_DIR = Path(__file__).resolve().parent.parent

# Segurança: pegar valores sensíveis do ambiente
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "replace-me-in-prod")
DEBUG = os.environ.get("DJANGO_DEBUG", "False") in ("1", "true", "True")

# Hosts permitidos (separados por vírgula em DJANGO_ALLOWED_HOSTS)
_allowed = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(",") if h.strip()]

# URLs de login
LOGIN_URL = os.environ.get("DJANGO_LOGIN_URL", "/login/")
LOGIN_REDIRECT_URL = os.environ.get("DJANGO_LOGIN_REDIRECT_URL", "/cadastro/")
LOGOUT_REDIRECT_URL = os.environ.get("DJANGO_LOGOUT_REDIRECT_URL", "/")

# Media / uploads
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Static
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # para collectstatic em produção

# Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "importacoes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sga.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "sga.wsgi.application"

# Database: usar DATABASE_URL se disponível (Postgres recomendado)
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    # tenta usar dj_database_url se instalado; fallback para parsing simples
    try:
        import dj_database_url

        DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
    except Exception:
        # básico: se DATABASE_URL não for suportada, mantém sqlite (warn)
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internacionalização
LANGUAGE_CODE = os.environ.get("DJANGO_LANGUAGE_CODE", "pt-br")
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "America/Sao_Paulo")
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Segurança para produção (controle via variáveis de ambiente)
SESSION_COOKIE_SECURE = os.environ.get("DJANGO_SESSION_COOKIE_SECURE", str(not DEBUG)) in (
    "1",
    "True",
    "true",
)
CSRF_COOKIE_SECURE = os.environ.get("DJANGO_CSRF_COOKIE_SECURE", str(not DEBUG)) in ("1", "True", "true")
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", str(not DEBUG)) in (
    "1",
    "True",
    "true",
)
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", "False"
) in ("1", "True", "true")
SECURE_HSTS_PRELOAD = os.environ.get("DJANGO_SECURE_HSTS_PRELOAD", "False") in ("1", "True", "true")
X_FRAME_OPTIONS = "DENY"

# Logging mínimo com rotação (útil para auditoria de eventos)
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "sga.log"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_FILE),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["file", "console"], "level": "INFO"},
}

# Exemplo: cabeçalho HTTP para identificar proxy (se estiver atrás de reverse proxy)
USE_X_FORWARDED_HOST = os.environ.get("DJANGO_USE_X_FORWARDED_HOST", "False") in (
    "1",
    "True",
    "true",
)

# Ajustes adicionais (opcionais): registre o IP real do usuário em middleware personalizado
# e crie handlers/rotinas específicas para AccessLog / AuditLog no app core.

# Fallbacks e valores úteis para desenvolvimento
if DEBUG:
    # em dev, mostrar logs no console já suficiente
    logging.getLogger("django").setLevel(logging.DEBUG)