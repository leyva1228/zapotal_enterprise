# 07 — Manejo de Errores, Logging y Observabilidad

> **Tipo:** Auditoría — Cómo se manejan los errores y qué se observa
> **Alcance:** `GlobalExceptionHandler`, logging, métricas, health checks.

---

## 1. `GlobalExceptionHandler` — Lo mejor del proyecto

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(WebClientResponseException.class)
    public ResponseEntity<ErrorResponseDTO> handleWebClientException(...) { ... }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponseDTO> handleValidation(...) { ... }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponseDTO> handleGeneralException(...) { ... }
}
```

### 1.1. Handler de `WebClientResponseException` (Django devolvió error)

```java
@ExceptionHandler(WebClientResponseException.class)
public ResponseEntity<ErrorResponseDTO> handleWebClientException(
        WebClientResponseException ex, HttpServletRequest request) {
    return ResponseEntity.status(ex.getStatusCode()).body(
        new ErrorResponseDTO(
            LocalDateTime.now().toString(),
            ex.getStatusCode().value(),
            ex.getStatusText(),
            ex.getResponseBodyAsString(),  // ⚠️ body crudo de Django
            request.getRequestURI()
        )
    );
}
```

**Fortalezas:**

- Captura cualquier error que venga de Django.
- Reusa el status code de Django (no lo sobrescribe con 500).
- Usa el `ErrorResponseDTO` canónico.

**Debilidades:**

- ⚠️ `ex.getResponseBodyAsString()` **repite el cuerpo JSON crudo de Django** en el campo `message` del gateway. Esto rompe la consistencia: el cliente móvil recibe un `ErrorResponseDTO` con `message` siendo un JSON de Django (no un mensaje en español).
- **No loguea el error** en el servidor. Si Django falla, el gateway no deja rastro en sus logs (más allá del "DJANGO -> SPRING 200" del filtro).
- **No incluye** `WebClientResponseException.getHeaders()` ni info de trazabilidad.

**Ejemplo concreto de inconsistencia:**

Si Django responde `400 {"detail": "Email ya registrado"}`, el gateway responde:

```json
{
  "timestamp": "2026-06-29T...",
  "status": 400,
  "error": "Bad Request",
  "message": "{\"detail\": \"Email ya registrado\"}",   // ⚠️ JSON dentro de string
  "path": "/api/auth/register"
}
```

El móvil recibe un JSON dentro de un string. Tiene que parsear dos veces.

**Solución correcta:**

```java
@ExceptionHandler(WebClientResponseException.class)
public ResponseEntity<ErrorResponseDTO> handleWebClientException(...) {
    // Log para debugging
    log.warn("Django returned {} for {}: {}", 
        ex.getStatusCode(), request.getRequestURI(), ex.getResponseBodyAsString());
    
    // Mapear a mensaje en español
    String safeMessage = switch (ex.getStatusCode().value()) {
        case 400 -> "Solicitud inválida";
        case 401 -> "No autorizado";
        case 403 -> "Acceso denegado";
        case 404 -> "Recurso no encontrado";
        case 502, 503, 504 -> "Servicio no disponible";
        default -> "Error al procesar la solicitud";
    };
    
    return ResponseEntity.status(ex.getStatusCode()).body(
        new ErrorResponseDTO(
            LocalDateTime.now().toString(),
            ex.getStatusCode().value(),
            ex.getStatusText(),
            safeMessage,    // ✅ mensaje en español
            request.getRequestURI()
        )
    );
}
```

### 1.2. Handler de `MethodArgumentNotValidException` (Bean Validation falló)

```java
@ExceptionHandler(MethodArgumentNotValidException.class)
public ResponseEntity<ErrorResponseDTO> handleValidation(
        MethodArgumentNotValidException ex, HttpServletRequest request) {
    String message = ex.getBindingResult()
        .getFieldErrors()
        .stream()
        .findFirst()  // ⚠️ solo el primer error
        .map(error -> error.getField() + ": " + error.getDefaultMessage())
        .orElse("Datos inválidos");

    return ResponseEntity.badRequest().body(
        new ErrorResponseDTO(
            LocalDateTime.now().toString(),
            400,
            "Bad Request",
            message,
            request.getRequestURI()
        )
    );
}
```

**Debilidades:**

- ⚠️ `.findFirst()` **solo retorna el primer error**. Si el cliente envía 3 campos inválidos, recibe 1 mensaje y tiene que adivinar los otros 2.
- El formato `"campo: mensaje"` se mete en `message` (string), no se desglosa en `fieldErrors` (mapa). El cliente no puede iterar programáticamente.

**Comparación con el Lab 5 (Fase 4):**

```java
// Forma canónica del Lab 5
public ResponseEntity<?> manejarValidaciones(MethodArgumentNotValidException ex) {
    Map<String, String> errores = new HashMap<>();
    ex.getBindingResult().getFieldErrors()
        .forEach(error -> errores.put(error.getField(), error.getDefaultMessage()));
    return ResponseEntity.badRequest().body(errores);
}
```

El gateway debería:

1. **Capturar TODOS los errores**, no solo el primero.
2. **Devolver `fieldErrors: Map<String, String>`** en el `ErrorResponseDTO`.
3. **Permitir que el cliente renderice los errores** campo por campo.

**Solución correcta:**

```java
// 1. Extender ErrorResponseDTO con fieldErrors opcional
public record ErrorResponseDTO(
    String timestamp,
    int status,
    String error,
    String message,
    String path,
    Map<String, String> fieldErrors  // ← nuevo, opcional
) {}

// 2. Handler que captura todos
@ExceptionHandler(MethodArgumentNotValidException.class)
public ResponseEntity<ErrorResponseDTO> handleValidation(...) {
    Map<String, String> fieldErrors = new HashMap<>();
    ex.getBindingResult().getFieldErrors()
        .forEach(e -> fieldErrors.put(e.getField(), e.getDefaultMessage()));
    
    String firstMessage = fieldErrors.values().stream().findFirst()
        .orElse("Datos inválidos");
    
    return ResponseEntity.badRequest().body(
        new ErrorResponseDTO(
            LocalDateTime.now().toString(),
            400,
            "Bad Request",
            firstMessage,
            request.getRequestURI(),
            fieldErrors
        )
    );
}
```

### 1.3. Handler genérico de `Exception`

```java
@ExceptionHandler(Exception.class)
public ResponseEntity<ErrorResponseDTO> handleGeneralException(
        Exception ex, HttpServletRequest request) {
    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
        new ErrorResponseDTO(
            LocalDateTime.now().toString(),
            500,
            "Internal Server Error",
            "Error interno del gateway",   // ✅ no expone detalles
            request.getRequestURI()
        )
    );
}
```

**Fortaleza:**

- ✅ Mensaje genérico "Error interno del gateway" (no expone stacktrace al cliente).

**Debilidades:**

- ⚠️ **No loguea la excepción** en el servidor. Si llega un NullPointerException, el gateway responde 500 pero no hay rastro para debuggear. Debería ser:

```java
log.error("Unhandled exception at {}", request.getRequestURI(), ex);
```

## 2. Excepciones NO manejadas

`GlobalExceptionHandler` solo captura 3 tipos. Para una API de ~50 endpoints, faltan:

| Excepción | Status default | Cuándo ocurre |
|---|---|---|
| `HttpMessageNotReadableException` | 400 | JSON malformado en body |
| `MissingServletRequestParameterException` | 400 | Falta query param obligatorio |
| `MethodArgumentTypeMismatchException` | 400 | Tipo incorrecto en path variable (ej. `{id}/abc` cuando espera Long) |
| `HttpRequestMethodNotSupportedException` | 405 | Método no permitido (ej. PUT en endpoint que solo tiene GET) |
| `NoHandlerFoundException` | 404 | URL que no existe |
| `MaxUploadSizeExceededException` | 413 | Upload demasiado grande |
| `AccessDeniedException` | 403 | (no llegaría porque `permitAll`, pero defensivo) |

**Recomendación:** añadir al menos 4-5 handlers para cubrir los casos más comunes. Esto **demuestra el curso** (Lab 5) y da mejor DX al cliente.

## 3. Logging

### 3.1. Configuración (`application.yml`)

```yaml
logging:
  level:
    root: INFO
    com.comunidad.gateway: INFO
```

**Análisis:** configuración mínima. Solo nivel INFO. No hay:
- Appender personalizado (logs en JSON para producción).
- Correlation ID / trace ID.
- Logback config separado (`logback-spring.xml`).

### 3.2. Uso de logging en el código

| Clase | Nivel | Mensaje |
|---|---|---|
| `WebClientLoggingConfig.logRequest` | INFO | `"SPRING -> DJANGO {} {}"` (método + URL) |
| `WebClientLoggingConfig.logResponse` | INFO | `"DJANGO -> SPRING STATUS {}"` (status) |
| `GlobalExceptionHandler` | (ninguno) | ⚠️ No loguea nada |

**Hallazgo crítico:** `GlobalExceptionHandler` **NO loguea** las excepciones. Si Django falla y devuelve 500, el gateway responde 500 al móvil pero **no queda rastro en los logs del gateway**. Imposible debuggear.

**Análisis de los logs del WebClient:**

```java
@Bean
public ExchangeFilterFunction logRequest() {
    return ExchangeFilterFunction.ofRequestProcessor(request -> {
        log.info("SPRING -> DJANGO {} {}", request.method(), request.url());
        return Mono.just(request);
    });
}

@Bean
public ExchangeFilterFunction logResponse() {
    return ExchangeFilterFunction.ofResponseProcessor(response -> {
        log.info("DJANGO -> SPRING STATUS {}", response.statusCode());
        return Mono.just(response);
    });
}
```

**Fortalezas:**

- ✅ Loguea cada request/response (útil para trazabilidad).
- ✅ Indica origen (SPRING/DJANGO) y dirección.

**Debilidades:**

- ⚠️ **No loguea el body** (ni request ni response). Para debuggear requests con payload, hay que añadir un debugger.
- ⚠️ **No loguea headers** (no se ve el `Authorization` completo, pero sí podría verse el `Content-Type`).
- ⚠️ **Nivel INFO siempre** — para producción debería ser DEBUG con `logback-spring.xml`.

### 3.3. `Slf4j` vs `System.out`

```java
@Slf4j
@Configuration
public class WebClientLoggingConfig { ... }
```

✅ Usa `@Slf4j` de Lombok. Bien. No hay `System.out.println` en el código (verificado con grep mental).

## 4. Observabilidad

### 4.1. Spring Boot Actuator

Expuesto en `application.yml`:

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: always   # ⚠️ expone detalles sin auth
```

**Endpoints disponibles:**

- `GET /actuator/health` — estado de la app y sus componentes.
- `GET /actuator/info` — info de la app.
- `GET /actuator/metrics` — métricas JVM (memoria, threads, GC, etc.).

**Hallazgo:** `show-details: always` es riesgoso en producción. Debería ser `when_authorized` o `never`. Detalles como `diskSpace` y `db` no deberían ser públicos.

### 4.2. Métricas personalizadas

**No hay.** El gateway no usa `io.micrometer:micrometer-core` ni expone contadores de "requests por endpoint", "errores por tipo", etc.

**Recomendación:**

```java
@Service
public class EventosService {
    private final Counter requests;
    private final Counter errors;

    public EventosService(MeterRegistry registry) {
        this.requests = registry.counter("eventos.requests");
        this.errors = registry.counter("eventos.errors");
    }

    public PagedResponseDTO<List<EventoResponseDTO>> obtenerEventos(String auth) {
        requests.increment();
        try {
            return eventosClient.obtenerEventos(auth);
        } catch (Exception e) {
            errors.increment();
            throw e;
        }
    }
}
```

### 4.3. Distributed tracing

**No hay.** No hay `spring-cloud-starter-sleuth` ni OpenTelemetry. No hay `traceId` o `spanId` en los logs.

**Impacto:** si el móvil reporta "falló a las 14:32", no se puede seguir el flujo completo gateway → Django.

### 4.4. Health checks

| Endpoint | Qué chequea | Notas |
|---|---|---|
| `GET /actuator/health` | Spring context (auto) | Por defecto |
| `GET /api/health` | Nada (estático) | Retorna string fijo |
| `GET /api/django-test` | Que Django responda a `/api/v1/noticias/` | Proxy check, no health dedicado |

**Hallazgo:** no hay un health check que verifique la BD MySQL. `actuator/health` no lo expone porque no hay un `HealthIndicator` para DataSource. Se podría añadir:

```java
@Component
public class DjangoHealthIndicator implements HealthIndicator {
    @Override
    public Health health() {
        try {
            String response = djangoHealthClient.probarConexion();
            return Health.up().withDetail("django", "reachable").build();
        } catch (Exception e) {
            return Health.down().withException(e).build();
        }
    }
}
```

## 5. Resumen de manejo de errores y observabilidad

| Aspecto | Estado | Severidad |
|---|---|---|
| `@RestControllerAdvice` | ✅ Implementado | — |
| `ErrorResponseDTO` canónico | ✅ Implementado | — |
| Captura errores de WebClient | ✅ Sí | — |
| Captura errores de validación | ✅ Sí | — |
| Captura excepciones genéricas | ✅ Sí | — |
| Captura TODOS los errores de validación | ❌ Solo el primero | Media |
| Mapeo seguro de errores de Django | ❌ Repite body crudo | Media |
| Logging de excepciones | ❌ **No loguea** | **Alta** |
| Manejo de excepciones HTTP adicionales (405, 413) | ❌ No | Baja |
| Métricas por endpoint | ❌ No | Media |
| Distributed tracing | ❌ No | Media |
| Health check de BD | ❌ No | Baja |
| Health check de Django | ✅ Parcial (`/api/django-test`) | — |
| `show-details: always` en actuator | ❌ Riesgoso | Media |
| JSON logs para producción | ❌ No | Baja |
| Correlación de logs (request ID) | ❌ No | Media |

**Puntuación global:** 4/14 puntos (28%). Faltan muchos elementos que el curso y las buenas prácticas empresariales recomiendan.

## 6. Recomendaciones

### 6.1. Corto plazo (refactor sin cambiar arquitectura)

1. **Loguear las excepciones** en `GlobalExceptionHandler` (con `log.error(..., ex)`).
2. **Mapear errores de Django a mensajes en español** (no repetir el body crudo).
3. **Capturar TODOS los errores de validación** (no solo el primero).
4. **Cambiar `show-details: always` a `when_authorized`**.
5. **Añadir handlers** para `HttpMessageNotReadableException`, `MethodArgumentTypeMismatchException`, etc.

### 6.2. Mediano plazo (mejoras operacionales)

1. **Migrar a JSON logs** con `logstash-logback-encoder`.
2. **Añadir `spring-boot-starter-actuator` con `micrometer-registry-prometheus`**.
3. **Métricas por endpoint** (`Timer`, `Counter`).
4. **Distributed tracing** con `micrometer-tracing-bridge-otel` + exportador.

### 6.3. Lo que NO se debe hacer

- No añadir `log.info(ex.getMessage())` en producción (puede exponer datos sensibles).
- No añadir `logging.level.org.springframework.web: DEBUG` en producción (ruido).
- No usar `System.out.println` (ya no se usa, bien).

Ver `08_auditoria_hallazgos.md` (H-04, H-12) y `09_propuestas_y_plan.md` para el plan.
