# Auditoría API Security Testing — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## PHASE 1: API DISCOVERY

### Endpoints Enumerados

```
GET    /api/usuarios/             → Listar usuarios
POST   /api/usuarios/             → Crear usuario
GET    /api/usuarios/{id}/        → Ver usuario
PUT    /api/usuarios/{id}/        → Reemplazar usuario
PATCH  /api/usuarios/{id}/        → Actualizar usuario
DELETE /api/usuarios/{id}/        → Eliminar usuario
POST   /api/login/                → Inicio de sesión
POST   /api/token/refresh/        → Refresh JWT

GET    /api/categorias/           → Listar categorías
POST   /api/categorias/           → Crear categoría
...

GET    /api/noticias/             → Listar noticias
POST   /api/noticias/             → Crear noticia
GET    /api/noticias/{id}/relacionadas/ → Noticias relacionadas
...

GET    /api/comentarios/          → Listar comentarios
POST   /api/comentarios/          → Crear comentario
...

GET    /api/reacciones/           → Listar reacciones
POST   /api/reacciones/           → Crear/toggle reacción
...

GET    /api/mensajes/             → Listar mensajes (TODOS)
POST   /api/mensajes/             → Enviar mensaje
...

GET    /api/notificaciones/       → Listar notificaciones (TODAS)
POST   /api/notificaciones/       → Crear notificación
...

GET    /api/contacto-mensajes/    → Listar mensajes de contacto (TODOS)
POST   /api/contacto-mensajes/    → Enviar mensaje de contacto
...

GET    /api/libro-reclamaciones/  → Listar reclamos (TODOS)
POST   /api/libro-reclamaciones/  → Crear reclamo
...
```

### Total: ~40 endpoints (CRUD × 10 recursos)

---

## PHASE 2: AUTHENTICATION TESTING

### 2.1 Token Endpoints

| Prueba | Resultado | Severidad |
|--------|-----------|-----------|
| POST /api/login/ sin credenciales | 400 Bad Request | Info |
| POST /api/login/ email inválido | 400 "Correo o contrasena incorrectos" | ✅ Seguro |
| POST /api/login/ password incorrecto | 400 "Correo o contrasena incorrectos" | ✅ Seguro |
| POST /api/token/refresh/ sin token | 401 | ✅ |
| POST /api/token/refresh/ token expirado | 401 | ✅ |

### 2.2 User Enumeration

```python
# Login view: Mismo mensaje y mismo status para email no existente y password incorrecto
# ✅ No hay user enumeration detectable
```

### 2.3 Autenticación Bypass

| Endpoint | Acceso sin auth | Método | Severidad |
|----------|----------------|--------|-----------|
| GET /api/usuarios/ | ✅ Permitido (read-only) | GET | Info |
| POST /api/usuarios/ | ❌ Requiere auth | POST | ✅ |
| DELETE /api/mensajes/{id} | ❌ Requiere auth | DELETE | ⚠️ Los mensajes no son del usuario (son CharField) |

---

## PHASE 3: AUTHORIZATION TESTING

### 3.1 Object-Level Authorization (IDOR)

| Prueba | Riesgo |
|--------|--------|
| GET /api/mensajes/ → ver mensajes de otros | **ALTO** — Cualquier usuario autenticado ve todos los mensajes |
| GET /api/notificaciones/ → ver notifs de otros | **ALTO** |
| GET /api/contacto-mensajes/ → ver datos de contacto | **ALTO** |
| GET /api/libro-reclamaciones/ → ver reclamos | **ALTO** |
| DELETE /api/usuarios/1 → eliminar otro usuario | **ALTO** |
| PATCH /api/comentarios/1 → editar comentario ajeno | **ALTO** |

### 3.2 Function-Level Authorization

| Prueba | Riesgo |
|--------|--------|
| USUARIO puede crear ADMIN | Medio — `tipo_usuario` no se valida |
| USUARIO puede crear autoridades | Medio |
| USUARIO puede marcar notificaciones como leídas | Bajo |

---

## PHASE 4: INPUT VALIDATION

### 4.1 SQL Injection

| Endpoint | Vector | Riesgo |
|----------|--------|--------|
| login_usuario | email field | ✅ Mitigado por Django ORM |
| ViewSets | query params | ✅ Mitigado por Django ORM |
| Comentario | contenido | ✅ Mitigado por Django ORM |

**No hay raw SQL en el código.** ✅

### 4.2 XSS

| Endpoint | Campo | Riesgo |
|----------|-------|--------|
| Comentario.contenido | TextField | ⚠️ No se sanitiza output en API (DRF serializa como string puro) |
| Noticia.contenido | TextField | ⚠️ Depende del frontend sanitizar |

**La API no sanitiza HTML en contenido.** Si el frontend renderiza como HTML sin escapar, hay XSS.

### 4.3 File Upload

| Endpoint | Campo | Riesgo |
|----------|-------|--------|
| POST /api/multimedia/ | archivo (FileField) | **ALTO** — Sin validación de tipo MIME |
| POST /api/usuarios/ | foto_perfil (ImageField) | ⚠️ Django ImageField valida que sea imagen, pero no validación de seguridad adicional |

---

## PHASE 5: RATE LIMITING

### 5.1 Pruebas

| Endpoint | Límite | Efectivo |
|----------|--------|----------|
| POST /api/login/ | LoginThrottle: 10/hour | ❌ **No aplicado** |
| GET /api/noticias/ | AnonRateThrottle: 100/day | ✅ Global activo |
| POST /api/usuarios/ | UserRateThrottle: 1000/day | ✅ Global activo |

### 5.2 Bypass

El `LoginThrottle` se define en `LoginThrottle` class pero **nunca se asigna a `login_usuario`**. El endpoint de login solo tiene el throttle global `AnonRateThrottle` de 100/día.

---

## PHASE 6: ERROR HANDLING

### 6.1 Information Disclosure

| Prueba | Resultado | Severidad |
|--------|-----------|-----------|
| GET /api/usuarios/999999 | `{"detail": "Not found."}` | ✅ Seguro |
| POST /api/usuarios/ con data inválida | Errores de validación DRF | ⚠️ Expone estructura interna |
| GET /api/ (raíz) | 404 DRF | ✅ |
| DEBUG=True stack trace | No probado (no hay endpoint que explote) | ⚠️ |

### 6.2 Debug Mode

```python
DEBUG = config('DEBUG', default=True, cast=bool)
```

**DEBUG por defecto True.** En producción con DEBUG=True, Django expone stack traces completos con settings (incluyendo SECRET_KEY, DB_PASSWORD) en errores 500.

---

## PHASE 7: SECURITY CHECKLIST

| Check | Estado | Evidencia |
|-------|--------|-----------|
| Authentication working | ⚠️ Parcial | Login funciona, AUTH_USER_MODEL roto |
| Authorization enforced | ❌ No | Sin permisos, sin roles, sin ownership |
| Input validated | ⚠️ Parcial | DNI ✅, Multimedia archivo ❌ |
| Rate limiting active | ⚠️ Parcial | Global ✅, Login ❌ |
| Errors sanitized | ⚠️ Parcial | Login ✅, DRF ❌ (detalles de validación expuestos) |
| Logging enabled | ❌ No | Logger definido, no usado |
| CORS configured | ❌ Inseguro | `CORS_ALLOW_ALL_ORIGINS = True` |
| HTTPS enforced | ❌ No | Sin SSL redirect |

---

## 8. Score API Security Testing: 20/100

| Fase | Peso | Score | Comentario |
|------|------|-------|------------|
| Discovery | 10% | 60 | Endpoints identificables |
| Authentication | 20% | 30 | Login funciona, JWT no integrado |
| Authorization | 25% | 0 | Sin permisos, IDOR en todos los recursos |
| Input Validation | 20% | 40 | ORM protege SQL, file upload inseguro |
| Rate Limiting | 10% | 20 | Login sin throttle específico |
| Error Handling | 15% | 25 | DEBUG default True, sin sanitización |
| **Total** | **100%** | **20** | **CRÍTICO — Sin autorización en ningún endpoint** |
