# API Endpoints Report - Zapotal Core Django (Backend Antiguo)

## Información General
- **Framework:** Django REST Framework
- **Base URL:** `http://localhost:8000` (por defecto)
- **Autenticación:** No implementada (login simple sin JWT/tokens)
- **Documentación Automática:** `/docs/` (Swagger UI)

## Endpoints por Recurso

### 1. Login
| Método | Endpoint | Descripción | Autenticación | Body |
|--------|----------|-------------|---------------|------|
| POST | `/api/login/` | Iniciar sesión | No | `{ email, password }` |

### 2. Usuarios (`/api/usuarios/`)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/usuarios/` | Listar usuarios |
| POST | `/api/usuarios/` | Crear usuario |
| GET | `/api/usuarios/{id}/` | Obtener usuario |
| PUT | `/api/usuarios/{id}/` | Actualizar usuario |
| PATCH | `/api/usuarios/{id}/` | Actualizar parcial |
| DELETE | `/api/usuarios/{id}/` | Eliminar usuario |

### 3. Comuneros (`/api/comuneros/`)
| Método | Endpoint |
|--------|----------|
| GET, POST, GET/{id}, PUT, PATCH, DELETE | `/api/comuneros/` |

### 4. Categorías (`/api/categorias/`)
CRUD completo en `/api/categorias/`

### 5. Noticias (`/api/noticias/`)
CRUD completo en `/api/noticias/`

### 6. Eventos (`/api/eventos/`)
CRUD completo en `/api/eventos/`

### 7. Comentarios (`/api/comentarios/`)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/comentarios/` | Listar (filtra por `?noticia=id` o `?evento=id`) |
| POST | `/api/comentarios/` | Crear comentario |
| GET | `/api/comentarios/{id}/` | Obtener comentario |
| PUT/PATCH | `/api/comentarios/{id}/` | Actualizar |
| DELETE | `/api/comentarios/{id}/` | Eliminar |

### 8. Reacciones (`/api/reacciones/`)
CRUD completo en `/api/reacciones/` (likes/dislikes)

### 9. Mensajes (`/api/mensajes/`)
CRUD completo en `/api/mensajes/`

### 10. Notificaciones (`/api/notificaciones/`)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/notificaciones/` | Listar (filtra por `?usuario_id=id`) |
| POST | `/api/notificaciones/` | Crear |
| GET/PUT/PATCH/DELETE | `/api/notificaciones/{id}/` | CRUD individual |

### 11. Multimedia (`/api/multimedia/`)
CRUD completo en `/api/multimedia/` (imágenes/videos)

### 12. Autoridades (`/api/autoridades/`)
CRUD completo en `/api/autoridades/`

### 13. Contacto (`/api/contacto/`)
CRUD completo en `/api/contacto/` (mensajes de contacto)

### 14. Libro de Reclamaciones (`/api/libro-reclamaciones/`)
CRUD completo (permiso público - `AllowAny`)

### 15. Documentación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/schema/` | Esquema OpenAPI (JSON) |
| GET | `/docs/` | Swagger UI |

## Resumen por Método

| Método | Cantidad de Endpoints |
|--------|----------------------|
| GET | 15 recursos × 2 (list + detail) ≈ 30 |
| POST | 15 |
| PUT | 15 |
| PATCH | 15 |
| DELETE | 15 |
| **Total** | **~90 endpoints** (DRF genera automáticamente) |

## Notas Importantes

### Autenticación
- **No hay autenticación con JWT/tokens** - solo login básico que retorna datos del usuario sin token
- Todas las APIs son públicas (sin restricción por defecto)
- El login no genera token, solo verifica credenciales y retorna perfil

### Filtros Disponibles
- Comentarios: `?noticia=id` o `?evento=id`
- Notificaciones: `?usuario_id=id` (requerido, sino retorna vacío)

### Campos Especiales en Respuestas
- Usuarios incluyen: `foto_perfil_url`, `nombre_completo`, `iniciales`
- Noticias/Eventos incluyen: `multimedia` anidado, `usuario` anidado
- Comentarios incluyen: `usuario_data`, `usuario_nombre`, `usuario_foto`, `usuario_iniciales`, `fecha_formateada`

### Particularidades
- **Libro de Reclamaciones:** Permiso `AllowAny` explícito (público)
- **Notificaciones:** Filtrado lógico por tipo (GLOBAL/COMUNEROS/PERSONAL) según el usuario
- **Contraseñas:** Almacenadas en texto plano (¡inseguro!)

## Archivos Clave
- `config/urls.py` - URL raíz
- `adminpanel/urls.py` - Definición de routers
- `adminpanel/views.py` - ViewSets y lógica
- `adminpanel/serializers.py` - Serializadores

---
*Reporte generado automáticamente por análisis de código fuente - Backend Django antiguo*