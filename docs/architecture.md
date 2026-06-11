# Arquitectura del Sistema

## Visión General

Zapotal Enterprise sigue una arquitectura de 3 capas:

```
┌──────────────────────────────────────────────────────────────┐
│                    Frontend (SPA)                            │
│  React 18 + TypeScript + Vite (comunidad_zapotal_frontend)  │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐   │
│  │  Auth   │ │   Pages  │ │  Admin   │ │  Components   │   │
│  └────┬────┘ └────┬─────┘ └────┬─────┘ └───────┬───────┘   │
│       └────────────┴────────────┴────────────────┘          │
│                        │  HTTP (JWT)                         │
└────────────────────────┼─────────────────────────────────────┘
                         │
┌────────────────────────┼─────────────────────────────────────┐
│              Backend (Django REST API)                       │
│  comunidad_zapotal_backend/zapotal_config/urls.py            │
│  ┌─────────────────────────────────────────────┐             │
│  │           API Gateway (DRF)                  │             │
│  │  /api/v1/accounts/   /api/v1/content/       │             │
│  │  /api/v1/comunidad/  /api/v1/messaging/     │             │
│  │  /api/v1/reports/    /api/docs/             │             │
│  └──────────┬─────────────────┬────────────────┘             │
│             │                 │                               │
│  ┌──────────▼──┐  ┌──────────▼──────────┐                   │
│  │   Apps      │  │  Core Infrastructure│                   │
│  │             │  │                     │                    │
│  │ accounts   │  │ constants.py        │                    │
│  │ content    │  │ validators.py       │                    │
│  │ comunidad  │  │ permissions.py      │                    │
│  │ messaging  │  │ pagination.py       │                    │
│  │ reports    │  │ exceptions.py       │                    │
│  │            │  │ admin_site.py       │                    │
│  └──────┬─────┘  │ health.py           │                    │
│         │        └─────────────────────┘                    │
│         │                                                    │
│  ┌──────▼──────┐  ┌─────────────────┐  ┌──────────────┐    │
│  │  PostgreSQL  │  │  Celery + Redis │  │  SimpleJWT   │    │
│  │  (dev: SQLite)│  │ (configurado)   │  │              │    │
│  └─────────────┘  └─────────────────┘  └──────────────┘    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│         zapotal_ai_orchestator (IA)          │
│  Módulo separado de IA                       │
└──────────────────────────────────────────────┘
```

## Flujo de Autenticación

```
Login (email+password) → /api/v1/accounts/login/ → JWT (access + refresh)
Access token en header: Authorization: Bearer <access>
Refresh: /api/v1/accounts/refresh/
Register: /api/v1/accounts/register/ → crea Usuario + Comunero
Profile: /api/v1/accounts/profile/ → GET/PUT
```

## Frontend → API

| Página | Endpoints que consume |
|--------|----------------------|
| Login | POST /api/v1/accounts/login/ |
| Register | POST /api/v1/accounts/register/ |
| Home | GET /api/v1/content/noticias/?estado=PUBLICADA, GET /api/v1/content/eventos/ |
| Noticias | GET /api/v1/content/noticias/, GET /api/v1/content/categorias/ |
| Noticia detalle | GET /api/v1/content/noticias/{id}/, GET /api/v1/content/comentarios/?noticia={id} |
| Nosotros | GET /api/v1/comunidad/autoridades/ |
| Admin | CRUD completo sobre content y accounts (requiere admin) |
| Mensajería | GET/POST /api/v1/messaging/mensajes/, GET /api/v1/messaging/notificaciones/ |
| Contacto | POST /api/v1/reports/contacto/ (público) |
| Reclamaciones | POST /api/v1/reports/reclamaciones/ (público) |
| Donaciones | Redirección externa a Paga.pe (sin API local) |

## Tecnologías Clave

- **Django 5.x** con **DRF** para REST API
- **SimpleJWT** para autenticación stateless
- **drf-spectacular** para documentación OpenAPI/Swagger
- **django-cors-headers** para CORS (orígenes: localhost:5173, localhost:3000)
- **django-throttling** para rate limiting en login/register
- **django-filter** para búsqueda y filtrado en endpoints
- **Celery + Redis** configurados en settings (tareas asíncronas disponibles)
- **Pillow** para manejo de imágenes de perfil
