# 04 — Endpoints REST y Contratos HTTP

> **Tipo:** Auditoría — Catálogo completo de endpoints
> **Alcance:** todos los endpoints REST del gateway, métodos, paths, DTOs, códigos de error.

---

## 1. Prefijos de URL

| Prefijo | Controllers | Notas |
|---|---|---|
| `/api/auth/**` | `AuthController` | 9 endpoints |
| `/api/comentarios/**` | `ComentariosController` | 5 endpoints |
| `/api/contacto-mensaje/**` | `ContactoMensajeController` | 1 endpoint |
| `/api/eventos/**` | `EventosController` | 1 endpoint |
| `/api/libro-reclamaciones/**` | `LibroReclamacionController` | 2 endpoints |
| `/api/mensajes/**` | `MensajesController` | 5 endpoints |
| `/api/multimedias/**` | `MultimediaController` | 1 endpoint |
| `/api/noticias/**` | `NoticiasController` | 1 endpoint |
| `/api/notificaciones/**` | `NotificacionesController` | 1 endpoint |
| `/api/reacciones/**` | `ReaccionesController` | 2 endpoints |
| `/api/reportes-contenido/**` | `ReportesContenidoController` | 3 endpoints |
| `/api/autoridades/**` | `AutoridadesController` | 1 endpoint |
| `/api/favoritos/**` | `FavoritoController` | 5 endpoints (JPA propia) |
| `/api/health`, `/api/django-test` | `HealthController` | 2 endpoints |
| `/media/**` | `MediaProxyController` | Proxy de media de Django |
| `/actuator/**` | (Spring Boot Actuator) | Health, info, metrics |

**Total: ~50 endpoints** (+ actuator).

## 2. Catálogo detallado por módulo

### 2.1. Auth (9 endpoints)

| # | Método | Path | Body (Request DTO) | Validación | Response DTO | Auth requerida |
|---|---|---|---|---|---|---|
| 1 | POST | `/api/auth/register` | `RegisterRequestDTO` | `@Valid` parcial | `UsuarioDTO` | No |
| 2 | POST | `/api/auth/login` | `LoginRequestDTO` | `@Valid` completo | `LoginResponseDTO` | No |
| 3 | POST | `/api/auth/refresh` | `RefreshTokenRequestDTO` | — | `RefreshTokenResponseDTO` | No |
| 4 | GET | `/api/auth/me` | — | — | `UsuarioDTO` | Sí (Bearer) |
| 5 | PATCH | `/api/auth/update` | `UpdateProfileRequestDTO` | (sin @Valid) | `UsuarioDTO` | Sí (Bearer) |
| 6 | GET | `/api/auth/seguridad` | — | — | `SeguridadResponseDTO` | Sí (Bearer, @RequestHeader) |
| 7 | POST | `/api/auth/cambiar-password` | `CambiarPasswordRequestDTO` | `@Valid` | `Void` | Sí (Bearer) |
| 8 | POST | `/api/auth/desactivar-cuenta` | `DesactivarCuentaRequestDTO` | `@Valid` | `MessageResponseDTO` | Sí (Bearer) |
| 9 | POST | `/api/auth/reenviar-verificacion` | — | — | `MessageResponseDTO` | Sí (Bearer) |

**Observaciones:**

- El controller es `@RequestMapping("/api/auth")` y los paths internos son relativos.
- El endpoint 6 usa `@RequestHeader("Authorization") String authorizationHeader` en lugar de `HttpServletRequest request` + `AuthHeaderUtil`. Inconsistencia.
- El endpoint 3 (`refresh`) no requiere Bearer (es para refrescar el token).

### 2.2. Comentarios (5 endpoints)

| # | Método | Path | Body | Validación | Response |
|---|---|---|---|---|---|
| 1 | GET | `/api/comentarios` | — | — | `PagedResponseDTO<List<ComentarioResponseDTO>>` |
| 2 | GET | `/api/comentarios/noticia/{noticiaId}` | — | — | idem |
| 3 | GET | `/api/comentarios/evento/{eventoId}` | — | — | idem |
| 4 | POST | `/api/comentarios` | `ComentarioRequestDTO` | `@Valid` parcial | `ComentarioResponseDTO` |
| 5 | DELETE | `/api/comentarios/{comentarioId}` | — | — | `void` (204) |

**Observación:** el endpoint 1 reenvía `request.getQueryString()` al service (filtros de Django). Los demás no.

### 2.3. ContactoMensaje (1 endpoint)

| # | Método | Path | Body | Response |
|---|---|---|---|---|
| 1 | POST | `/api/contacto-mensaje` | `ContactoMensajeRequestDTO` | `ContactoMensajeResponseDTO` |

### 2.4. Eventos (1 endpoint)

| # | Método | Path | Response |
|---|---|---|---|
| 1 | GET | `/api/eventos` | `PagedResponseDTO<List<EventoResponseDTO>>` |

### 2.5. LibroReclamacion (2 endpoints)

| # | Método | Path | Body | Validación | Response |
|---|---|---|---|---|---|
| 1 | POST | `/api/libro-reclamaciones` | `LibroReclamacionRequestDTO` | `@Valid` | `LibroReclamacionResponseDTO` |
| 2 | GET | `/api/libro-reclamaciones/me` | — | — | `PagedResponseDTO<List<LibroReclamacionResponseDTO>>` |

### 2.6. Mensajes (5 endpoints)

| # | Método | Path | Body | Validación | Response |
|---|---|---|---|---|---|
| 1 | GET | `/api/mensajes` | — | — | `PagedResponseDTO<List<MensajeResponseDTO>>` |
| 2 | GET | `/api/mensajes/recibidos` | — | — | idem |
| 3 | GET | `/api/mensajes/enviados` | — | — | idem |
| 4 | POST | `/api/mensajes` | `MensajeRequestDTO` | `@Valid` completo | `MensajeResponseDTO` |
| 5 | POST | `/api/mensajes/{id}/marcar-leido` | — | — | `MensajeResponseDTO` |

### 2.7. Multimedia (1 endpoint)

| # | Método | Path | Response |
|---|---|---|---|
| 1 | GET | `/api/multimedias` | `PagedResponseDTO<List<MultimediaResponseDTO>>` |

### 2.8. Noticias (1 endpoint)

| # | Método | Path | Response |
|---|---|---|---|
| 1 | GET | `/api/noticias` | `PagedResponseDTO<List<NoticiaResponseDTO>>` |

### 2.9. Notificaciones (1 endpoint)

| # | Método | Path | Response |
|---|---|---|---|
| 1 | GET | `/api/notificaciones` | `PagedResponseDTO<List<NotificacionResponseDTO>>` |

### 2.10. Reacciones (2 endpoints)

| # | Método | Path | Body | Response |
|---|---|---|---|---|
| 1 | GET | `/api/reacciones` | — | `PagedResponseDTO<List<ReaccionResponseDTO>>` |
| 2 | POST | `/api/reacciones` | `ReaccionRequestDTO` | `ReaccionResponseDTO` |

### 2.11. ReportesContenido (3 endpoints)

| # | Método | Path | Body | Response |
|---|---|---|---|---|
| 1 | GET | `/api/reportes-contenido` | — | `PagedResponseDTO<List<ReporteContenidoResponseDTO>>` |
| 2 | POST | `/api/reportes-contenido` | `ReporteContenidoRequestDTO` | `ReporteContenidoResponseDTO` |
| 3 | (otro) | ... | ... | ... |

### 2.12. Autoridades (1 endpoint)

| # | Método | Path | Response |
|---|---|---|---|
| 1 | GET | `/api/autoridades` | `PagedResponseDTO<List<AutoridadResponseDTO>>` |

### 2.13. Favoritos (5 endpoints, JPA propia)

| # | Método | Path | Body | Validación | Response |
|---|---|---|---|---|---|
| 1 | GET | `/api/favoritos` | — | (interna JWT) | `List<FavoritoResponseDTO>` |
| 2 | GET | `/api/favoritos/count` | — | (interna JWT) | `Long` |
| 3 | POST | `/api/favoritos` | `FavoritoRequestDTO` | `@Valid` + manual | `FavoritoResponseDTO` |
| 4 | GET | `/api/favoritos/existe?tipoContenido=&contenidoId=` | — | (interna JWT) | `Boolean` |
| 5 | DELETE | `/api/favoritos/{favoritoId}` | — | (interna JWT) | `void` (204) |
| 6 | DELETE | `/api/favoritos?tipoContenido=&contenidoId=` | — | (interna JWT) | `void` (204) |

**Diferencia clave:** estos endpoints **NO** consultan Django. Leen/escriben directamente en MySQL local (JPA).

### 2.14. Health (2 endpoints)

| # | Método | Path | Response |
|---|---|---|---|
| 1 | GET | `/api/health` | `"Zapotal Gateway funcionando correctamente"` (estático) |
| 2 | GET | `/api/django-test` | String (HTML de Django si OK, error si falla) |

### 2.15. MediaProxy (1 endpoint, dinámico)

| # | Método | Path | Response |
|---|---|---|---|
| 1 | GET | `/media/**` | `byte[]` con `Content-Type` y `Cache-Control: max-age=86400` |

**Path dinámico:** cualquier URL bajo `/media/` se reenvía a Django. Ej: `/media/noticias/2026/foto.jpg` → `http://django:8000/media/noticias/2026/foto.jpg`.

### 2.16. Actuator (Spring Boot)

| # | Path | Habilitado |
|---|---|---|
| 1 | `/actuator/health` | Sí |
| 2 | `/actuator/info` | Sí |
| 3 | `/actuator/metrics` | Sí |

`show-details: always` → expone detalles de DB, disco, etc. (sensible en prod).

## 3. Códigos de error (vía `GlobalExceptionHandler`)

| Excepción | Status | Body | Notas |
|---|---|---|---|
| `WebClientResponseException` | El statusCode de Django | `ErrorResponseDTO` con `message = body crudo de Django` | ⚠️ Inconsistencia |
| `MethodArgumentNotValidException` | 400 | `ErrorResponseDTO` con `message = "campo: mensaje"` (solo el primer error) | ⚠️ Pierde info de errores múltiples |
| `Exception` (cualquier otra) | 500 | `ErrorResponseDTO` con `message = "Error interno del gateway"` | Oculta detalles (bien) |

**Campos de `ErrorResponseDTO`:**

```java
public record ErrorResponseDTO(
    String timestamp,    // LocalDateTime.now().toString()
    int status,          // código HTTP
    String error,        // ex.getStatusText() o "Bad Request" o "Internal Server Error"
    String message,      // varía según excepción
    String path          // request.getRequestURI()
) {}
```

**Faltante:** `fieldErrors` (mapa de campo → mensaje) que el Lab 5 mostraba.

## 4. Códigos de error NO manejados

`GlobalExceptionHandler` solo captura 3 tipos. El gateway **NO** maneja explícitamente:

- `HttpMessageNotReadableException` (JSON malformado en body) → 400 default de Spring.
- `MissingServletRequestParameterException` (falta query param) → 400 default.
- `MethodArgumentTypeMismatchException` (tipo incorrecto en path variable) → 400 default.
- `org.springframework.security.access.AccessDeniedException` → 403 default (no llegaría porque `permitAll`).
- `org.springframework.web.HttpRequestMethodNotSupportedException` → 405 default.

**Hallazgo:** el `GlobalExceptionHandler` es minimalista. Para una API de ~50 endpoints, debería capturar al menos los 4-5 errores más comunes.

## 5. Patrones de autenticación

### 5.1. 3 patrones usados inconsistentemente

| Patrón | Controllers que lo usan | Ejemplo |
|---|---|---|
| `HttpServletRequest` + `AuthHeaderUtil` | 11 controllers | `AuthController` (excepto un método), `ComentariosController`, etc. |
| `@RequestHeader("Authorization")` | 1 método de `AuthController` | `AuthController.seguridad()` |
| Pasar el header directamente al client | Todos los clients (vía service) | `eventosService.obtenerEventos(authorizationHeader)` |

**Hallazgo:** los 3 patrones coexisten. Debería estandarizarse a uno.

### 5.2. `AuthHeaderUtil.getBearerToken()`

```java
public static String getBearerToken(HttpServletRequest request) {
    String header = request.getHeader("Authorization");
    if (header == null || header.isBlank()) return null;
    if (!header.startsWith("Bearer ")) return null;
    return header;  // ⚠️ retorna el header completo, no solo el token
}
```

**Hallazgo:** el método se llama `getBearerToken` pero **retorna el header completo** (con "Bearer " incluido), no el token solo. Es un nombre engañoso. La lógica downstream asume que el header completo está OK (porque el WebClient lo reenvía tal cual).

## 6. Headers HTTP personalizados

| Header | Origen | Uso |
|---|---|---|
| `Authorization: Bearer *** | Cliente móvil | Reenviado a Django por el filtro |
| `X-Internal-API-Key` | — | **No usado** en el gateway (sí lo usaba el pdf-worker eliminado) |
| `Cache-Control: public, max-age=86400` | `MediaProxyController` | Añadido al servir media de Django |
| `Content-Type: application/json` | Default Spring | Body de request/response |

## 7. Path mapping vs Django

**Comparación de paths** (gateway vs Django):

| Path gateway | Path Django (asumido) |
|---|---|
| `GET /api/auth/me` | `GET /api/v1/me/` |
| `GET /api/eventos` | `GET /api/v1/eventos/` |
| `POST /api/auth/login` | `POST /api/v1/login/` |
| ... | ... |

**Análisis:** el gateway **redefine los paths** (sin `/api/v1/`). Esto es una **ventaja** del BFF: el cliente móvil habla `/api/auth/login` y el gateway lo traduce a `/api/v1/login/`. El móvil queda desacoplado del versionado de Django.

**Pero también es un riesgo:** si Django cambia `/api/v1/login/` a `/api/v2/login/`, el gateway rompe **silenciosamente** (porque no hay test que lo detecte).

## 8. Webhooks

**Búsqueda:** no hay endpoints con `@PostMapping` que parezcan webhooks (no hay `@RequestBody WebhookPayload`, no hay firma HMAC, no hay `X-Hub-Signature`).

**Conclusión:** el gateway **no expone webhooks**. Solo consume Django (outbound) y expone REST para móvil (inbound).

## 9. Resumen de endpoints

| Categoría | # | Patrón |
|---|---|---|
| Passthrough 1:1 a Django | ~40 | Controller → Service → Client → WebClient → Django |
| Con validación de input | ~6 | `@Valid` en `@RequestBody` |
| Con lógica propia (favoritos) | 5 | Controller → Service → JPA → MySQL |
| Diagnóstico | 2 | Health estático + test de Django |
| Proxy de media | 1 | WebClient reenvía + añade Cache-Control |
| Actuator | 3 | Health, info, metrics |

**Total: ~50 endpoints REST** + actuator.

**Hallazgos clave:**

1. ✅ Hay Bean Validation en DTOs request (parcial, mejorable).
2. ✅ Hay un `GlobalExceptionHandler` con `ErrorResponseDTO` canónico.
3. ❌ No hay webhooks (consumir ni exponer).
4. ❌ No hay OpenAPI/Swagger.
5. ❌ El `MediaProxyController` es la única pieza con valor agregado real (cache).
6. ❌ El módulo `favoritos` rompe el patrón y tiene problemas de seguridad.

Ver `08_auditoria_hallazgos.md` para el análisis completo.
