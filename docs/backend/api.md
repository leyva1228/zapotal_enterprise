# API REST — Endpoints

Base URL: `/api/v1/`

## Autenticación

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| POST | `/auth/login/` | Iniciar sesión (email + password) | 10/min |
| POST | `/auth/register/` | Registrar usuario | 5/min |
| POST | `/auth/refresh/` | Refrescar token JWT | - |
| POST | `/auth/logout/` | Cerrar sesión | Requiere auth |
| GET | `/auth/profile/` | Ver perfil propio | Requiere auth |
| PUT/PATCH | `/auth/profile/` | Actualizar perfil | Requiere auth |

## Content

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/content/categorias/` | Listar categorías | Público |
| POST | `/content/categorias/` | Crear categoría | Admin |
| GET | `/content/categorias/{id}/` | Detalle categoría | Público |
| PUT/PATCH | `/content/categorias/{id}/` | Actualizar | Admin |
| DELETE | `/content/categorias/{id}/` | Eliminar | Admin |
| GET | `/content/noticias/` | Listar noticias públicas | Público |
| POST | `/content/noticias/` | Crear noticia | Admin/Comunero |
| GET | `/content/noticias/{id}/` | Detalle noticia | Público |
| PUT/PATCH | `/content/noticias/{id}/` | Actualizar | Owner/Admin |
| DELETE | `/content/noticias/{id}/` | Eliminar | Owner/Admin |
| GET | `/content/noticias/{id}/relacionadas/` | Noticias relacionadas | Público |
| POST | `/content/noticias/{id}/incrementar_vistas/` | +1 vista | Público |
| GET | `/content/eventos/` | Listar eventos | Público |
| POST | `/content/eventos/` | Crear evento | Admin/Comunero |
| PUT/PATCH | `/content/eventos/{id}/` | Actualizar | Owner/Admin |
| DELETE | `/content/eventos/{id}/` | Eliminar | Owner/Admin |
| GET | `/content/multimedia/` | Listar multimedia | Público |
| POST | `/content/multimedia/` | Subir archivo | Admin |
| GET | `/content/comentarios/` | Listar (filtro noticia) | Público |
| POST | `/content/comentarios/` | Crear comentario | Requiere auth |
| PUT/PATCH | `/content/comentarios/{id}/` | Actualizar | Owner |
| DELETE | `/content/comentarios/{id}/` | Eliminar | Owner/Admin |
| GET | `/content/reacciones/` | Listar reacciones | Público |
| POST | `/content/reacciones/` | Crear reacción | Requiere auth |
| POST | `/content/reacciones/toggle/` | Toggle like/dislike | Requiere auth |

## Comunidad

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/comunidad/autoridades/` | Listar autoridades | Público |
| POST | `/comunidad/autoridades/` | Crear autoridad | Admin |
| GET | `/comunidad/autoridades/{id}/` | Detalle autoridad | Público |
| PUT/PATCH | `/comunidad/autoridades/{id}/` | Actualizar | Admin |
| DELETE | `/comunidad/autoridades/{id}/` | Eliminar | Admin |

## Messaging

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/messaging/mensajes/` | Mis mensajes | Requiere auth |
| POST | `/messaging/mensajes/` | Enviar mensaje | Requiere auth |
| GET | `/messaging/mensajes/{id}/` | Detalle mensaje | Propietario |
| PUT/PATCH | `/messaging/mensajes/{id}/` | Actualizar | Propietario |
| DELETE | `/messaging/mensajes/{id}/` | Eliminar | Propietario |
| GET | `/messaging/notificaciones/` | Mis notificaciones | Requiere auth |
| PATCH | `/messaging/notificaciones/{id}/` | Marcar leída | Requiere auth |

## Reports

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| POST | `/reports/contacto/` | Enviar mensaje de contacto | Público |
| GET | `/reports/contacto/{id}/` | Ver mensaje | Admin |
| DELETE | `/reports/contacto/{id}/` | Eliminar mensaje | Admin |
| POST | `/reports/reclamaciones/` | Enviar reclamación | Público |
| GET | `/reports/reclamaciones/{id}/` | Ver reclamación | Admin |
| PATCH | `/reports/reclamaciones/{id}/` | Actualizar estado | Admin |
| DELETE | `/reports/reclamaciones/{id}/` | Eliminar | Admin |

## Esquema y Documentación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/schema/` | OpenAPI Schema (JSON) |
| GET | `/api/docs/` | Swagger UI |

## Health

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health/` | Health check del sistema |

## Admin

| URL | Descripción |
|-----|-------------|
| `/backend/` | Admin personalizado |
