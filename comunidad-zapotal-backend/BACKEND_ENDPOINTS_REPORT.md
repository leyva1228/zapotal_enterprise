# API Endpoints Report - Comunidad Zapotal Backend

## Información General
- **Framework:** Express.js
- **Base URL:** `http://localhost:3000` (por defecto, configurable via PORT en .env)
- **Rate Limiting:** 100 solicitudes cada 15 minutos por IP para rutas `/api/*`
- **Autenticación:** JWT (Bearer token) requerido para rutas protegidas

## Endpoints por Módulo

### 1. Health Check
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/health` | Verificar estado del servidor | No |

### 2. Auth (`/api/auth`)
| Método | Endpoint | Descripción | Autenticación | Body/Params |
|--------|----------|-------------|---------------|--------------|
| POST | `/api/auth/register` | Registrar nuevo usuario | No | `{ nombre, email, password, ... }` (validado) |
| POST | `/api/auth/login` | Iniciar sesión | No | `{ email, password }` |
| GET | `/api/auth/verify` | Verificar token JWT | Sí | - |

### 3. Users (`/api/users`)
| Método | Endpoint | Descripción | Autenticación | Params/Body |
|--------|----------|-------------|---------------|-------------|
| GET | `/api/users/:id/profile` | Obtener perfil público de usuario | No | `:id` - ID de usuario |
| GET | `/api/users/profile` | Obtener mi propio perfil | Sí | - |
| PUT | `/api/users/profile` | Actualizar mi perfil | Sí | Body con campos a actualizar |
| PUT | `/api/users/change-password` | Cambiar contraseña | Sí | `{ oldPassword, newPassword }` |
| POST | `/api/users/upload-avatar` | Subir avatar | Sí | `multipart/form-data` con archivo |
| GET | `/api/users/search` | Buscar usuarios | Sí | Query: `?q=termino` |

### 4. Communities (`/api/communities`)
| Método | Endpoint | Descripción | Autenticación | Params/Body |
|--------|----------|-------------|---------------|-------------|
| GET | `/api/communities` | Listar todas las comunidades | No | Query: paginación opcional |
| GET | `/api/communities/:id` | Obtener comunidad por ID | No | `:id` - ID de comunidad |
| GET | `/api/communities/:id/members` | Listar miembros de comunidad | No | `:id` - ID de comunidad |
| GET | `/api/communities/:id/posts` | Listar posts de comunidad | No | `:id` - ID de comunidad |
| POST | `/api/communities` | Crear nueva comunidad | Sí | `{ nombre, descripcion, ... }` |
| PUT | `/api/communities/:id` | Actualizar comunidad | Sí | `:id`, body con campos |
| DELETE | `/api/communities/:id` | Eliminar comunidad | Sí | `:id` |
| POST | `/api/communities/:id/join` | Unirse a comunidad | Sí | `:id` |
| POST | `/api/communities/:id/leave` | Salir de comunidad | Sí | `:id` |
| PUT | `/api/communities/:id/members/:userId/role` | Actualizar rol de miembro | Sí | `:id`, `:userId`, body `{ role }` |

### 5. Posts (`/api/posts`)
| Método | Endpoint | Descripción | Autenticación | Params/Body |
|--------|----------|-------------|---------------|-------------|
| GET | `/api/posts` | Listar todos los posts | No | Query: paginación, filtros |
| GET | `/api/posts/:id` | Obtener post por ID | No | `:id` |
| POST | `/api/posts` | Crear nuevo post | Sí | `multipart/form-data` con `{ titulo, contenido, comunidad_id, imagen? }` |
| PUT | `/api/posts/:id` | Actualizar post | Sí | `:id`, body con campos |
| DELETE | `/api/posts/:id` | Eliminar post | Sí | `:id` |

### 6. Comments (`/api/comments`)
| Método | Endpoint | Descripción | Autenticación | Params/Body |
|--------|----------|-------------|---------------|-------------|
| GET | `/api/comments/post/:postId` | Listar comentarios de un post | No | `:postId` |
| POST | `/api/comments` | Crear comentario | Sí | `{ contenido, post_id }` |
| PUT | `/api/comments/:id` | Actualizar comentario | Sí | `:id`, body `{ contenido }` |
| DELETE | `/api/comments/:id` | Eliminar comentario | Sí | `:id` |

### 7. Likes (`/api/likes`)
| Método | Endpoint | Descripción | Autenticación | Params |
|--------|----------|-------------|---------------|--------|
| POST | `/api/likes/post/:postId` | Dar like a un post | Sí | `:postId` |
| DELETE | `/api/likes/post/:postId` | Quitar like de un post | Sí | `:postId` |
| GET | `/api/likes/post/:postId` | Obtener lista de likes de un post | Sí | `:postId` |

### 8. Follows (`/api/follows`)
| Método | Endpoint | Descripción | Autenticación | Params |
|--------|----------|-------------|---------------|--------|
| POST | `/api/follows/:userId` | Seguir a un usuario | Sí | `:userId` |
| DELETE | `/api/follows/:userId` | Dejar de seguir a un usuario | Sí | `:userId` |
| GET | `/api/follows/followers/:userId` | Obtener seguidores de un usuario | Sí | `:userId` |
| GET | `/api/follows/following/:userId` | Obtener usuarios que sigue | Sí | `:userId` |

### 9. Notifications (`/api/notifications`)
| Método | Endpoint | Descripción | Autenticación | Params/Body |
|--------|----------|-------------|---------------|-------------|
| GET | `/api/notifications` | Obtener mis notificaciones | Sí | Query: paginación |
| PUT | `/api/notifications/:id/read` | Marcar notificación como leída | Sí | `:id` |
| PUT | `/api/notifications/read-all` | Marcar todas como leídas | Sí | - |
| DELETE | `/api/notifications/:id` | Eliminar notificación | Sí | `:id` |

### 10. Dashboard (`/api/dashboard`)
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/dashboard/stats` | Obtener estadísticas del dashboard | Sí |
| GET | `/api/dashboard/recent-activity` | Obtener actividad reciente | Sí |

## Resumen de Endpoints por Método

| Método | Cantidad |
|--------|----------|
| GET | 20 |
| POST | 11 |
| PUT | 9 |
| DELETE | 8 |
| **Total** | **48** |

## Notas Importantes

### Autenticación
- Todas las rutas con "Sí" en la columna Autenticación requieren header: `Authorization: Bearer <token>`
- El token se obtiene de `/api/auth/login`

### Parámetros Comunes
- **Paginación:** Muchos endpoints GET soportan `?page=1&limit=10`
- **Archivos:** Los endpoints con `upload-avatar` o `posts` con imagen usan `multipart/form-data`

### Middlewares Aplicados
- **CORS:** Habilitado globalmente
- **Rate Limit:** 100 req/15min para rutas `/api/*`
- **Validación:** `express-validator` en rutas específicas (register, login, posts, comments, etc.)
- **Manejo de errores:** Global 404 y 500

### Archivos de Rutas
- `src/routes/auth.routes.js`
- `src/routes/user.routes.js`
- `src/routes/community.routes.js`
- `src/routes/post.routes.js`
- `src/routes/comment.routes.js`
- `src/routes/like.routes.js`
- `src/routes/follow.routes.js`
- `src/routes/notification.routes.js`
- `src/routes/dashboard.routes.js`

## Cómo Usar Este Reporte
1. Levantar el servidor con `npm start` o `npm run dev`
2. Usar la base URL `http://localhost:3000` (o el puerto configurado)
3. Para rutas protegidas, primero autenticarse en `/api/auth/login`
4. Incluir el token JWT en el header `Authorization: Bearer <token>`

---
*Reporte generado automáticamente por análisis de código fuente*