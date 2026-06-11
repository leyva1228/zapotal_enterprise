# Backend - comunidad_zapotal_backend

Django 5.x REST API para Zapotal Enterprise.

## Estructura

```
comunidad_zapotal_backend/
├── manage.py
├── requirements.txt
├── zapotal_config/
│   ├── settings.py       # Configuración principal
│   ├── urls.py           # Routing principal
│   ├── wsgi.py           # WSGI entry point
│   └── asgi.py           # ASGI entry point
├── apps/
│   ├── core/             # Base compartida
│   ├── accounts/         # Usuarios y autenticación
│   ├── content/          # Noticias, eventos, multimedia
│   ├── comunidad/        # Autoridades comunales
│   ├── messaging/        # Mensajería privada
│   └── reports/          # Contacto y reclamaciones
└── static/               # Archivos estáticos
```

## Tecnologías

- Django 5.x
- Django REST Framework
- SimpleJWT (autenticación JWT)
- drf-spectacular (documentación OpenAPI)
- django-cors-headers
- django-filter
- django-throttling
- Celery + Redis
- PostgreSQL (producción) / SQLite (desarrollo)

## Apps

| Documento | Descripción |
|-----------|-------------|
| `settings.md` | Configuración de Django settings |
| `core.md` | Constantes, validadores, permisos |
| `accounts.md` | Modelos, servicios, vistas de usuarios |
| `content.md` | Contenido: noticias, eventos, multimedia |
| `comunidad.md` | Autoridades comunales |
| `messaging.md` | Mensajería entre usuarios |
| `reports.md` | Contacto y libro de reclamaciones |
