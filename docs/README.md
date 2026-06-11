# Zapotal Enterprise

Portal web de la comunidad campesina **Zapotal** — plataforma integral de gestión comunal con autenticación, noticias, eventos, mensajería privada, notificaciones, libro de reclamaciones y orquestador de IA.

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Django 5.x + Django REST Framework |
| Frontend | React 18 + TypeScript + Vite |
| IA Orchestator | Python (módulo separado `zapotal_ai_orchestator`) |
| DB | PostgreSQL (dev: SQLite) |
| Auth | JWT (SimpleJWT) |
| Async | Celery + Redis (configurado) |
| Docs API | drf-spectacular (Swagger/OpenAPI) |

## Apps del Backend

| App | Propósito |
|-----|-----------|
| `core` | Base: constantes, validadores, permisos, paginación, excepciones, health checks |
| `accounts` | Usuarios y comuneros: registro, login, perfil, refresh JWT |
| `content` | Contenido: categorías, noticias, eventos, multimedia, comentarios, reacciones |
| `comunidad` | Autoridades comunales |
| `messaging` | Mensajería privada entre usuarios + notificaciones |
| `reports` | Contacto y libro de reclamaciones |

## Frontend

Aplicación SPA con React + TypeScript, páginas principales:

- Login / Register / Profile
- Home / Noticias / Eventos
- Nosotros (autoridades)
- Admin (gestión de contenido)
- Contacto / Libro de Reclamaciones
- Donaciones (Paga.pe)

## Índice de documentos

| Documento | Contenido |
|-----------|-----------|
| `architecture.md` | Arquitectura general del sistema |
| `setup.md` | Instalación, configuración y despliegue |
| `api.md` | Endpoints REST, autenticación y esquemas |
| `TODO.md` | Progreso de documentación |
| `VERSIONING.md` | Historial de versiones |
| `backend/README.md` | Visión general del backend |
| `backend/settings.md` | Configuración de Django settings |
| `backend/core.md` | App core (constantes, validadores, permisos) |
| `backend/accounts.md` | App accounts (usuarios, comuneros, auth) |
| `backend/content.md` | App content (noticias, eventos, multimedia, etc.) |
| `backend/comunidad.md` | App comunidad (autoridades) |
| `backend/messaging.md` | App messaging (mensajes, notificaciones) |
| `backend/reports.md` | App reports (contacto, reclamaciones) |
| `frontend/README.md` | Visión general del frontend |
| `frontend/auth.md` | Autenticación (login, registro, perfil) |
