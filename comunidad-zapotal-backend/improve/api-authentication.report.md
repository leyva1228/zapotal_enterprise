# api-authentication — Auditoría de autenticación de API

## Resumen Ejecutivo

Autenticación JWT con SimpleJWT. Email como identificador único (USERNAME_FIELD). Rate limiting en login (10/hora). Sin logout endpoint, sin refresh rotation, sin blacklist de tokens. Adecuado para MVP. Faltan características de producción.

## Análisis Detallado

### JWT Implementation
- ✅ SimpleJWT configurado con `SIMPLE_JWT` en settings.py
- ✅ Access token + refresh token
- ✅ `AUTH_HEADER_TYPES: 'Bearer'`
- ✅ Token obtenido via `/api/token/` y `/api/token/refresh/`
- ⚠️ Sin `ACCESS_TOKEN_LIFETIME` visible — default 5 minutos (quizás muy corto para frontend)
- ⚠️ Sin `ROTATE_REFRESH_TOKENS = True` — no se rotan refresh tokens
- ⚠️ Sin `BLACKLIST_AFTER_ROTATION = True` — no se blacklistean tokens viejos

### Endpoints de Autenticación

| Endpoint | Método | Propósito | Protección |
|----------|--------|-----------|------------|
| `/api/login/` | POST | Login personalizado | Throttle 10/hora |
| `/api/token/` | POST | Obtener JWT pair | Ninguna |
| `/api/token/refresh/` | POST | Refrescar access token | Ninguna (requiere refresh token válido) |
| `/api/usuarios/` | POST | Registro | Ninguna (AllowAny) |

### Password Security
- ✅ Passwords almacenadas con Django PBKDF2 (configurable)
- ✅ Validación de password en `UsuarioRegistroSerializer.validate_password`
- ⚠️ No se usa AUTH_PASSWORD_VALIDATORS de Django para reforzar complejidad

### User Enumeration
- ❌ **LoginSerializer.validar_usuario activo()** — en LoginSerializer, la lógica distingue:
  - "El correo electrónico no está registrado" (usuario no existe)
  - "La cuenta está desactivada" (existe pero inactiva)
  - "Contraseña incorrecta" (existe pero password malo)
  - Esto permite enumerar qué correos están registrados

### Refresh Token Security
- ⚠️ Sin `ROTATE_REFRESH_TOKENS` — refresh token es reutilizable indefinidamente
- ⚠️ Sin logout endpoint — no se pueden invalidar sesiones
- ⚠️ No se implementa token expiry check server-side más allá de lifetime

### Best Practices
- ✅ HTTPS assumed
- ✅ Tokens via Authorization header (Bearer)
- ✅ No tokens in URL parameters
- ✅ No sensitive data in JWT payload (solo user id)
- ❌ No HttpOnly cookies (tokens via header — expuestos a XSS en frontend)
- ❌ Sin rate limiting en `/api/token/` y `/api/token/refresh/`

## Puntos Fuertes
1. Email como identifier (USERNAME_FIELD) — correcto para aplicación moderna
2. JWT con SimpleJWT — implementación madura y segura
3. Rate limiting en login (10/hora) — mitigación de brute force
4. Password validation en serializer de registro
5. LoginSerializer valida estado de la cuenta

## Vulnerabilidades
1. User enumeration (login revela existencia de cuentas)
2. Sin refresh rotation (refresh token reusable)
3. Sin logout / token revocation
4. Sin rate limiting en endpoints JWT estándar
5. Sin password validators de Django configurados

## Recomendaciones
1. Mensaje genérico en login: "Credenciales inválidas" (sin distinguir existencia)
2. `SIMPLE_JWT['ROTATE_REFRESH_TOKENS'] = True`
3. `SIMPLE_JWT['BLACKLIST_AFTER_ROTATION'] = True` + `'rest_framework_simplejwt.token_blacklist'` en INSTALLED_APPS
4. Endpoint de logout que blacklistea el token actual
5. Rate limiting en `/api/token/` y `/api/token/refresh/`
6. Agregar `AUTH_PASSWORD_VALIDATORS` en settings.py (mín. 8 chars, no similar al email)
7. Considerar `ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)` (mejor experiencia UX)

## Conclusión

Sistema de autenticación funcional con JWT. Las carencias principales son seguridad de refresh tokens y user enumeration. Recomendación: implementar rotation + blacklist antes de producción; corregir mensajes de login inmediatamente.
