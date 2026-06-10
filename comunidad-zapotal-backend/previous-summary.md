
## Goal
- Django backend (comunidad-zapotal-backend) for Comunidad Zapotal enterprise monorepo — a community management platform for a rural farming community in Peru ("Sistema de gestión comunal para la Comunidad Campesina Zapotal")
- Multistack SaaS: Django API backend + React frontend (planned via django-vite) + Kotlin Android app + Spring Boot microservice

## Constraints & Preferences
- Monorepo restructured: old `zapotal_*` dirs → new `comunidad-zapotal-*` layout (backend, app, sb)
- MySQL database `comunidad_zapotal_db` at localhost:3306, root/no password
- Spanish locale (`es-pe`), Lima timezone
- Django 6.0.4, Python 3.12, DRF 3.17, JWT auth, Unfold admin theme

## Progress

### Backend (comunidad-zapotal-backend) — Mostly Complete
- **apps.core**: Shared utilities, validators (DNI 8 digits, phone 6-15 digits), `seed_data` management command
- **apps.accounts**: Custom `Usuario` model (email-based auth, ADMIN/COMUNERO/USUARIO roles), JWT login with rate limiting (10/h), CRUD viewset, migrations applied
- **apps.content**: 6 models (Categoria, Noticia, Evento, Multimedia, Comentario, Reaccion), full CRUD viewsets with search/filter/ordering
- **apps.comunidad**: Comunero + Autoridad models with active/inactive states and nested serializers
- **apps.messaging**: Mensaje + Notificacion models, user-scoped viewsets, mark-read actions
- **apps.reports**: Reporte, ContactoMensaje (public, AllowAny), LibroReclamacion (Peruvian legal complaints book)
- **Configuration**: DRF pagination/throttling, CORS (localhost:3000,5173), Unfold admin with blue scheme, security headers, logging, drf-spectacular OpenAPI
- **Deploy**: nginx.conf (SSL + reverse proxy), uvicorn config, deploy dir
- All 6 apps have models, serializers, views, urls, admin registrations, and tests

### Android App (comunidad-zapotal-app) — Partially Complete
- Kotlin + Gradle (KTS) with full UI structure: activities, fragments, adapters, XML layouts
- Retrofit API client (10 endpoints), 12+ data model classes
- Login, registration, news feed, events, authorities, profile management, reactions UI
- Navigation drawer + bottom nav

### Spring Boot Microservice (comunidad-zapotal-sb) — Early Stage
- Spring Boot 3.5.0 / Java 17 / Maven
- Controllers proxy to Django API via WebClient (port 8080 → Django 8000)
- No database of its own — acts as API gateway

### Git History
- `f8ca2c5` — feat: initial enterprise architecture (284 files, 37K+ lines)
- `4c83b1e` — v1.0.0: setup React + Django + uvicorn, README, start.bat
- `bc3e750` — start.bat: independent Python/React conditions
- `8968fd3` — fix: static files with uvicorn, STATIC_URL, asgi.py simplified
- `3532f2a` — **WIP (uncommitted)**: massive restructuring deleting old dirs and recreating new ones

### Known Issues
1. **MySQL timezone data**: `date_hierarchy` in admin crashes with timezone error. `load_tzdata.py` exists but may not be run. Timezone tables verified as populated.
2. **Root URL `/`**: Returns 404 (no frontend integration yet)
3. **Profanity filter**: `Comentario.tiene_palabras_prohibidas` field exists but no filter logic
4. **DNI verification**: Field exists in models but no verification workflow
5. **React frontend**: Old React app was deleted; django-vite is in requirements but no frontend scaffolded yet

## Next Steps
1. **Commit the WIP restructuring** (285 files changed, 37K+ lines removed — old→new directory rename)
2. **Run migrations + seed data** (`python manage.py seed_data --force`)
3. **Scaffold React frontend** with django-vite integration
4. **Fix timezone admin crash** — run `load_tzdata.py` if not already effective
5. **Polish Android app** — error handling, backend connection
6. **Expand Spring Boot** — add business logic beyond proxying
7. **Productionize** — CI/CD, SSL certs, domain config
