# Configuración (settings.py)

Archivo: `zapotal_config/settings.py`

## Apps Instaladas

```python
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
    'django_filters',
    'django_throttle',
    # Locales
    'apps.core',
    'apps.accounts',
    'apps.content',
    'apps.comunidad',
    'apps.messaging',
    'apps.reports',
]
```

## DRF Config

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

## SimpleJWT

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

## CORS

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Frontend Vite
    'http://localhost:3000',  # Alternate
]
```

## Database

- **Producción**: PostgreSQL (configurar `DATABASE_URL` en `.env`)
- **Desarrollo**: SQLite (`db.sqlite3`)

## Throttling

| Endpoint | Rate |
|----------|------|
| Login | 10/min |
| Register | 5/min |
| Refresh | 10/min |

## Otros

- **Static root**: `static/`
- **Media root**: `media/`
- **Email**: SMTP configurable vía variables de entorno
- **Celery**: `CELERY_BROKER_URL=redis://localhost:6379/0` (configurado, no implementado en tareas)
